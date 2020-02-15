import logging
from operator import methodcaller
from typing import Iterable

from django.db import transaction
from django.http import Http404
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.models import Category, NameConflictError
from categories.tree import depth_first_create_category
from categories.validators import Validator, UniqueCategoriesNameInRequest, UniqueCategoriesNameInDB

logger = logging.getLogger(__file__)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class CategoriesTreeSerializer(serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()
    children = CategorySerializer(many=True, source='get_children')
    siblings = CategorySerializer(many=True, source='get_siblings')

    # I'm not sure about all of this.
    # You cannot drop the transaction,
    # if something happens during the process
    # you should rollback all changes no matter
    # temporary error was or not.
    # That's lead us to all Validators below are redundant.
    # The benefits from them are ghostly, but
    # problems are obvious:
    # - More code for test and maintain
    # - Same logic splitted on two difference palaces
    # - If count of valid requests exceeds the number of non-valid
    #   it is added additional load because of redundant.
    # - Need to add index on `name` field which will increase mem consumption by BD
    default_validators: Validator = [
        UniqueCategoriesNameInRequest,
        UniqueCategoriesNameInDB,
    ]

    class Meta:
        model = Category
        fields = ('id', 'name', 'parents', 'children', 'siblings')

    @staticmethod
    def get_parents(obj):
        if obj.parent:
            return [CategorySerializer(obj.parent).data]
        return []

    def create_categories(self) -> Iterable[Category]:
        data = self.initial_data
        self.validate(data)

        with transaction.atomic():
            return tuple(self._create_categories(data))

    def validate(self, attrs: dict):
        if not self.validators:
            return

        for v in self.validators:
            v.validate(attrs)

    @staticmethod
    def _create_categories(categories_tree: dict) -> Iterable[Category]:
        categories = depth_first_create_category(categories_tree)
        categories = map(methodcaller('save'), categories)
        return categories


class CategoryTree(APIView):

    @staticmethod
    def _get_requested_category(pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, pk, **__):
        category = self._get_requested_category(pk)
        serializer = CategoriesTreeSerializer(category)
        return Response(serializer.data)


class _CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class CategoriesList(APIView):

    def get(self, request, **__):
        """
        This method does not carry any functional
        and is only needed for hand-testing.

        Actually it should be dropped in prod or hided behind Auth
        """
        serializer = _CategorySerializer(Category.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request, **__):
        """
        Received a tree of a categories with format

        Category:
            {
                name: Str,
                children :[Category]
            }
        """
        # here we could use some exited lib,
        # but the conditions of the task require
        # that we do not do this
        try:
            created = CategoriesTreeSerializer(data=request.data).create_categories()
        except NameConflictError as e:
            logger.exception(str(e))
            return Response(e.json(), status=status.HTTP_400_BAD_REQUEST)

        return Response({"created": len(created)}, status=status.HTTP_201_CREATED)
