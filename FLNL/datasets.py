import random
from enum import Enum
from statistics import mean, stdev
from typing import Dict, List, Optional, Union, Iterable, Tuple, Any
import logging
import copy
from collections import defaultdict
from pprint import pprint

from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.formula import Formula
from FLNL.proof import ProofTree, ProofNode
from FLNL.utils import flatten_dict
from FLNL.translators import Translator
import kern_profiler

logger = logging.getLogger(__name__)


class ProofStance(Enum):
    PROOF = 'PROOF'
    DISPROOF = 'DISPROOF'
    UNKNOWN = 'UNKNOWN'


class WorldAssumption(Enum):
    CWA = 'CWA'
    OWA = 'OWA'


def _generate_random_sentence(translator: Translator):
    acceptable_formula_reps = translator.acceptable_formulas
    for formula_rep in random.sample(acceptable_formula_reps, len(acceptable_formula_reps)):
        nls, _ = translator.translate([Formula(formula_rep)])
        if nls[0][1] is not None:
            return nls[0][1]
    return 'Love Love LoveLive!'


def _make_instance_label(proof_stance: ProofStance, world_assump: WorldAssumption) -> Union[bool, str]:
    if world_assump == WorldAssumption.CWA:
        if proof_stance == ProofStance.PROOF:
            return True
        elif proof_stance == ProofStance.DISPROOF:
            return False
        elif proof_stance == ProofStance.UNKNOWN:
            return False
        else:
            raise ValueError()
    elif world_assump == WorldAssumption.OWA:
        if proof_stance == ProofStance.PROOF:
            return True
        elif proof_stance == ProofStance.DISPROOF:
            return False
        elif proof_stance == ProofStance.UNKNOWN:
            return 'Unknown'
        else:
            raise ValueError()
    else:
        raise ValueError()


class _DistractorNode:

    def __init__(self, distractor: Formula):
        self.formula = distractor

    @property
    def children(self):
        return []


Node = Union[ProofNode, _DistractorNode]


class NLProofSDataset:

    def __init__(self,
                 pipeline: ProofTreeGenerationPipeline,
                 proof_stances: List[str],
                 world_assump: str,
                 depth: int,
                 branch_extension_steps: int,
                 raise_if_translation_not_found=True):
        self.pipeline = pipeline

        self.proof_stances = [ProofStance(proof_stance) for proof_stance in proof_stances]
        self.world_assump = WorldAssumption(world_assump)

        self.depth = depth
        self.branch_extension_steps = branch_extension_steps
        self.raise_if_translation_not_found = raise_if_translation_not_found

    @profile
    def generate(self,
                 size: int,
                 conclude_hypothesis_from_subtree_roots_if_proof_is_unknown=True,
                 add_randome_sentence_if_context_is_null=True) -> Iterable[Tuple[Dict, ProofTree, Optional[List[Formula]], Dict[str, Any]]]:
        """ Generate dataset

        See discussions.md for the options.
        """

        def is_root(node: Node) -> bool:
            return isinstance(node, ProofNode) and node == proof_tree.root_node

        def is_leaf(node: Node) -> bool:
            return isinstance(node, ProofNode) and node in proof_tree.leaf_nodes

        def is_int(node: Node) -> bool:
            return isinstance(node, ProofNode) and (not is_root(node) and not is_leaf(node))

        def is_distractor(node: Node) -> bool:
            return isinstance(node, _DistractorNode)

        def _get_sent_from_node(node: Node) -> str:
            return node.formula.translation or node.formula.rep

        def _get_sent_from_formula(formula: Formula) -> str:
            return formula.translation or formula.rep

        sample_cum_stats = defaultdict(int)
        all_sample_stats = defaultdict(list)
        for i_sample in range(size):
            # generate a proof tree
            proof_tree, root_negation_formula, distractor_formulas, pipeline_stats = self.pipeline.run(
                self.depth,
                self.branch_extension_steps,
                raise_if_translation_not_found=self.raise_if_translation_not_found,
            )
            # print(f'============== i_sample: {i_sample} ================')
            # print(proof_tree.root_node.formula)
            # pprint(distractor_formulas)

            proof_stance = self.proof_stances[i_sample % len(self.proof_stances)]
            if proof_stance == ProofStance.PROOF:
                hypothesis = _get_sent_from_formula(proof_tree.root_node.formula)
                missing_leaf_nodes = []
            elif proof_stance == ProofStance.DISPROOF:
                hypothesis = _get_sent_from_formula(root_negation_formula)
                missing_leaf_nodes = []
            elif proof_stance == ProofStance.UNKNOWN:
                hypothesis = _get_sent_from_formula(proof_tree.root_node.formula)
                missing_leaf_nodes = random.sample(proof_tree.leaf_nodes,
                                                   max(1, int(len(proof_tree.leaf_nodes) * 0.2)))
            else:
                raise ValueError()

            # indentify nodes in proof
            nodes_in_proof: List[Node] = []
            missing_nodes = copy.copy(missing_leaf_nodes)
            for node in proof_tree.depth_first_traverse():
                if is_root(node):
                    if any((child in missing_nodes for child in node.children)):
                        missing_nodes.append(node)
                        continue
                elif is_leaf(node):
                    continue
                elif is_int(node):
                    if any((child in missing_nodes for child in node.children)):
                        missing_nodes.append(node)
                        continue
                elif is_distractor(node):
                    continue
                else:
                    raise Exception()
                nodes_in_proof.extend(node.children)
                nodes_in_proof.append(node)

            all_nodes: List[Node] = list(nodes_in_proof)\
                + [_DistractorNode(distractor) for distractor in distractor_formulas]
            if len(all_nodes) == 0:
                if add_randome_sentence_if_context_is_null:
                    random_sentence = _generate_random_sentence(self.pipeline.translator)
                    all_nodes = [_DistractorNode(Formula(random_sentence))]
                    logger.info('Adding a random sentence into context since context have no sentence. The randome sentence is: "%s"', random_sentence)
                else:
                    raise NotImplementedError('We must add something to context since null context will lead to error in NLProofS learning.')

            # build node ids
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

            i_int = 1
            for node in proof_tree.depth_first_traverse():
                if node not in all_nodes:
                    continue

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

            # make proof string
            proof_elems = []
            for node in proof_tree.depth_first_traverse():
                if node not in all_nodes:
                    continue

                if is_root(node):
                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + ' -> hypothesis'
                elif is_leaf(node):
                    continue
                elif is_int(node):
                    node_id = node2id[node]
                    child_ids = [node2id[child] for child in node.children]
                    proof_str = ' & '.join(child_ids) + f' -> {node_id}: {_get_sent_from_node(node)}'
                elif is_distractor(node):
                    continue
                else:
                    raise Exception()

                proof_elems.append(proof_str)

            if proof_stance == ProofStance.UNKNOWN and conclude_hypothesis_from_subtree_roots_if_proof_is_unknown:
                subtree_root_nodes: List[Node] = []
                for node in nodes_in_proof:
                    _is_root = True

                    for other_node in nodes_in_proof:
                        if other_node == node:
                            continue
                        descendants_of_other_node = list(proof_tree.depth_first_traverse(other_node))
                        if node in descendants_of_other_node:
                            _is_root = False
                            break

                    if _is_root:
                        subtree_root_nodes.append(node)

                # We do not consider leaf nodes.
                # Since ther are indistinguishable from distractors, the prover can not specify them.
                subtree_root_nodes_wo_leaf = [node for node in subtree_root_nodes if not is_leaf(node)]

                if len(subtree_root_nodes_wo_leaf) == 0:
                    # rare case but possible when all the subtrees are leaf
                    node_ids = ['sent1']
                else:
                    node_ids = [node2id[node] for node in subtree_root_nodes_wo_leaf]
                proof_elems.append(' & '.join(node_ids) + ' -> hypothesis')

            proof_str = '; '.join(proof_elems) + ';'
            proof_strs = [proof_str]  # only one proof in our dataset

            # make output json
            label = _make_instance_label(proof_stance, self.world_assump)
            dataset_json = {
                'hypothesis': hypothesis,
                'context': context,
                'proofs': proof_strs,

                'proof_stance': proof_stance.value,
                'answer': label,

                'original_tree_depth': proof_tree.depth,

                # I have no idea how to define depth from the root when proof is incomplete.
                'depth': None if proof_stance == ProofStance.UNKNOWN else proof_tree.depth,
            }

            # Update statistics
            sample_stats = flatten_dict(pipeline_stats)
            sample_stats[f'answer.{label}'] = 1
            sample_stats[f'proof_stance.{proof_stance.value}'] = 1
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
