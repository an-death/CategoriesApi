from functools import partial
from operator import methodcaller
from typing import Iterable

from django.db import transaction, IntegrityError
from django.http import Http404
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.models import Category, NameConflictError


class CategoryTreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class CategoriesTreeSerializer(serializers.ModelSerializer):
    parents = serializers.SerializerMethodField()
    children = CategoryTreeSerializer(many=True, source='get_children')
    siblings = CategoryTreeSerializer(many=True, source='get_siblings')

    class Meta:
        model = Category
        fields = ('id', 'name', 'parents', 'children', 'siblings')

    def get_parents(self, obj):
        if obj.parent:
            return [CategoryTreeSerializer(obj.parent).data]
        return []


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


class CategoryDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class CategoriesList(APIView):
    def get(self, request, **__):
        serializer = CategoryDescSerializer(Category.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request, **__):
        """
        received a tree of a categories with format
        Category:
            { name: Str, children :[Category]}
        """
        # here we could use some exited lib,
        # but the conditions of the task require
        # that we do not do this

        try:
            with transaction.atomic():
                created = len(self._create_categories(request.data))
        except NameConflictError as e:
            return Response(e.json(), status=status.HTTP_400_BAD_REQUEST)

        return Response({"created": created}, status=status.HTTP_201_CREATED)

    @staticmethod
    def _create_categories(categories_tree: dict) -> Iterable[Category]:
        categories = depth_first_create_category(categories_tree)
        categories = map(methodcaller('save'), categories)
        return tuple(categories)


def depth_first_create_category(tree, parent=None) -> Iterable[Category]:
    cat = Category(name=tree['name'], parent=parent)

    if 'children' in tree:
        create_child = partial(depth_first_create_category, parent=cat)
        children = map(create_child, tree['children'])
    else:
        children = ()

    yield cat
    for c in children:
        yield from c
