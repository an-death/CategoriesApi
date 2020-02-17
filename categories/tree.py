from functools import partial
from typing import Iterable, Callable, Type

Data = Type['A']
Node = Type['B']
NodeBuilder = Callable[[Data, Node], Node]
ChildGetter = Callable[[Data], Iterable[Data]]


def traverse_depth_first(node_builder: NodeBuilder,
                         child_getter: ChildGetter,
                         data: Data,
                         parent=None) -> Iterable[Node]:
    root = node_builder(data, parent)

    create_child = partial(traverse_depth_first, node_builder, child_getter, parent=root)
    children = map(create_child, child_getter(data))

    yield root
    for c in children:
        yield from c
