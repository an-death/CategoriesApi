from functools import partial
from typing import Iterable

from categories.models import Category


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

