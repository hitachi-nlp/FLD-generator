from FLD_generator.proof import ProofNode, ProofTree
from FLD_generator.formula import Formula
from pprint import pprint


def test_proof_tree():
    """
    n0 ->
    n1 -> n2 ->
          n3 -> n4
    n0 --

    where '->' means parent and '--' means assump_parent.
    """

    n0 = ProofNode(Formula('n0'))
    n1 = ProofNode(Formula('n1'))
    n2 = ProofNode(Formula('n2'))
    n3 = ProofNode(Formula('n3'))
    n4 = ProofNode(Formula('n4'))

    n0.set_parent(n2)
    n1.set_parent(n2)
    n2.set_parent(n4)
    n3.set_parent(n4)
    n3.add_assump_child(n0)

    tree = ProofTree(nodes=[n0, n1, n2, n3, n4])

    assert set(tree.leaf_nodes) == {n0, n1, n3}

    tree_traversed_nodes = list(tree.depth_first_traverse())
    assert list(tree_traversed_nodes) == [n0, n1, n2, n3, n4]

    # -- test copy --
    copy_tree = tree.copy()
    copy_tree_traversed_nodes = list(copy_tree.depth_first_traverse())
    assert len(tree_traversed_nodes) == len(copy_tree_traversed_nodes)
    for orig_node, copy_node in zip(tree_traversed_nodes, copy_tree_traversed_nodes):
        print(orig_node)
        assert orig_node != copy_node\
            and orig_node.formula == copy_node.formula

        if orig_node == n3:
            assert len(orig_node.assump_children) == 1
        assert len(orig_node.assump_children) == len(copy_node.assump_children)
        for orig_assump, copy_assump in zip(orig_node.assump_children, copy_node.assump_children):
            print('    assump:', orig_assump)
            assert orig_assump != copy_assump\
                and orig_assump.formula == copy_assump.formula


if __name__ == '__main__':
    test_proof_tree()
