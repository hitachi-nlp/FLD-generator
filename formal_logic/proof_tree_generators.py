import random
import logging
from typing import List, Optional, Any, Iterable, Tuple, Dict

from timeout_timer import timeout as timeout_context

from pprint import pprint
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
    formula_is_identical_to,
    argument_is_identical_to,
    generate_quantifier_arguments,
)
from .proof import ProofTree, ProofNode
from .exception import FormalLogicExceptionBase
from .utils import weighted_shuffle

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
                 complicated_arguments_weight=0.0,
                 quantified_arguments_weight=0.0,
                 quantify_all_at_once=True,
                 elim_dneg=False,
                 timeout: Optional[int] = 30):
        self.elim_dneg = elim_dneg
        self.timeout = timeout

        self._arguments, self._argument_weights = self._load_arguments(
            arguments,
            complicated_arguments_weight=complicated_arguments_weight,
            quantified_arguments_weight=quantified_arguments_weight,
            quantify_all_at_once=quantify_all_at_once,
            elim_dneg=elim_dneg,
        )

    def _load_arguments(self,
                        arguments: List[Argument],
                        complicated_arguments_weight: float,
                        quantified_arguments_weight: float,
                        quantify_all_at_once: bool,
                        elim_dneg: bool) -> Tuple[List[Argument], List[Argument]]:
        logger.info('loading arguments ....')

        def is_argument_new(argument: Argument, arguments: List[Argument]) -> bool:
            is_already_added = False
            for existent_argument in arguments:
                if argument_is_identical_to(argument, existent_argument):
                    logger.info('-- Argument is identical to the already added argument. Will be skipped. --')
                    logger.info('tried to add  : %s', str(argument))
                    logger.info('already added : %s', str(existent_argument))
                    is_already_added = True
                    break
            return not is_already_added

        complicated_arguments: List[Argument] = []
        if complicated_arguments_weight > 0.0:
            for argment in arguments:
                for complicated_argument, _, name in generate_complicated_arguments(argment, elim_dneg=elim_dneg, get_name=True):
                    if is_argument_new(complicated_argument, arguments + complicated_arguments):
                        complicated_argument.id += f'.{name}'
                        complicated_arguments.append(complicated_argument)

        quantified_arguments: List[Argument] = []
        if quantified_arguments_weight > 0.0:
            unique_formulas: List[Formula] = []
            for argument in arguments + complicated_arguments:
                for formula in argument.all_formulas:
                    if all(not formula_is_identical_to(formula, existent_formula) for existent_formula in unique_formulas):
                        unique_formulas.append(formula)

            for argument_type in ['universal_quantifier_elim', 'existential_quantifier_intro']:
                for i_formula, formula in enumerate(unique_formulas):
                    for quantified_argument in generate_quantifier_arguments(argument_type, formula, id_prefix=f'fomula-{i_formula}', quantify_all_at_once=quantify_all_at_once):
                        if is_argument_new(quantified_argument, arguments + complicated_arguments + quantified_arguments):
                            quantified_arguments.append(quantified_argument)

        def calc_argument_weight(argument: Argument) -> float:
            if argument in arguments:
                return 1 / len(arguments) * (1 - complicated_arguments_weight - quantified_arguments_weight) if len(arguments) > 0 else None
            elif argument in complicated_arguments:
                return 1 / len(complicated_arguments) * complicated_arguments_weight if len(arguments) > 0 else None
            elif argument in quantified_arguments:
                return 1 / len(quantified_arguments) * complicated_arguments_weight if len(arguments) > 0 else None
            else:
                raise NotImplementedError()

        _arguments = arguments + complicated_arguments + quantified_arguments
        _argument_weights = {argument: calc_argument_weight(argument) for argument in _arguments}

        # TODO: check sum of weights

        logger.info('================================================     loaded arguments     ================================================')
        # for argument in sorted(_arguments, key=lambda arg: arg.id):
        for argument in _arguments:
            logger.info('weight: %f    %s', _argument_weights[argument], str(argument))

        return _arguments, _argument_weights

    # def _make_rough_weight_extended_arguments(self,
    #                                           this_arguments: List[Argument],
    #                                           that_arguments: List[Argument],
    #                                           this_weight: float) -> List[Argument]:
    #     """
    #     this_weight = len(this_arguments) * n / (len(this_arguments) * n + len(that_arguments))
    #     => n = this_weight * len(that_arguments) / ( len(this_arguments) - len(this_arguments) * this_weight )
    #          = ( this_weight / (1 - this_weight) ) * ( len(that_arguments) / len(this_arguments) )
    #     """
    #     if this_weight == 1.0:
    #         return this_arguments
    #     elif this_weight >= 0.99:
    #         logger.warning('we do not include that_arguments since the this_weight is so high (>= 0.99)')
    #         return this_arguments

    #     this_multiplier = int(this_weight / (1 - this_weight) * (len(that_arguments) / len(this_arguments)))
    #     if this_multiplier == 0:  # down sampling
    #         raise NotImplementedError()

    #     weight_extended_this_arguments = []
    #     for _ in range(0, this_multiplier):
    #         weight_extended_this_arguments.extend(this_arguments)

    #     return weight_extended_this_arguments + that_arguments

    def generate_tree(self,
                      depth=3,
                      max_retry=100) -> Optional[ProofTree]:
        for _ in range(0, max_retry):
            try:
                proof_tree = _generate_tree(self._arguments,
                                            argument_weights=self._argument_weights,
                                            depth=depth,
                                            elim_dneg=self.elim_dneg,
                                            timeout=self.timeout)
                return proof_tree
            except ProofTreeGenerationFailure as e:
                logger.info('Generation failed with message "%s" Will retry', str(e))
            except TimeoutError:
                logger.info('Generation failed with TimeoutError(). Will retry')
        raise ProofTreeGenerationFailure(f'generate_tree() failed with max_retry={max_retry}.')


@profile
def _generate_tree(arguments: List[Argument],
                   argument_weights: Optional[Dict[Argument, float]] = None,
                   depth=1,
                   elim_dneg=False,
                   timeout: Optional[int] = None) -> Optional[ProofTree]:

    timeout = timeout or 99999999
    with timeout_context(timeout, exception=TimeoutError):
        proof_tree = _generate_stem(arguments, depth, PREDICATES, CONSTANTS, argument_weights=argument_weights, elim_dneg=elim_dneg)
        _extend_braches(proof_tree, arguments, depth, PREDICATES, CONSTANTS, argument_weights=argument_weights, elim_dneg=elim_dneg)

    return proof_tree


@profile
def _generate_stem(arguments: List[Argument],
                   depth: int,
                   predicate_pool: List[str],
                   constant_pool: List[str],
                   argument_weights: Optional[Dict[Argument, float]] = None,
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

    for cur_arg in _shuffle_arguments(arguments, weights=argument_weights):
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
                if any((formula_is_identical_to(premise, cur_conclusion)
                        for premise in arg.premises))
            ]
            if len(chainable_args) == 0:
                break

            is_arg_done = False
            next_arg_replaced = None
            for next_arg_unreplaced in _shuffle_arguments(chainable_args, argument_weights):
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
                raise ProofTreeGenerationFailure('_generate_stem() failed.')

        if is_tree_done:
            return proof_tree

    raise Exception('Unexpected')


@profile
def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    max_steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    argument_weights: Optional[Dict[Argument, float]] = None,
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
                if formula_is_identical_to(arg.conclusion, leaf_node.formula)
            ]
            if len(chainable_args) == 0:
                # logger.info('_extend_braches() retry since no chainable arguments found ...')
                continue

            for next_arg_unreplaced in _shuffle_arguments(chainable_args, weights=argument_weights):
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
            raise ProofTreeGenerationFailure('_extend_braches failed.')


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


# def _weighted_shuffle(weighted_elems: List[Tuple[float, Any]]) -> Iterable[Any]:
#     weights = [weight for weight, _ in weighted_elems]
#     for idx in weighted_shuffle(weights):
#         yield weighted_elems[idx]


def _shuffle(elems: List[Any],
             weights: Optional[List[float]] = None) -> Iterable[Any]:
    if weights is None:
        yield from random.sample(elems, len(elems))
    else:
        for idx in weighted_shuffle(weights):
            yield elems[idx]


def _shuffle_arguments(arguments: List[Argument],
                       weights: Optional[Dict[Argument, float]] = None) -> Iterable[Argument]:
    _weights = [weights[argument] for argument in arguments] if weights is not None else None
    yield from _shuffle(arguments, weights=_weights)
