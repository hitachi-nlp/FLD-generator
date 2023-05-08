from FLD.proof import ProofNode, ProofTree
from FLD.formula import Formula
from pprint import pprint


def test_tree_copy():
    """
    n_assump -> n0 -> n2 -> n4
                n1 ->
                      n3 ->
    """

    n_assump = ProofNode(Formula('n_assump'))
    n0 = ProofNode(Formula('n0'))
    n1 = ProofNode(Formula('n1'))
    n2 = ProofNode(Formula('n2'))
    n3 = ProofNode(Formula('n3'))
    n4 = ProofNode(Formula('n4'))

    n_assump.set_assump_parent(n0)
    n0.set_parent(n2)
    n1.set_parent(n2)
    n2.set_parent(n4)
    n3.set_parent(n4)

    orig_tree = ProofTree(nodes=[n0, n1, n2, n3, n4, n_assump])
    copy_tree = orig_tree.copy()

    orig_tree_traversed_nodes = list(orig_tree.depth_first_traverse())
    copy_tree_traversed_nodes = list(copy_tree.depth_first_traverse())

    assert len(orig_tree_traversed_nodes) == len(copy_tree_traversed_nodes)
    for orig_node, copy_node in zip(orig_tree_traversed_nodes, copy_tree_traversed_nodes):
        print(orig_node)
        assert orig_node != copy_node\
            and orig_node.formula == copy_node.formula

        if orig_node == n0:
            assert len(orig_node.assump_children) == 1
        assert len(orig_node.assump_children) == len(copy_node.assump_children)
        for orig_assump, copy_assump in zip(orig_node.assump_children, copy_node.assump_children):
            print('    assump:', orig_assump)
            assert orig_assump != copy_assump\
                and orig_assump.formula == copy_assump.formula


if __name__ == '__main__':
    test_tree_copy()