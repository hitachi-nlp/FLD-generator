import random
from enum import Enum
from statistics import mean, stdev
from typing import Dict, List, Optional, Union, Iterable, Tuple, Any
import logging
import copy
from collections import defaultdict

from formal_logic.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from formal_logic.formula import Formula
from formal_logic.proof import ProofTree, ProofNode
from formal_logic.utils import flatten_dict
import kern_profiler

logger = logging.getLogger(__name__)


class ProofType(Enum):
    PROOF = 'proof'
    DISPROOF = 'disproof'
    INCOMPLETE = 'incomplete'


class WorldAssumption(Enum):
    CWA = 'CWA'
    OWA = 'OWA'


def _make_instance_label(proof_type: ProofType, world_assump: WorldAssumption) -> Union[bool, str]:
    if world_assump == WorldAssumption.CWA:
        if proof_type == ProofType.PROOF:
            return True
        elif proof_type == ProofType.DISPROOF:
            return False
        elif proof_type == ProofType.INCOMPLETE:
            return False
        else:
            raise ValueError()
    elif world_assump == WorldAssumption.OWA:
        if proof_type == ProofType.PROOF:
            return True
        elif proof_type == ProofType.DISPROOF:
            return False
        elif proof_type == ProofType.INCOMPLETE:
            return 'Unknown'
        else:
            raise ValueError()
    else:
        raise ValueError()


class _DistractorNode:

    def __init__(self, distractor: Formula):
        self.formula = distractor


class NLProofSDataset:

    def __init__(self,
                 pipeline: ProofTreeGenerationPipeline,
                 proof_types: List[str],
                 world_assump: str,
                 depth: int,
                 max_leaf_extensions: int,
                 raise_if_translation_not_found=True):
        self.pipeline = pipeline

        self.proof_types = [ProofType(proof_type) for proof_type in proof_types]
        self.world_assump = WorldAssumption(world_assump)

        self.depth = depth
        self.max_leaf_extensions = max_leaf_extensions
        self.raise_if_translation_not_found = raise_if_translation_not_found

    @profile
    def generate(self, size: int) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]], Dict[str, Any]]]:

        def is_root(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and node == proof_tree.root_node

        def is_leaf(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and node in proof_tree.leaf_nodes

        def is_int(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, ProofNode) and (not is_root(node) and not is_leaf(node))

        def is_distractor(node: Union[ProofNode, _DistractorNode]) -> bool:
            return isinstance(node, _DistractorNode)

        def _get_sent_from_node(node: Union[ProofNode, _DistractorNode]) -> str:
            return node.formula.translation or node.formula.rep

        def _get_sent_from_formula(formula: Formula) -> str:
            return formula.translation or formula.rep

        sample_cum_stats = defaultdict(int)
        all_sample_stats = defaultdict(list)
        for i_sample in range(size):
            proof_tree, root_negation_formula, distractor_formulas, pipeline_stats = self.pipeline.run(
                self.depth,
                self.max_leaf_extensions,
                raise_if_translation_not_found=self.raise_if_translation_not_found,
            )


            proof_type = self.proof_types[i_sample % len(self.proof_types)]
            if proof_type == ProofType.PROOF:
                hypothesis = _get_sent_from_formula(proof_tree.root_node.formula)
                missing_leaf_nodes = []
            elif proof_type == ProofType.DISPROOF:
                hypothesis = _get_sent_from_formula(root_negation_formula)
                missing_leaf_nodes = []
            elif proof_type == ProofType.INCOMPLETE:
                hypothesis = _get_sent_from_formula(proof_tree.root_node.formula)
                missing_leaf_nodes = random.sample(proof_tree.leaf_nodes,
                                                   max(1, int(len(proof_tree.leaf_nodes) * 0.2)))
            else:
                raise ValueError()

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
                f'{id_}: {_get_sent_from_node(node)}'
                for id_, node in id2node.items()
                if id_.startswith('sent') and node not in missing_leaf_nodes
            ])

            proof_elems = []
            missing_nodes = copy.copy(missing_leaf_nodes)
            for node in proof_tree.depth_first_traverse():
                if is_root(node):
                    if any((child in missing_nodes for child in node.children)):
                        missing_nodes.append(node)
                        continue

                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + ' -> hypothesis'
                    proof_elems.append(proof_str)

                elif is_leaf(node):
                    continue

                elif is_int(node):
                    if any((child in missing_nodes for child in node.children)):
                        missing_nodes.append(node)
                        continue

                    node_id = node2id[node]
                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + f' -> {node_id}: {_get_sent_from_node(node)}'
                    proof_elems.append(proof_str)

                elif is_distractor(node):
                    continue

                else:
                    raise Exception()
            proof_str = '; '.join(proof_elems) + ';'
            proof_strs = [proof_str]  # only one proof in our dataset

            label = _make_instance_label(proof_type, self.world_assump)
            dataset_json = {
                'hypothesis': hypothesis,
                'context': context,
                'proofs': proof_strs,

                'proof_type': proof_type.value,
                'answer': label,

                'depth': proof_tree.depth,
            }

            # Update statistics
            sample_stats = flatten_dict(pipeline_stats)
            sample_stats[f'answer.{label}'] = 1
            sample_stats[f'proof_type.{proof_type.value}'] = 1
            sample_stats['word_count_hypothesis'] = len(hypothesis.split(' '))
            sample_stats['word_count_context'] = len(context.split(' '))
            sample_stats['word_count_proof'] = mean([len(proof_str.split(' ')) for proof_str in proof_strs])
            sample_stats['word_count_all'] = sample_stats['word_count_hypothesis'] + sample_stats['word_count_context'] + sample_stats['word_count_proof']
            sample_stats['tree'] = 1

            for name, count in sample_stats.items():
                sample_cum_stats[name] += count

            for name, count in sample_stats.items():
                if name.find('argument') >= 0 or name.find('translation') >= 0:
                    continue
                all_sample_stats[name].append(count)

            sample_avg_stats = {
                name: count / sample_cum_stats['tree']
                for name, count in sample_cum_stats.items()
                if name != 'tree'
            }

            sample_std_stats = {
                name: stdev(count_list) if len(count_list) >= 2 else None
                for name, count_list in all_sample_stats.items()
            }

            yield dataset_json,\
                proof_tree,\
                distractor_formulas,\
                flatten_dict({'cum': sample_cum_stats, 'avg': sample_avg_stats, 'std': sample_std_stats})
