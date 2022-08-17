import random
import logging
from typing import List, Optional, Any

from timeout_timer import timeout as timeout_context

from .formula import (
    PREDICATES,
    CONSTANTS,
    Formula,
)
from .formula_checkers import (
    is_formula_set_nonsense,
)
from .argument import Argument
from .argument_checkers import is_argument_nonsense
from .replacements import (
    generate_replacement_mappings_from_formula,
    generate_replaced_formulas,
    generate_complicated_arguments,
    replace_formula,
    replace_argument,
    is_formula_identical,
)
from .proof import ProofTree, ProofNode
from .exception import FormalLogicExceptionBase

from .formula import (
    IMPLICATION,
    AND,
    OR,
    NOT,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
)
import kern_profiler

logger = logging.getLogger(__name__)


class ProofTreeGenerationFailure(FormalLogicExceptionBase):
    pass


class ProofTreeGenerator:

    def __init__(self,
                 arguments: List[Argument],
                 allow_complication=False,
                 elim_dneg=False,
                 timeout: Optional[int] = 30):
        self.allow_complication = allow_complication
        self.elim_dneg = elim_dneg
        self.timeout = timeout

        if allow_complication:
            self.arguments = []
            for argment in arguments:
                for complicated_argument, _, name in generate_complicated_arguments(argment, elim_dneg=elim_dneg, get_name=True):
                    complicated_argument.id += f'.{name}'
                    self.arguments.append(complicated_argument)
        else:
            self.arguments = arguments

        logger.info('============ arguments for generation ============')
        for argument in sorted(self.arguments, key=lambda arg: arg.id):
            logger.info(argument)

    def generate_tree(self, depth=3) -> Optional[ProofTree]:
        for _ in range(0, 10):
            try:
                proof_tree = _generate_tree(self.arguments,
                                            depth=depth,
                                            elim_dneg=self.elim_dneg,
                                            timeout=self.timeout)
                return proof_tree
            except ProofTreeGenerationFailure:
                logger.info('Generation failed with ProofTreeGenerationFailure(). Will retry')
            except TimeoutError:
                logger.info('Generation failed with TimeoutError(). Will retry')
        raise ProofTreeGenerationFailure()


@profile
def _generate_tree(arguments: List[Argument],
                   depth=1,
                   elim_dneg=False,
                   timeout: Optional[int] = None) -> Optional[ProofTree]:

    timeout = timeout or 99999999
    with timeout_context(timeout, exception=TimeoutError):
        proof_tree = _generate_stem(arguments, depth, PREDICATES, CONSTANTS, elim_dneg=elim_dneg)
        _extend_braches(proof_tree, arguments, depth, PREDICATES, CONSTANTS, elim_dneg=elim_dneg)

    return proof_tree


@profile
def _generate_stem(arguments: List[Argument],
                   depth: int,
                   predicate_pool: List[str],
                   constant_pool: List[str],
                   elim_dneg=False) -> Optional[ProofTree]:
    """ Generate stem of proof tree in a top-down manner.

    The steps are:
    (i) Choose an argument.
    (ii) Add the premises of the argument to tree.
    (iii) Choose next argument where one of the premises of the chosen argument is the same as the conclusion of the argument chosen in (i).
    (iv) Add the premises of the argument chosen in (iii)
    (v) Repeat (iii) - (iv).
    """

    def update(premise_nodes: List[ProofNode],
               conclusion_node: ProofNode,
               argument: Argument,
               proof_tree: ProofTree):
        for premise_node in premise_nodes:
            conclusion_node.add_child(premise_node)
        conclusion_node.argument = argument
        for node in premise_nodes + [conclusion_node]:
            proof_tree.add_node(node)

    for cur_arg in _shuffle(arguments):
        proof_tree = ProofTree()
        cur_conclusion_node = ProofNode(cur_arg.conclusion)
        cur_premise_nodes = [ProofNode(premise) for premise in cur_arg.premises]
        update(cur_premise_nodes, cur_conclusion_node, cur_arg, proof_tree)

        is_tree_done = False
        while True:
            if proof_tree.depth >= depth:
                is_tree_done = True
                break

            formulas_in_tree = [node.formula for node in proof_tree.nodes]

            cur_conclusion = cur_conclusion_node.formula

            # Choose next argument
            chainable_args = [
                arg for arg in arguments
                if any((is_formula_identical(premise, cur_conclusion)
                        for premise in arg.premises))
            ]
            if len(chainable_args) == 0:
                break

            is_arg_done = False
            next_arg_replaced = None
            for next_arg_unreplaced in _shuffle(chainable_args):
                if is_arg_done:
                    break

                # Choose mapping
                # The outer loops are for speedup: first build mappings on small variabl set and then use it for filtering out the mappings on large variable set.
                for premise in _shuffle(next_arg_unreplaced.premises):
                    if is_arg_done:
                        break

                    for premise_mapping in generate_replacement_mappings_from_formula(
                        [premise],
                        # [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                        [cur_conclusion],
                        allow_complication=False,
                        block_shuffle=True,
                    ):
                        if is_arg_done:
                            break

                        premise_replaced = replace_formula(premise, premise_mapping, elim_dneg=elim_dneg)

                        if premise_replaced.rep != cur_conclusion.rep:  # chainable or not
                            continue

                        # for early rejection
                        if is_formula_set_nonsense([premise_replaced] + formulas_in_tree):
                            continue

                        for mapping in generate_replacement_mappings_from_formula(
                            next_arg_unreplaced.premises + [next_arg_unreplaced.conclusion],
                            [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                            constraints=premise_mapping,
                            allow_complication=False,
                            block_shuffle=True,
                        ):
                            if is_arg_done:
                                break

                            next_arg_replaced = replace_argument(next_arg_unreplaced, mapping, elim_dneg=elim_dneg)

                            if is_argument_nonsense(next_arg_replaced):
                                continue

                            if is_formula_set_nonsense(next_arg_replaced.all_formulas + formulas_in_tree):
                                continue

                            if not _is_formula_new(next_arg_replaced.conclusion, formulas_in_tree):
                                continue

                            other_premises = [premise for premise in next_arg_replaced.premises
                                              if premise.rep != cur_conclusion.rep]
                            if not _is_formulas_new(other_premises, formulas_in_tree):
                                # If any of other premises already exists in the tree, it will lead to a loop.
                                # We want to avoid a loop.
                                continue

                            is_arg_done = True
                            break

            if is_arg_done:
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

                cur_conclusion_node = next_conclusion_node
                cur_premise_nodes = next_premise_nodes
            else:
                raise ProofTreeGenerationFailure()

        if is_tree_done:
            return proof_tree

    raise Exception('Unexpected')


@profile
def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    max_steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    elim_dneg=False) -> None:
    """ Extend branches of the proof_tree tree in a bottom-up manner.

    The steps are:
    (i) Choose a leaf node in the tree.
    (ii) Choose an argument where the conclusion of the argument matched the leaf node chosen in (i)
    (iii) Add the psemises of the chosen argument into tree.
    (iv) Repeat (ii) and (iii)
    """

    cur_step = 0
    while True:
        if cur_step >= max_steps:
            break

        formulas_in_tree = [node.formula for node in proof_tree.nodes]

        leaf_nodes = [node for node in proof_tree.leaf_nodes
                      if proof_tree.get_node_depth(node) < proof_tree.depth]
        if len(leaf_nodes) == 0:
            return

        is_leaf_node_done = False
        next_arg_replaced = None
        target_leaf_node = None
        for leaf_node in _shuffle(leaf_nodes):
            if is_leaf_node_done:
                break

            target_leaf_node = leaf_node

            # Choose next argument
            chainable_args = [
                arg for arg in arguments
                if is_formula_identical(arg.conclusion, leaf_node.formula)
            ]
            if len(chainable_args) == 0:
                # logger.info('_extend_braches() retry since no chainable arguments found ...')
                continue

            for next_arg_unreplaced in _shuffle(chainable_args):
                if is_leaf_node_done:
                    break

                # Choose mapping
                # The following two nested loop is for speedup:
                # 1. First, we generate the small number of mappings by using small number of symbols. Then, we find appropriate sub-mappings
                # 2. Second, we generate full number of mappings, using the sub-mappings as filters.
                for conclusion_mapping in generate_replacement_mappings_from_formula(
                        [next_arg_unreplaced.conclusion],
                        # [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                        [leaf_node.formula],
                        allow_complication=False,
                        block_shuffle=True,
                ):
                    if is_leaf_node_done:
                        break

                    conclusion_replaced = replace_formula(next_arg_unreplaced.conclusion, conclusion_mapping, elim_dneg=elim_dneg)

                    if conclusion_replaced.rep != leaf_node.formula.rep:
                        continue

                    # for early rejection
                    if is_formula_set_nonsense([conclusion_replaced] + formulas_in_tree):
                        continue

                    for mapping in generate_replacement_mappings_from_formula(
                        next_arg_unreplaced.all_formulas,
                        [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                        constraints=conclusion_mapping,
                        allow_complication=False,
                        block_shuffle=True,
                    ):
                        next_arg_replaced = replace_argument(next_arg_unreplaced, mapping, elim_dneg=elim_dneg)

                        if is_argument_nonsense(next_arg_replaced):
                            continue

                        if is_formula_set_nonsense(next_arg_replaced.all_formulas + formulas_in_tree):
                            continue

                        if not _is_formulas_new(next_arg_replaced.premises, formulas_in_tree):
                            # If any of the premises are already in the tree, it will lead to a loop.
                            # We want to avoid a loop.
                            continue

                        is_leaf_node_done = True
                        break

        if is_leaf_node_done:
            # Upate tree
            next_arg_replaced.conclusion = target_leaf_node.formula  # refer to the sampe object
            target_leaf_node.argument = next_arg_replaced
            next_premise_nodes = [ProofNode(premise)
                                  for premise in next_arg_replaced.premises]
            for premise_node in next_premise_nodes:
                proof_tree.add_node(premise_node)
                target_leaf_node.add_child(premise_node)
            cur_step += 1
        else:
            raise ProofTreeGenerationFailure()


def _is_formulas_new(formulas: List[Formula], existing_formulas: List[Formula]) -> bool:
    return all((_is_formula_new(formula, existing_formulas)
                for formula in formulas))


def _is_formula_new(formula: Formula,
                    existing_formulas: List[Formula]) -> bool:
    return len(_search_formulas([formula], existing_formulas)) == 0


def _search_formulas(formulas: List[Formula],
                     existing_formulas: List[Formula]) -> List[Formula]:
    return [
        existing_formula
        for formula in formulas
        for existing_formula in existing_formulas
        if existing_formula.rep == formula.rep
    ]


def _search_formula(formula: Formula,
                    existing_formulas: List[Formula]) -> List[Formula]:
    return [
        existing_formula
        for existing_formula in existing_formulas
        if existing_formula.rep == formula.rep
    ]


def _shuffle(elems: List[Any]) -> List[Any]:
    return random.sample(elems, len(elems))
