import random
from typing import Dict, List, Optional, Union
import logging

from formal_logic.formula import Formula
from formal_logic.proof import ProofTree, ProofNode

logger = logging.getLogger(__name__)


def to_nlproof(proof_tree: ProofTree,
               distractors: Optional[List[Formula]]) -> Dict:
    """
    {
      "hypothesis": "harry is red",
      "context": "sent1: harry is kind sent2: charlie is white sent3: blue people are nice sent4: harry is blue sent5: if someone is red and rough then they are nice sent6: charlie is kind sent7: all white people are red sent8: if someone is white and blue then they are nice sent9: if someone is red then they are smart sent10: if someone is kind then they are red sent11: erin is rough sent12: harry is red sent13: bob is kind sent14: all rough people are red sent15: if someone is smart then they are blue sent16: bob is white sent17: if someone is nice then they are rough sent18: bob is nice sent19: erin is red",
      "proofs": [
        "sent3 & sent4 -> int1: harry is nice; sent17 & int1 -> int2: harry is rough; sent14 & int2 -> hypothesis;",
        "sent12 -> hypothesis;",
        "sent1 & sent10 -> hypothesis;"
      ],
      "answer": true,
      "depth": 0
    }
    """
    class DistractorNode:

        def __init__(self, distractor: Formula):
            self.formula = distractor

    def get_str(node: Union[ProofNode, DistractorNode]) -> str:
        return node.formula.translation or node.formula.rep

    hypothesis = get_str(proof_tree.root_node)

    all_nodes: List[Union[ProofNode, DistractorNode]] = list(proof_tree.nodes)\
        + [DistractorNode(distractor) for distractor in distractors]

    def is_root(node: Union[ProofNode, DistractorNode]) -> bool:
        return isinstance(node, ProofNode) and node == proof_tree.root_node

    def is_leaf(node: Union[ProofNode, DistractorNode]) -> bool:
        return isinstance(node, ProofNode) and node in proof_tree.leaf_nodes

    def is_int(node: Union[ProofNode, DistractorNode]) -> bool:
        return isinstance(node, ProofNode) and (not is_root(node) and not is_leaf(node))

    def is_distractor(node: Union[ProofNode, DistractorNode]) -> bool:
        return isinstance(node, DistractorNode)

    i_sent = 1
    node2id = {}
    id2node = {}
    for node in random.sample(all_nodes, len(all_nodes)):
        if is_root(node):
            id_ = 'hypothesis'
        elif is_leaf(node):
            id_ = f'sent{i_sent}'
            i_sent += 1
        elif is_int(node):
            continue
        elif is_distractor(node):
            id_ = f'sent{i_sent}'
            i_sent += 1
        else:
            raise Exception()
        node2id[node] = id_
        id2node[id_] = node

    # add int node with depth first order.
    i_int = 1
    for node in proof_tree.depth_first_traverse():
        if is_int(node):
            id_ = f'int{i_int}'
            i_int += 1
            node2id[node] = id_
            id2node[id_] = node

    context = ' '.join([
        f'{id_}: {get_str(node)}'
        for id_, node in id2node.items()
        if id_.startswith('sent')
    ])

    proof_strs = []
    for node in proof_tree.depth_first_traverse():
        if is_root(node):
            child_ids = [node2id[child] for child in node.children]
            proof_str = ' & '.join(child_ids) + ' -> hypothesis'
            proof_strs.append(proof_str)
        elif is_leaf(node):
            continue
        elif is_int(node):
            node_id = node2id[node]
            child_ids = [node2id[child] for child in node.children]
            proof_str = ' & '.join(child_ids) + f' -> {node_id}: {get_str(node)}'
            proof_strs.append(proof_str)
        elif is_distractor(node):
            continue
        else:
            raise Exception()
    proof_str = '; '.join(proof_strs)

    return {
        'hypothesis': hypothesis,
        'context': context,
        'proofs': [proof_str],
        'answer': True,
        'depth': proof_tree.depth,
    }
