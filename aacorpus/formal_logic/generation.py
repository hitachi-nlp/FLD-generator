import random
from typing import List, Tuple, Optional, Iterable, Union
from aacorpus.formal_logic.formula import PREDICATE_POOL, CONSTANT_POOL
from aacorpus.formal_logic import (
    generate_replacement_mappings,
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    generate_replaced_formulas,
    generate_replaced_arguments,
    Formula,
    Argument,
    replace_formula,
    replace_argument,
    is_satisfiable as is_formulas_satisfiable,
)
from .proof import ProofTree, ProofNode
from aacorpus.exception import AACorpusExceptionBase
import logging

logger = logging.getLogger(__name__)

_NG_FORMULAS = [
    Formula('(x): Fx -> Fx'),
    Formula('(Ex): Fx -> Fx'),
]


class MaxRetryExceedError(AACorpusExceptionBase):
    pass


def generate_tree(arguments: List[Argument], depth=1) -> Optional[ProofTree]:
    max_retry = 10
    try:
        proof_tree = _generate_stem(arguments, depth, PREDICATE_POOL, CONSTANT_POOL, max_retry=max_retry)
    except MaxRetryExceedError:
        logger.warning('_generate_stem() exception max retry (%d). Will return None.', max_retry)
        return None

    try:
        _extend_braches(proof_tree, arguments, depth, PREDICATE_POOL, CONSTANT_POOL, max_retry=max_retry)
    except MaxRetryExceedError:
        logger.warning('_extend_braches() exception max retry (%d). Will return None.', max_retry)
        return None

    return proof_tree


def _generate_stem(arguments: List[Argument],
                   depth: int,
                   predicate_pool: List[str],
                   constant_pool: List[str],
                   max_retry=10) -> Optional[ProofTree]:

    def update(premise_nodes: List[ProofNode],
               conclusion_node: ProofNode,
               argument: Argument,
               proof_tree: ProofTree):
        for premise_node in premise_nodes:
            conclusion_node.add_child(premise_node)
        conclusion_node.argument = argument
        for node in premise_nodes + [conclusion_node]:
            proof_tree.add_node(node)

    proof_tree = ProofTree()
    cur_arg = random.choice(arguments)
    cur_conclusion_node = ProofNode(cur_arg.conclusion)
    cur_premise_nodes = [ProofNode(premise) for premise in cur_arg.premises]
    update(cur_premise_nodes, cur_conclusion_node, cur_arg, proof_tree)

    cur_depth = 1
    retry = 0
    while True:
        if retry >= max_retry:
            raise MaxRetryExceedError()
        retry += 1

        if cur_depth >= depth:
            break

        cur_conclusion = cur_conclusion_node.formula

        # Choose next argument
        chainable_args = [
            arg for arg in arguments
            if any([premise_replaced.rep == cur_conclusion.rep
                    for premise in arg.premises
                    for premise_replaced, _ in generate_replaced_formulas(premise, cur_conclusion)])
        ]
        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        # The outer loops are for speedup: first build mappings on small variabl set and then use it for filtering out the mappings on large variable set.
        is_proper_mapping = False
        for premise in random.sample(next_arg_unreplaced.premises, len(next_arg_unreplaced.premises)):
            for premise_mapping in generate_replacement_mappings_from_formula(
                [premise],
                [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                shuffle=True,
            ):
                premise_replaced = replace_formula(premise, premise_mapping)
                if premise_replaced.rep != cur_conclusion.rep:
                    continue

                for mapping in generate_replacement_mappings_from_formula(
                    next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion],
                    [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                    constraints=premise_mapping,
                    shuffle=True,
                ):

                    next_arg_replaced = replace_argument(next_arg_unreplaced, mapping)

                    if all([premise.rep != cur_conclusion.rep
                            for premise in next_arg_replaced.premises]):
                        continue

                    if _has_ng_premises(next_arg_replaced):
                        continue

                    if len(_get_premises_already_in_tree(next_arg_replaced, proof_tree)) >= 2:  # 1 for the chained promise:
                        continue

                    if not _is_satisfiable(next_arg_replaced, proof_tree):
                        continue

                    if not _new_formula_is_deduced(next_arg_replaced, proof_tree):
                        continue

                    is_proper_mapping = True
                    break
                if is_proper_mapping:
                    break
            if is_proper_mapping:
                break

        if not is_proper_mapping:
            logger.info('_generate_stem() retry since proper mapping could not be generated...')
            continue

        # Update tree
        next_conclusion_node = ProofNode(next_arg_replaced.conclusion)
        next_conclusion_node.argument = next_arg_replaced
        next_premise_nodes = [
            cur_conclusion_node if premise.rep == cur_conclusion.rep else ProofNode(premise)
            for premise in next_arg_replaced.premises
        ]
        update(next_premise_nodes, next_conclusion_node, next_arg_replaced, proof_tree)

        cur_arg = next_arg_replaced
        cur_conclusion_node = next_conclusion_node
        cur_premise_nodes = next_premise_nodes
        cur_depth += 1

    return proof_tree


def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    max_retry=10) -> None:
    cur_step = 0
    retry = 0
    while True:
        if retry >= max_retry:
            raise MaxRetryExceedError()
        retry += 1

        if cur_step >= steps:
            break

        leaves = proof_tree.leaf_nodes
        leaf_node = None
        for leaf_node in random.sample(leaves, len(leaves)):
            if proof_tree.get_node_depth(leaf_node) >= proof_tree.depth:
                continue
            break
        if leaf_node is None:
            break

        # Choose next argument
        chainable_args = [
            arg for arg in arguments
            if any([conclsion_replaced.rep == leaf_node.formula.rep
                    for conclsion_replaced, _ in generate_replaced_formulas(arg.conclusion, leaf_node.formula)])
        ]
        if len(chainable_args) == 0:
            continue
        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        # The following two nested loop is for speedup:
        # 1. First, we generate the small number of mappings by using small number of symbols. Then, we find appropriate sub-mappings
        # 2. Second, we generate full number of mappings, using the sub-mappings as filters.
        is_proper_mapping = False
        for conclusion_mapping in generate_replacement_mappings_from_formula([next_arg_unreplaced.conclusion],
                                                                             [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                                                                             shuffle=True):
            conclusion_replaced = replace_formula(next_arg_unreplaced.conclusion, conclusion_mapping)
            if conclusion_replaced.rep != leaf_node.formula.rep:
                continue

            for mapping in generate_replacement_mappings_from_formula(
                next_arg_unreplaced.all_formulas,
                [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                constraints=conclusion_mapping,
                shuffle=True,
            ):
                next_arg_replaced = replace_argument(next_arg_unreplaced, mapping)
                if next_arg_replaced.conclusion.rep != leaf_node.formula.rep:
                    raise Exception()

                if _has_ng_premises(next_arg_replaced):
                    continue

                if len(_get_premises_already_in_tree(next_arg_replaced, proof_tree)) >= 1:
                    continue

                if not _is_satisfiable(next_arg_replaced, proof_tree):
                    continue

                is_proper_mapping = True
                break

            if is_proper_mapping:
                break

        if not is_proper_mapping:
            logger.info('_extend_branches() retry since proper mapping could not be generated...')

        # Upate tree
        leaf_node.argument = next_arg_replaced
        next_premise_nodes = [ProofNode(premise)
                              for premise in next_arg_replaced.premises]
        for premise_node in next_premise_nodes:
            proof_tree.add_node(premise_node)
            leaf_node.add_child(premise_node)
        cur_step += 1


def _has_ng_premises(arg: Argument) -> bool:
    return any([
        ng_formula_replaced.rep == premise.rep
        for premise in arg.premises
        for ng_formula in _NG_FORMULAS
        for ng_formula_replaced, _ in generate_replaced_formulas(ng_formula, premise)
    ])


def _get_premises_already_in_tree(arg: Argument, proof_tree: ProofTree) -> List[Formula]:
    return [
        premise
        for existent_node in proof_tree.nodes
        for premise in arg.premises
        if premise.rep == existent_node.formula.rep
    ]


def _is_satisfiable(arg: Argument, proof_tree: ProofTree) -> bool:
    return is_formulas_satisfiable([node.formula for node in proof_tree.nodes]
                                   + arg.premises
                                   + [arg.conclusion])


def _new_formula_is_deduced(arg: Argument, proof_tree: ProofTree) -> bool:
    return all([
        arg.conclusion.rep != node.formula.rep
        for node in proof_tree.nodes
    ])
