from typing import List, Tuple, Optional, Iterable, Union
from .formula import Formula
from .argument import Argument
from .exception import FormalLogicExceptionBase
import logging

logger = logging.getLogger(__name__)


class MultipleParentError(FormalLogicExceptionBase):
    pass


class ProofNode:

    def __init__(self, formula: Formula):
        self.formula = formula
        self.argument: Optional[Argument] = None
        self.parent: Optional[ProofNode] = None
        self._children: List['ProofNode'] = []
        # self._tree: Optional['ProofTree'] = None

    def add_child(self, node: 'ProofNode') -> None:
        if node.parent is not None:
            raise MultipleParentError('Can\'t add child since it already has a parent.')

        node.parent = self
        if node not in self._children:
            self._children.append(node)

    def delete_child(self, node: 'ProofNode') -> None:
        for _node in self._children:
            if _node  == node:
                self._children.remove(node)
                break
        if len(self._children) == 0:
            self.argument = None

    @property
    def children(self):
        return self._children

    def __str__(self) -> str:
        return f'ProofNode({self.formula})'

    def __repr__(self) -> str:
        return str(self)


class ProofTree:

    def __init__(self, nodes: Optional[List[ProofNode]] = None):
        self._nodes: List[ProofNode] = nodes or []

    def add_node(self, node: ProofNode) -> None:
        if node not in self._nodes:
            self._nodes.append(node)
            # node._tree = self

    def delete_node(self, node: ProofNode) -> None:
        self._nodes.remove(node)
        # node._tree = None
        for _node in self._nodes:
            if _node.parent == node:
                _node.parent = None
            _node.delete_child(node)

    @property
    def nodes(self) -> List[ProofNode]:
        return self._nodes

    @property
    def leaf_nodes(self) -> List[ProofNode]:
        return [node for node in self._nodes
                if len(node.children) == 0]

    @property
    def root_node(self) -> Optional[ProofNode]:
        if len(self._nodes) == 0:
            return None

        nodes_wo_parent = [node for node in self._nodes
                           if node.parent is None]
        if len(nodes_wo_parent) == 0:
            return None
        elif len(nodes_wo_parent) == 1:
            return nodes_wo_parent[0]
        else:
            raise Exception()

    @property
    def depth(self) -> int:
        """ The depth of a binary tree is the total number of edges from the root node to the most distant leaf node.

        See https://www.baeldung.com/cs/binary-tree-height#definition.
        """

        return max([self.get_node_depth(leaf_node)
                    for leaf_node in self.leaf_nodes])

    def get_node_depth(self, node: ProofNode) -> int:
        """ The depth of a node in a binary tree is the total number of edges from the root node to the target node.

        See https://www.baeldung.com/cs/binary-tree-height#definition.
        """
        depth = 0
        cur_node = node
        while cur_node.parent is not None:
            cur_node = cur_node.parent
            depth += 1
        return depth

    def depth_first_traverse(self,
                             start_node: Optional[ProofNode] = None,
                             depth=0,
                             get_depth=False) -> Iterable[Union[ProofNode, Tuple[ProofNode, int]]]:
        if len(self._nodes) == 0:
            return None

        start_node = start_node or self.root_node
        for child_node in start_node.children:
            yield from self.depth_first_traverse(start_node=child_node, depth=depth + 1, get_depth=get_depth)
        yield (start_node, depth) if get_depth else start_node

    def __repr__(self):
        return 'ProofTree(...)'

    def __str__(self):
        return self.__repr__()

    @property
    def format_str(self):
        rep = ''
        # rep = 'ProofTree(\n'
        for node, depth in self.depth_first_traverse(get_depth=True):
            rep += ''.join([f'{_depth}    ' for _depth in range(0, 10)]) + '\n'
            rep += ''.join(['|    '] * 10) + '\n'
            rep += '|    ' * depth + f'|  {node.argument}\n'
            rep += '|    ' * depth + f'|{node}\n'
            rep += ''.join(['|    '] * 10) + '\n'
        # rep += '\n)'
        return rep
