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
            and orig_node.formula == copy_node.formula

        if orig_node == n3:
            assert len(orig_node.assump_children) == 1
        assert len(orig_node.assump_children) == len(copy_node.assump_children)
        for orig_assump, copy_assump in zip(orig_node.assump_children, copy_node.assump_children):
            print('    assump:', orig_assump)
            assert orig_assump != copy_assump\
                and orig_assump.formula == copy_assump.formula

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

    assert set(tree.leaf_nodes) == {n3}

    tree_traversed_nodes = list(tree.depth_first_traverse())
    assert list(tree_traversed_nodes) == [n0, n2, n3, n4]


# def test_find_must_consistent_node_sets():
#     """
#     n0 ->
#     n1 -> n2 ->
#           n3 -> n4
#     n0 --
# 
#     where '->' means parent and '--' means assump_parent.
#     """
# 
#     n0, n1, n2, n3, n4, *_ = _prepare_nodes()
# 
#     n0.set_parent(n2)
#     n1.set_parent(n2)
#     n2.set_parent(n4)
#     n3.set_parent(n4)
#     n3.add_assump_child(n0)
#     tree = ProofTree(nodes=[n0, n1, n2, n3, n4])
# 
#     assert find_must_consistent_node_sets(tree.root_node) == [{n0, n1, n3}]
# 
#     """
#     n0 ->
#     n1 -> n2 -> n3 ->
# 
#     n5 -> n7
#     n6
#                    ->  n4 (arg=negation_elim)
#     """
# 
#     n0, n1, n2, n3, n4, n5, n6, n7, *_ = _prepare_nodes()
# 
#     n0.set_parent(n2)
#     n1.set_parent(n2)
#     n2.set_parent(n3)
#     n3.set_parent(n4)
# 
#     n5.set_parent(n7)
#     n6.set_parent(n7)
#     n7.set_parent(n4)
# 
#     n4.argument = Argument(None, None, None, id='negation_elim...')
#     tree = ProofTree(nodes=[n0, n1, n2, n3, n4, n5, n6, n7])
# 
#     find_must_consistent_node_sets(tree.root_node)
#     assert find_must_consistent_node_sets(tree.root_node) == [{n0, n1}, {n5, n6}]
# 
#     """
#     n0 ->
#     n1 -> n2 -> n3 ->
# 
#     n5 -> n7
#     n6
#                    ->  n4 (arg=negation_elim)
#     n8 -> n10
#     n9
#                                               -> n11
#     """
# 
#     n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, *_ = _prepare_nodes()
# 
#     n0.set_parent(n2)
#     n1.set_parent(n2)
#     n2.set_parent(n3)
#     n3.set_parent(n4)
# 
#     n5.set_parent(n7)
#     n6.set_parent(n7)
#     n7.set_parent(n4)
# 
#     n8.set_parent(n10)
#     n9.set_parent(n10)
# 
#     n4.set_parent(n11)
#     n10.set_parent(n11)
# 
#     n4.argument = Argument(None, None, None, id='negation_elim...')
#     tree = ProofTree(nodes=[n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11])
# 
#     assert find_must_consistent_node_sets(tree.root_node) == [
#         {n0, n1, n8, n9},
#         {n5, n6, n8, n9}
#     ]
# 
#     """
#     n0 ->
#     n1 -> n2 -> n3 ->
# 
#     n5 -> n7
#     n6
#                    ->  n4 (arg=negation_elim)
#     n8 -> n10
#     n9
#                                               -> n11 (arg=negation_elim)
#     """
# 
#     n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, *_ = _prepare_nodes()
# 
#     n0.set_parent(n2)
#     n1.set_parent(n2)
#     n2.set_parent(n3)
#     n3.set_parent(n4)
# 
#     n5.set_parent(n7)
#     n6.set_parent(n7)
#     n7.set_parent(n4)
# 
#     n8.set_parent(n10)
#     n9.set_parent(n10)
# 
#     n4.set_parent(n11)
#     n10.set_parent(n11)
# 
#     n4.argument = Argument(None, None, None, id='negation_elim...')
#     n11.argument = Argument(None, None, None, id='negation_elim...')
#     tree = ProofTree(nodes=[n0, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11])
# 
#     assert find_must_consistent_node_sets(tree.root_node) == [
#         {n0, n1},
#         {n5, n6},
#         {n8, n9},
#     ]


if __name__ == '__main__':
    test_proof_tree()
    # test_find_must_consistent_node_sets()
