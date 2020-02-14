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
