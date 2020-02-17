from django.test import TestCase

from categories.tree import traverse_depth_first


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
        child_getter = lambda tree: tree.get('children', ())
        node_builder = lambda tree, _: tree['name']
        result = traverse_depth_first(node_builder, child_getter, self.input_tree)

        self.assertEqual(self.expected_output, tuple(result))
