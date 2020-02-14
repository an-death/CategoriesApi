from operator import attrgetter

from django.test import TestCase

from categories.views import depth_first_create_category


class CategoryTreeTestCase(TestCase):

    def setUp(self):
        self.input_tree = {
            'name': 'first',
            'children': [
                {
                    'name': 'second',
                    'children': [
                        {
                            'name': 'third',
                        }
                    ],
                },
                {
                    'name': 'fourth',
                }
            ],
        }
        self.expected_output = (
            'first', 'second', 'third', 'fourth'
        )

    def test_depth_first_category_formatting(self):
        result = depth_first_create_category(self.input_tree)
        result = map(attrgetter('name'), result)
        self.assertEqual(self.expected_output, tuple(result))

