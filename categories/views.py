from django.http import Http404, JsonResponse
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.models import Category


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
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
