from pprint import pprint
from typing import List

from FLD_generator.proof import ProofNode, ProofTree
from FLD_generator.argument import Argument
from FLD_generator.formula import Formula


def _prepare_nodes() -> List[ProofNode]:
    return [ProofNode(Formula(f'n{i}')) for i in range(0, 30)]


def test_proof_tree():
    """
    n0 ->
    n1 -> n2 ->
          n3 -> n4
    n0 --

    where '->' means parent and '--' means assump_parent.
    """

    n0, n1, n2, n3, n4, *_ = _prepare_nodes()

    n0.set_parent(n2)
    n1.set_parent(n2)
    n2.set_parent(n4)
    n3.set_parent(n4)
    n3.add_assump_child(n0)
    tree = ProofTree(nodes=[n0, n1, n2, n3, n4])

    assert set(tree.nodes) == {n0, n1, n2, n3, n4}

    assert set(tree.leaf_nodes) == {n1, n3}

    tree_traversed_nodes = list(tree.depth_first_traverse())
    assert list(tree_traversed_nodes) == [n0, n1, n2, n3, n4]

    # -- test copy --
    copy_tree = tree.copy()
    copy_tree_traversed_nodes = list(copy_tree.depth_first_traverse())
    assert len(tree_traversed_nodes) == len(copy_tree_traversed_nodes)
    for orig_node, copy_node in zip(tree_traversed_nodes, copy_tree_traversed_nodes):
        print(orig_node)
        assert orig_node != copy_node\
            and orig_node.formula.rep == copy_node.formula.rep

        if orig_node == n3:
            assert len(orig_node.assump_children) == 1
        assert len(orig_node.assump_children) == len(copy_node.assump_children)
        for orig_assump, copy_assump in zip(orig_node.assump_children, copy_node.assump_children):
            print('    assump:', orig_assump)
            assert orig_assump != copy_assump\
                and orig_assump.formula.rep == copy_assump.formula.rep

    """
    n0 -> n2 ->
          n3 -> n4
    n0 --

    where '->' means parent and '--' means assump_parent.
    """

    n0, _, n2, n3, n4, *_ = _prepare_nodes()

    n0.set_parent(n2)
    n2.set_parent(n4)
    n3.set_parent(n4)
    n3.add_assump_child(n0)
    tree = ProofTree(nodes=[n0, n2, n3, n4])

    assert set(tree.nodes) == {n0, n2, n3, n4}

    assert set(tree.leaf_nodes) == {n3}

    tree_traversed_nodes = list(tree.depth_first_traverse())
    assert list(tree_traversed_nodes) == [n0, n2, n3, n4]


if __name__ == '__main__':
    test_proof_tree()
