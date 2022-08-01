import random
import logging
import re
from typing import List, Optional

from timeout_timer import timeout as timeout_context

from .formula import (
    PREDICATES,
    CONSTANTS,
    Formula,
    is_satisfiable as is_formulas_satisfiable,
)
from .argument import Argument
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replaced_formulas,
    replace_formula,
    replace_argument,
)
from .proof import ProofTree, ProofNode
from .exception import AACorpusExceptionBase

from .formula import (
    IMPLICATION,
    AND,
    OR,
    NOT,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
)
# import kern_profiler

logger = logging.getLogger(__name__)


_NG_FORMULA_REGEXPS = [
    f'({predicate}|{NOT}{predicate}) ({IMPLICATION}|{AND}|{OR}) ({predicate}|{NOT}{predicate})'
    for predicate in PREDICATES
] + [
    f'({predicate}{individual}|{NOT}{predicate}{individual}) ({IMPLICATION}|{AND}|{OR}) ({predicate}{individual}|{NOT}{predicate}{individual})'
    for predicate in PREDICATES
    for individual in CONSTANTS + VARIABLES

]

_NG_FORMULA_REGEXP = re.compile('|'.join(_NG_FORMULA_REGEXPS))


class MaxRetryExceedError(AACorpusExceptionBase):
    pass


# @profile
def generate_tree(arguments: List[Argument],
                  depth=1,
                  elim_dneg=False,
                  timeout: Optional[int] = None) -> Optional[ProofTree]:
    timeout = timeout or 99999999
    with timeout_context(timeout, exception=TimeoutError):

        max_retry = 10
        try:
            proof_tree = _generate_stem(arguments, depth, PREDICATES, CONSTANTS,
                                        elim_dneg=elim_dneg,
                                        max_retry=max_retry)
        except MaxRetryExceedError:
            logger.warning('_generate_stem() exception max retry (%d). Will return None.', max_retry)
            return None

        try:
            _extend_braches(proof_tree, arguments, depth, PREDICATES, CONSTANTS,
                            elim_dneg=elim_dneg,
                            max_retry=max_retry)
        except MaxRetryExceedError:
            logger.warning('_extend_braches() exception max retry (%d). Will return None.', max_retry)
            return None

    return proof_tree


# @profile
def _generate_stem(arguments: List[Argument],
                   depth: int,
                   predicate_pool: List[str],
                   constant_pool: List[str],
                   elim_dneg=False,
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
                    for premise_replaced, _ in generate_replaced_formulas(premise, cur_conclusion, elim_dneg=elim_dneg)])
        ]
        if len(chainable_args) == 0:
            logger.info('_generate_stem() retry since no chainable arguments found ...')
            continue

        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        # The outer loops are for speedup: first build mappings on small variabl set and then use it for filtering out the mappings on large variable set.
        is_proper_mapping = False
        for premise in random.sample(next_arg_unreplaced.premises, len(next_arg_unreplaced.premises)):
            for premise_mapping in generate_replacement_mappings_from_formula(
                [premise],
                # [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                [cur_conclusion],
                shuffle=True,
            ):
                premise_replaced = replace_formula(premise, premise_mapping, elim_dneg=elim_dneg)

                if premise_replaced.rep != cur_conclusion.rep:
                    continue

                if _has_ng_formulas([premise_replaced]):
                    continue

                if not _is_satisfiable([premise_replaced], proof_tree):
                    continue

                for mapping in generate_replacement_mappings_from_formula(
                    next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion],
                    [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                    constraints=premise_mapping,
                    shuffle=True,
                ):

                    next_arg_replaced = replace_argument(next_arg_unreplaced, mapping, elim_dneg=elim_dneg)

                    if _is_conclusion_in_premises(next_arg_replaced):
                        continue

                    if _has_ng_formulas(next_arg_replaced.premises):
                        continue

                    if not _is_formula_new(next_arg_replaced.conclusion, proof_tree):
                        continue

                    if len(_get_formulas_already_in_tree(next_arg_replaced.premises, proof_tree)) >= 2:  # 1 for the chained promise:
                        continue

                    if not _is_satisfiable(next_arg_replaced.all_formulas, proof_tree):
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

        # Update
        for i_premise, premise in enumerate(next_arg_replaced.premises):
            if premise.rep == cur_conclusion.rep:
                next_arg_replaced.premises[i_premise] = cur_conclusion  # refer to the unique object.
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


# @profile
def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    elim_dneg=False,
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
                    for conclsion_replaced, _ in generate_replaced_formulas(arg.conclusion, leaf_node.formula, elim_dneg=elim_dneg)])
        ]
        if len(chainable_args) == 0:
            logger.info('_extend_braches() retry since no chainable arguments found ...')
            continue
        next_arg_unreplaced = random.choice(chainable_args)

        # Choose mapping
        # The following two nested loop is for speedup:
        # 1. First, we generate the small number of mappings by using small number of symbols. Then, we find appropriate sub-mappings
        # 2. Second, we generate full number of mappings, using the sub-mappings as filters.
        is_proper_mapping = False
        for conclusion_mapping in generate_replacement_mappings_from_formula(
                [next_arg_unreplaced.conclusion],
                # [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                [leaf_node.formula],
                shuffle=True,
        ):

            conclusion_replaced = replace_formula(next_arg_unreplaced.conclusion, conclusion_mapping, elim_dneg=elim_dneg)

            if conclusion_replaced.rep != leaf_node.formula.rep:
                continue

            if _has_ng_formulas([conclusion_replaced]):
                continue

            if not _is_satisfiable([conclusion_replaced], proof_tree):
                continue

            for mapping in generate_replacement_mappings_from_formula(
                next_arg_unreplaced.all_formulas,
                [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                constraints=conclusion_mapping,
                shuffle=True,
            ):
                next_arg_replaced = replace_argument(next_arg_unreplaced, mapping, elim_dneg=elim_dneg)

                if _has_ng_formulas(next_arg_replaced.premises):
                    continue

                if len(_get_formulas_already_in_tree(next_arg_replaced.premises, proof_tree)) >= 1:
                    continue

                if not _is_satisfiable(next_arg_replaced.all_formulas, proof_tree):
                    continue

                is_proper_mapping = True
                break

            if is_proper_mapping:
                break

        if not is_proper_mapping:
            logger.info('_extend_branches() retry since proper mapping could not be generated...')
            continue

        # Upate tree
        next_arg_replaced.conclusion = leaf_node.formula  # refer to the sampe object
        leaf_node.argument = next_arg_replaced
        next_premise_nodes = [ProofNode(premise)
                              for premise in next_arg_replaced.premises]
        for premise_node in next_premise_nodes:
            proof_tree.add_node(premise_node)
            leaf_node.add_child(premise_node)
        cur_step += 1


def _is_conclusion_in_premises(arg: Argument) -> bool:
    return any([arg.conclusion.rep == premise.rep
                for premise in arg.premises])


def _has_ng_formulas(formulas: List[Formula]) -> bool:
    return any([
        _NG_FORMULA_REGEXP.search(formula.rep) is not None
        for formula in formulas
    ])


def _get_formulas_already_in_tree(formulas: List[Formula], proof_tree: ProofTree) -> List[Formula]:
    return [
        formula
        for existent_node in proof_tree.nodes
        for formula in formulas
        if formula.rep == existent_node.formula.rep
    ]


def _is_satisfiable(formulas: List[Formula], proof_tree: ProofTree) -> bool:
    return is_formulas_satisfiable([node.formula for node in proof_tree.nodes]
                                   + formulas)


def _is_formula_new(formula: Formula, proof_tree: ProofTree) -> bool:
    return all([
        formula.rep != node.formula.rep
        for node in proof_tree.nodes
    ])
