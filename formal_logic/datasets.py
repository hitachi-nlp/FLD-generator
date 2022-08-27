import random
from statistics import mean
from typing import Dict, List, Optional, Union, Iterable, Tuple, Any
import logging
import copy
from collections import defaultdict

from formal_logic.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from formal_logic.formula import Formula
from formal_logic.proof import ProofTree, ProofNode
from formal_logic.utils import flatten_dict

logger = logging.getLogger(__name__)


class _DistractorNode:

    def __init__(self, distractor: Formula):
        self.formula = distractor


class NLProofSDataset:

    def __init__(self,
                 pipeline: ProofTreeGenerationPipeline,
                 world_assump: str,
                 depth: int = 5,
                 raise_if_translation_not_found=True):
        self.pipeline = pipeline
        self.world_assump = world_assump
        self.depth = depth
        self.raise_if_translation_not_found = raise_if_translation_not_found

    def generate(self, size: int) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]], Dict[str, Any]]]:

        def is_root(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and node == proof_tree.root_node

        def is_leaf(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and node in proof_tree.leaf_nodes

        def is_int(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and (not is_root(node) and not is_leaf(node))

        def is_distractor(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, _DistractorNode)

        def _get_sent(node: Union[ProofNode, _DistractorNode]) -> str:
            return node.formula.translation or node.formula.rep

        stats = defaultdict(int)
        hypothesis_lengths = []
        context_lengths = []
        mean_proof_lengths = []

        for i_sample in range(size):
            proof_tree, distractor_formulas, pipeline_stats = self.pipeline.run(
                depth=self.depth,
                raise_if_translation_not_found=self.raise_if_translation_not_found,
            )

            stats['trees'] += 1
            for key, count in flatten_dict(pipeline_stats).items():
                stats[key] += count

            if self.world_assump == 'label_true_only':
                label = True
                unproven_leaf_nodes = []
            elif self.world_assump == 'CWA':
                if i_sample % 2 == 0:
                    label = True
                    unproven_leaf_nodes = []
                else:
                    label = False
                    unproven_leaf_nodes = random.sample(proof_tree.leaf_nodes,
                                                        max(1, int(len(proof_tree.leaf_nodes) * 0.2)))
            elif self.world_assump == 'OWA':
                raise NotImplementedError()
            else:
                raise ValueError()

            hypothesis = _get_sent(proof_tree.root_node)
            hypothesis_lengths.append(len(hypothesis.split(' ')))

            all_nodes: List[Union[ProofNode, _DistractorNode]] = list(proof_tree.nodes)\
                + [_DistractorNode(distractor) for distractor in distractor_formulas]

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
                f'{id_}: {_get_sent(node)}'
                for id_, node in id2node.items()
                if id_.startswith('sent') and node not in unproven_leaf_nodes
            ])
            context_lengths.append(len(context.split(' ')))

            proof_elems = []
            unproven_nodes = copy.copy(unproven_leaf_nodes)
            for node in proof_tree.depth_first_traverse():
                if is_root(node):
                    if any((child in unproven_nodes for child in node.children)):
                        unproven_nodes.append(node)
                        continue

                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + ' -> hypothesis'
                    proof_elems.append(proof_str)

                elif is_leaf(node):
                    continue

                elif is_int(node):
                    if any((child in unproven_nodes for child in node.children)):
                        unproven_nodes.append(node)
                        continue

                    node_id = node2id[node]
                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + f' -> {node_id}: {_get_sent(node)}'
                    proof_elems.append(proof_str)

                elif is_distractor(node):
                    continue

                else:
                    raise Exception()
            proof_str = '; '.join(proof_elems) + ';'
            proof_strs = [proof_str]  # only one proof in our dataset
            mean_proof_lengths.append(mean([len(proof_str.split(' ')) for proof_str in proof_strs]))

            dataset_json = {
                'hypothesis': hypothesis,
                'context': context,
                'proofs': proof_strs,
                'answer': label,
                'depth': proof_tree.depth,
            }

            stats.update({
                'length.hypothesis': mean(hypothesis_lengths),
                'length.context': mean(context_lengths),
                'length.proof': mean(mean_proof_lengths),
            })

            yield dataset_json, proof_tree, distractor_formulas, stats.copy()
