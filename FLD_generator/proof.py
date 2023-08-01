from typing import List, Tuple, Optional, Iterable, Union, Dict, Set, Any
from collections import defaultdict
from copy import copy
import logging

from .formula import Formula
from .argument import Argument
from .exception import FormalLogicExceptionBase
from FLD_generator.utils import make_combination_from_iter

logger = logging.getLogger(__name__)


class MultipleParentError(FormalLogicExceptionBase):
    pass


class ProofNode:

    def __init__(self,
                 formula: Formula,
                 argument: Optional[Argument] = None,
                 tree: Optional['ProofTree'] = None):
        self.formula = formula
        self.argument: Optional[Argument] = argument

        self._parent: Optional[ProofNode] = None
        self._children: List['ProofNode'] = []

        self._assump_parent: Optional[ProofNode] = None
        self._assump_children: List['ProofNode'] = []

        self._tree = tree

    @property
    def parent(self):
        return self._parent

    def set_parent(self, node: 'ProofNode', force=False) -> None:
        node.add_child(self, force=force)

        self._share_tree(node)

    def _set_parent(self, node: 'ProofNode') -> None:
        self._parent = node

        self._share_tree(node)

    def delete_parent(self) -> None:
        if self._parent is not None:
            self._parent.delete_child(self)

        self.delete_tree()

    def _delete_parent(self) -> None:
        self._parent = None

        self.delete_tree()

    @property
    def ancestors(self) -> List['ProofNode']:
        if self.parent is None:
            return []
        else:
            return [self.parent] + self.parent.ancestors

    @property
    def children(self):
        return self._children

    def add_child(self, node: 'ProofNode', force=False) -> None:
        if not force and node.parent is not None:
            raise MultipleParentError('Can\'t add child since the child already has a parent.')

        if node not in self._children:
            self._children.append(node)
        node._set_parent(self)

        self._share_tree(node)

    def delete_child(self, node: 'ProofNode') -> None:
        for _node in self._children:
            if _node  == node:
                self._children.remove(_node)
                _node._delete_parent()
                break
        if len(self._children) == 0:
            self.argument = None

        node.delete_tree()

    @property
    def descendants(self) -> List['ProofNode']:
        descendants = copy(self.children)
        for child in self.children:
            descendants += child.descendants
        return descendants

    @property
    def assump_parent(self):
        return self._assump_parent

    def set_assump_parent(self, node: 'ProofNode', force=False) -> None:
        node.add_assump_child(self, force=force)

    def _set_assump_parent(self, node: 'ProofNode') -> None:
        self._assump_parent = node

    def delete_assump_parent(self) -> None:
        if self._assump_parent is not None:
            self._assump_parent.delete_assump_child(self)

    def _delete_assump_parent(self) -> None:
        self._assump_parent = None

    @property
    def assump_children(self):
        return self._assump_children

    def add_assump_child(self, node: 'ProofNode', force=False) -> None:
        if not force and node.assump_parent is not None:
            raise MultipleParentError('Can\'t add assump_child since the assump_child already has a assump_parent.')

        if node not in self._assump_children:
            self._assump_children.append(node)
        node._set_assump_parent(self)

    def delete_assump_child(self, node: 'ProofNode') -> None:
        for _node in self._assump_children:
            if _node  == node:
                self._assump_children.remove(_node)
                _node._delete_assump_parent()
                break
        if len(self._assump_children) == 0:
            self.argument = None

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0 and not self.is_assump

    @property
    def is_assump(self) -> bool:
        return self.assump_parent is not None

    @property
    def tree(self) -> Optional['ProofTree']:
        return self._tree

    def set_tree(self, tree: 'ProofTree') -> None:
        if self.tree is not None and tree != self.tree:
            raise ValueError('The node already has a tree.')
        self._tree = tree

    def delete_tree(self) -> None:
        self._tree = None

    def _share_tree(self, node: 'ProofNode') -> None:
        if node.tree is not None:
            self.set_tree(node.tree)
        elif self.tree is not None:
            node.set_tree(self.tree)

    def __str__(self) -> str:
        return f'ProofNode({self.formula}, is_assump={self.is_assump})'

    def __repr__(self) -> str:
        return str(self)


class ProofTree:

    def __init__(self, nodes: Optional[List[ProofNode]] = None):
        self._nodes: List[ProofNode] = nodes or []
        for node in self._nodes:
            node.set_tree(self)

    def add_node(self, node: ProofNode) -> None:
        if node not in self._nodes:
            self._nodes.append(node)
            node.set_tree(self)

    def delete_node(self, node: ProofNode) -> None:
        self._nodes.remove(node)

        for node_in_tree in self._nodes:
            if node.parent == node_in_tree:
                node.delete_parent()
            if node.assump_parent == node_in_tree:
                node.delete_assump_parent()
            node.delete_child(node_in_tree)
            node.delete_assump_child(node_in_tree)

        node.delete_tree()

    @property
    def nodes(self) -> List[ProofNode]:
        return self._nodes

    @property
    def leaf_nodes(self) -> List[ProofNode]:
        return [node for node in self._nodes
                if node.is_leaf]

    @property
    def assump_nodes(self) -> List[ProofNode]:
        return [node for node in self._nodes
                if node.is_assump]

    @property
    def root_node(self) -> Optional[ProofNode]:
        if len(self._nodes) == 0:
            return None

        nodes_wo_parent = [node for node in self._nodes
                           if node.parent is None and not node.is_assump]
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
        if len(self.leaf_nodes) == 0:
            return 0
        else:
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
                             depth=0) -> Iterable[ProofNode]:
        if len(self._nodes) == 0:
            return None

        start_node = start_node or self.root_node
        for child_node in start_node.children:
            yield from self.depth_first_traverse(start_node=child_node, depth=depth + 1)
        yield start_node

    @property
    def intermediate_constants(self) -> Iterable[Formula]:
        for node in self.nodes:
            if node.argument is None or node.argument.intermediate_constants is None:
                continue
            for constant in node.argument.intermediate_constants:
                yield constant

    def __repr__(self):
        return 'ProofTree(...)'

    def __str__(self):
        return self.__repr__()

    @property
    def format_str(self):
        rep = ''
        # rep = 'ProofTree(\n'
        for node in self.depth_first_traverse():
            depth = self.get_node_depth(node)
            rep += ''.join([f'{_depth}    ' for _depth in range(0, 10)]) + '\n'
            rep += ''.join(['|    '] * 10) + '\n'
            rep += '|    ' * depth + f'|  {node.argument}\n'
            rep += '|    ' * depth + f'|{node}\n'
            rep += ''.join(['|    '] * 10) + '\n'
        # rep += '\n)'
        return rep

    def copy(self, return_alignment=False) -> Union['ProofTree', Tuple['ProofTree', Dict['ProofNode', 'ProofNode']]]:
        nodes = self.nodes

        orig_nodes_to_orig_parents = {orig_node: orig_node.parent for orig_node in nodes}
        orig_nodes_to_orig_children = {orig_node: orig_node.children for orig_node in nodes}
        orig_nodes_to_orig_assump_parents = {orig_node: orig_node.assump_parent for orig_node in nodes}
        orig_nodes_to_orig_assump_children = {orig_node: orig_node.assump_children for orig_node in nodes}

        copy_nodes_to_orig_parents = {}
        copy_nodes_to_orig_children = defaultdict(set)
        copy_nodes_to_orig_assump_parents = {}
        copy_nodes_to_orig_assump_children = defaultdict(set)

        orig_nodes_to_copy_nodes = {}
        copy_nodes_to_orig_nodes = {}

        copy_nodes = []
        # for orig_node in nodes + assump_nodes:
        for orig_node in nodes:
            copy_node = ProofNode(orig_node.formula, argument=orig_node.argument)

            orig_nodes_to_copy_nodes[orig_node] = copy_node
            copy_nodes_to_orig_nodes[copy_node] = orig_node

            if orig_nodes_to_orig_parents.get(orig_node, None) is not None:
                orig_parent = orig_nodes_to_orig_parents[orig_node]
                copy_nodes_to_orig_parents[copy_node] = orig_parent

            if orig_nodes_to_orig_children.get(orig_node, None) is not None:
                orig_children = orig_nodes_to_orig_children[orig_node]
                for orig_child in orig_children:
                    copy_nodes_to_orig_children[copy_node].add(orig_child)

            if orig_nodes_to_orig_assump_parents.get(orig_node, None) is not None:
                orig_assump_parent = orig_nodes_to_orig_assump_parents[orig_node]
                copy_nodes_to_orig_assump_parents[copy_node] = orig_assump_parent

            if orig_nodes_to_orig_assump_children.get(orig_node, None) is not None:
                orig_assump_children = orig_nodes_to_orig_assump_children[orig_node]
                for orig_child in orig_assump_children:
                    copy_nodes_to_orig_assump_children[copy_node].add(orig_child)

            copy_nodes.append(copy_node)

        for copy_node in copy_nodes:

            if copy_node in copy_nodes_to_orig_parents:
                orig_parent = copy_nodes_to_orig_parents[copy_node]
                copy_parent = orig_nodes_to_copy_nodes[orig_parent]
                copy_node.set_parent(copy_parent, force=True)

            if copy_node in copy_nodes_to_orig_children:
                orig_children = copy_nodes_to_orig_children[copy_node]
                copy_children = [orig_nodes_to_copy_nodes[child] for child in orig_children]
                for copy_child in copy_children:
                    copy_node.add_child(copy_child, force=True)

            if copy_node in copy_nodes_to_orig_assump_parents:
                orig_assump_parent = copy_nodes_to_orig_assump_parents[copy_node]
                copy_assump_parent = orig_nodes_to_copy_nodes[orig_assump_parent]
                copy_node.set_assump_parent(copy_assump_parent, force=True)

            if copy_node in copy_nodes_to_orig_assump_children:
                orig_assump_children = copy_nodes_to_orig_assump_children[copy_node]
                copy_assump_children = [orig_nodes_to_copy_nodes[child] for child in orig_assump_children]
                for copy_child in copy_assump_children:
                    copy_node.add_assump_child(copy_child, force=True)

        if return_alignment:
            return ProofTree(nodes=copy_nodes), orig_nodes_to_copy_nodes
        else:
            return ProofTree(nodes=copy_nodes)
