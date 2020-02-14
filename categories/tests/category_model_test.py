from django.test import TestCase

from categories.models import Category, NameConflictError


class CategoryModelTestCase(TestCase):
    c1: Category
    c2: Category

    def setUp(self):
        self.c1 = Category.objects.create(name='test1')
        self.c2 = Category.objects.create(name='test2', parent=self.c1)

    def test_unique_name_field(self):
        badcat = Category(name='test1')
        self.assertRaises(NameConflictError, badcat.save)

    def test_get_parent(self):
        self.assertIsNone(self.c1.parent, msg='c1 has parent but must not')
        self.assertEqual(self.c2.parent.id, self.c1.id, msg='expect that c1 is parent for c2')

    def test_get_children(self):
        c2_children = tuple(self.c2.get_children())
        c1_children = tuple(self.c1.get_children())
        self.assertEqual(c2_children, (), msg='c2 has children but must not')
        self.assertEqual(c1_children, (self.c2,), msg='expect that c2 is child of c1')

    def test_get_siblings(self):
        c3 = Category(name='test3', parent=self.c1)
        c3.save()

        self.assertEqual(c3.get_siblings().first(), self.c2)
        self.assertEqual(self.c2.get_siblings().first(), c3)
