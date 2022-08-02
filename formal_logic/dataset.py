import random
from typing import Dict, List, Optional, Union, Iterable, Tuple
import logging

from formal_logic.tree_pipeline import TreePipeline
from formal_logic.formula import Formula
from formal_logic.proof import ProofTree, ProofNode

logger = logging.getLogger(__name__)


class NLProofSDataset:

    def __init__(self,
                 tree_pipeline: TreePipeline,
                 world_assump: str,
                 depth: int = 5,
                 num_distractors: int = 5):
        self.tree_pipeline = tree_pipeline
        self.world_assump = world_assump
        self.depth = depth
        self.num_distractors = num_distractors

    def generate(self, size: int) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]]]]:
        class DistractorNode:

            def __init__(self, distractor: Formula):
                self.formula = distractor

        def get_str(node: Union[ProofNode, DistractorNode]) -> str:
            return node.formula.translation or node.formula.rep

        for i_sample in range(size):
            proof_tree, distractors = self.tree_pipeline.run(depth=self.depth, num_distractors=self.num_distractors)
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

            dataset_json =  {
                'hypothesis': hypothesis,
                'context': context,
                'proofs': [proof_str],
                'answer': True,
                'depth': proof_tree.depth,
            }

            yield dataset_json, proof_tree, distractors
