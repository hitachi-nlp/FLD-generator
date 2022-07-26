from typing import List, Tuple, Optional, Iterable, Union
from formal_logic import Formula, Argument
from formal_logic.exception import AACorpusExceptionBase
import logging

logger = logging.getLogger(__name__)


class MultipleParentError(AACorpusExceptionBase):
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
        return f'ProofNode({self.formula.rep})'

    def __repr__(self) -> str:
        return str(self)


class ProofTree:

    def __init__(self):
        self._nodes: List[ProofNode] = []

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
    def root_node(self) -> ProofNode:
        return [node for node in self._nodes
                if node.parent is None][0]

    @property
    def depth(self) -> int:
        return max([self.get_node_depth(leaf_node)
                    for leaf_node in self.leaf_nodes])

    def get_node_depth(self, node: ProofNode) -> int:
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
        rep = 'ProofTree(\n'
        for node, depth in self.depth_first_traverse(get_depth=True):
            rep += '\n'
            rep += '    ' + '    ' * depth + f'node     : {node}\n'
            rep += '    ' + '    ' * depth + f' argument : {node.argument}'
            rep += '\n'
        rep += '\n)'
        return rep
