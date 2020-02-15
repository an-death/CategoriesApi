from functools import partial
from typing import Iterable

from categories.models import Category


def depth_first_create_category(tree, parent=None) -> Iterable[Category]:
    cat = Category(name=tree['name'], parent=parent)

    create_child = partial(depth_first_create_category, parent=cat)
    children = map(create_child, tree.get('children', ()))

    yield cat
    for c in children:
        yield from c
