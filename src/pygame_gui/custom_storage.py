from dataclasses import KW_ONLY, dataclass, field

import pygame


@dataclass
class BlockObject:
    """
    Arguments:
        name:
        parent:

        KW_ONLY
        dimensions (tuple[float, float]):
        coordinates (tuple[float, float]):
        colour (str):
        priority (int):
        surface (None):

    """
    name: str
    parent: str

    _: KW_ONLY
    dimensions: tuple[float, float]
    coordinates: tuple[float, float]
    colour: str
    surface: pygame.Surface
    priority: int = 0

    children: list[str] = field(default_factory=list, init=False)


class MyList(dict):
    """
    A dictionary with some list-like properties for storing BlockObjects
    Can:
    - keep track of parents
    - iterate by DFS
    
    """

    def __init__(self, node_name, node):
        super().__init__()
        self[node_name] = BlockObject(
            name=node_name,
            parent=None,
            dimensions=None,
            coordinates=None,
            colour=None,
            surface=node)
        self.node_name = node_name
        self.queue = []

    def append(self,
               name: str,
               parent: str,
               dimensions: tuple[float, float],
               coordinates: tuple[float, float],
               colour: str,
               priority: int = 0):
        """

        Args:
            name:
            parent:
            dimensions:
            coordinates:
            colour:
            priority:
        """
        self[parent].children.append((name, priority))
        self[name] = BlockObject(
            name=name,
            parent=parent,
            dimensions=dimensions,
            coordinates=coordinates,
            colour=colour,
            priority=priority)

    def branch(self, node):
        """Returns the branch of the tree beginning at node.
        """
        self.queue = [(node, self[node].priority)]
        return (x for x in self)

    def section(self, node):
        """Deprecated for readability
        """
        return self.branch(node)

    def __delitem__(self, item):
        parent = self[item].parent
        priority = self[item].priority
        self[parent].children.remove((item, priority))
        super().__delitem__(item)
        # deleted_items = []
        # for node in self.branch(item):
        # print(node[0])
        # super().__delitem__(node[0])
        # deleted_items.append(node[0])
        # return deleted_items

    # def __iter__(self):
    # if self.queue == []:
    # self.queue.extend(self[self.node][2])
    # return self

    # def __next__(self):
    # """Iterates through as a depth first search.
    # """
    # if not self.queue:
    # raise StopIteration
    # else:
    # current_object = self.queue.pop(0)
    # try:
    # self.queue.extend(self[current_object][2])
    # except KeyError as err:
    # print(err)
    # [print(x) for x in self.items()]
    # print(self.queue)
    # raise KeyError
    # return current_object, self[current_object][0], self[current_object][1]

    def __iter__(self):
        """Iterates through as a depth first search.
        """
        if not self.queue:
            self.queue.extend(sorted(self[self.node_name].children, key=lambda x: x[1], reverse=True))

        while self.queue:
            current_object = self.queue.pop(0)[0]
            new_items = sorted(self[current_object].children, key=lambda x: x[1], reverse=True)
            self.queue.extend(new_items)
            yield current_object, self[current_object]
