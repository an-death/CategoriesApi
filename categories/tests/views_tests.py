import json
from contextlib import contextmanager

from rest_framework import status
from rest_framework.test import APITestCase

from categories.models import Category


class CategoriesGetTestCase(APITestCase):
    @contextmanager
    def _setup_children(self):
        c1 = Category.objects.create(name='test1')
        c2 = Category.objects.create(name='test2', parent=c1)
        yield c1, c2
        Category.objects.all().delete()

    def test_validate_response_children(self):
        with self._setup_children() as (c1, c2):
            response = self.client.get(f'/categories/{c1.id}/')
            expected_response_data = {
                'id': c1.id,
                'name': c1.name,
                'parents': [],
                'children': [
                    {
                        'id': c2.id,
                        'name': c2.name,
                    },
                ],
                'siblings': []
            }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response_data)

    def _setup_parent(self):
        return self._setup_children()

    def test_validate_response_parents(self):
        with self._setup_parent() as (c1, c2):
            response = self.client.get(f'/categories/{c2.id}/')
            expected_response_data = {
                'id': c2.id,
                'name': c2.name,
                'parents': [
                    {
                        'id': c1.id,
                        'name': c1.name,
                    },
                ],
                'children': [],
                'siblings': []
            }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response_data)

    @contextmanager
    def _setup_siblings(self):
        c1 = Category.objects.create(name='test1')
        c2 = Category.objects.create(name='test2', parent=c1)
        c3 = Category.objects.create(name='test3', parent=c1)
        yield c1, c2, c3
        Category.objects.all().delete()

    def test_validate_response_siblings(self):
        with self._setup_siblings() as (c1, c2, c3):
            response = self.client.get(f'/categories/{c2.id}/')
            expected_response_data = {
                'id': c2.id,
                'name': c2.name,
                'parents': [
                    {
                        'id': c1.id,
                        'name': c1.name,
                    },
                ],
                'children': [],
                'siblings': [
                    {
                        'id': c3.id,
                        'name': c3.name,
                    },
                ]
            }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response_data)


class CategoryTreePostTestCase(APITestCase):

    def setUp(self):
        Category.objects.all().delete()

    def test_create_category_tree(self):
        created_category_count = 4
        input_data = {
            'name': 'test1',
            'children': [
                {
                    'name': 'test1.1',
                    'children': [
                        {
                            'name': 'test1.1.1'
                        }
                    ]
                },
                {
                    'name': 'test1.2'
                }
            ]
        }
        data = json.dumps(input_data)
        resp = self.client.post('/categories/', data=data, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.json()['created'], created_category_count)

    def test_except_name_conflict_in_create(self):
        category_name = 'test1'
        Category(name=category_name).save()
        data = json.dumps({'name': category_name})
        resp = self.client.post('/categories/', data=data, content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(category_name in resp.json()['error'])
