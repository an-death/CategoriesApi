from operator import attrgetter

from django.test import TestCase

from categories.models import Category
from categories.views import CategorySerializer, CategoriesTreeSerializer


class CategorySerializerTestCase(TestCase):

    def tearDown(self):
        Category.objects.all().delete()

    def test_serialize(self):
        category = Category(name='test_serialize')
        expected = {'id': 1, 'name': 'test_serialize'}

        category.save()
        result = CategorySerializer(category).data

        self.assertEqual(expected, result)

    def test_deserialize(self):
        category_data = {
            'name': 'test_deserialize#1',
            'children': [
                {
                    'name': 'test_deserialize#2'
                }
            ]
        }
        expected = [
            (1, 'test_deserialize#1', None),
            (2, 'test_deserialize#2', 1)
        ]

        serializer = CategoriesTreeSerializer(data=category_data)
        cats = serializer.create_categories()

        result = list(map(attrgetter('id', 'name', 'parent_id'), cats))
        self.assertEqual(expected, result)
