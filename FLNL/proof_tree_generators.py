import random
import logging
from collections import defaultdict
from typing import List, Optional, Any, Iterable, Tuple, Dict, Union, Callable
from pprint import pformat
import logging

from timeout_timer import timeout as timeout_context

from pprint import pprint
from .formula import (
    PREDICATES,
    CONSTANTS,
    Formula,
)
from .formula_checkers import is_ok_set as is_ok_formula_set
from .argument import Argument
from .argument_checkers import is_senseful as is_argument_senseful
from .interpretation import (
    generate_mappings_from_formula,
    generate_formulas_in_target_space,
    generate_complicated_arguments,
    interprete_formula,
    interprete_argument,
    formula_is_identical_to,
    argument_is_identical_to,
    generate_quantifier_arguments,
)
# from .utils import DelayedLogger
from .proof import ProofTree, ProofNode
from .exception import FormalLogicExceptionBase
from .utils import weighted_shuffle

from .formula import (
    IMPLICATION,
    AND,
    OR,
    NEGATION,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
)
import kern_profiler

# _LOG_ONLY_WHEN_FAILED = True
logger = logging.getLogger(__name__)


class ProofTreeGenerationFailure(FormalLogicExceptionBase):
    pass


class ProofTreeGenerator:

    def __init__(self,
                 arguments: List[Argument],
                 complicated_arguments_weight=0.0,
                 quantified_arguments_weight=0.0,
                 quantify_all_at_once=True,
                 elim_dneg=False):
        self.elim_dneg = elim_dneg

        self._complicated_arguments_weight = complicated_arguments_weight
        self.arguments, self.argument_weights = self._load_arguments(
            arguments,
            complicated_arguments_weight=self._complicated_arguments_weight,
            quantified_arguments_weight=quantified_arguments_weight,
            quantify_all_at_once=quantify_all_at_once,
            elim_dneg=elim_dneg,
        )

    @property
    def complicated_arguments_weight(self):
        return self._complicated_arguments_weight

    def _load_arguments(self,
                        arguments: List[Argument],
                        complicated_arguments_weight: float,
                        quantified_arguments_weight: float,
                        quantify_all_at_once: bool,
                        elim_dneg: bool) -> Tuple[List[Argument], List[Argument]]:
        logger.info('-- loading arguments ....')

        complicated_arguments: List[Argument] = []
        if complicated_arguments_weight > 0.0:
            for argment in arguments:
                for complicated_argument, _, name in generate_complicated_arguments(argment,
                                                                                    elim_dneg=elim_dneg,
                                                                                    suppress_op_expansion_if_exists=True,
                                                                                    get_name=True):
                    if _is_argument_new(complicated_argument, arguments + complicated_arguments):
                        complicated_argument.id += f'.{name}'
                        complicated_arguments.append(complicated_argument)

        quantified_arguments: List[Argument] = []
        if quantified_arguments_weight > 0.0:
            unique_formulas: List[Formula] = []
            for argument in arguments + complicated_arguments:
                for formula in argument.all_formulas:
                    if all(not formula_is_identical_to(formula, existent_formula) for existent_formula in unique_formulas):
                        unique_formulas.append(formula)

            for argument_type in [
                    'universal_quantifier_elim',

                    # we do not use existential_quantifier_intro since it has no chainable_args unless existential_quantifier_elim, which is not implemented yet.
                    # 'existential_quantifier_intro',
            ]:
                for i_formula, formula in enumerate(unique_formulas):
                    for quantified_argument in generate_quantifier_arguments(argument_type, formula, id_prefix=f'fomula-{str(i_formula).zfill(6)}', quantify_all_at_once=quantify_all_at_once):
                        if _is_argument_new(quantified_argument, arguments + complicated_arguments + quantified_arguments):
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

        logger.info('------- loaded arguments ------')
        for argument in _arguments:
            logger.info('weight: %f    %s', _argument_weights[argument], str(argument))

        return _arguments, _argument_weights

    def generate_tree(self,
                      depth: int,
                      branch_extension_steps: int,
                      max_retry=100,
                      timeout=5) -> Optional[ProofTree]:

        return self._run(
            'generate_tree()',
            max_retry,
            timeout,
            self._generate_tree,
            depth,
            branch_extension_steps,
        )

    def generate_stem(self,
                      depth: int,
                      max_retry=100,
                      timeout=5) -> Optional[ProofTree]:
        return self._run(
            'generate_stem()',
            max_retry,
            timeout,
            self._generate_stem,
            depth,
        )

    def extend_braches(self,
                       generate_initial_tree_fn: Callable[[], ProofTree],
                       # proof_tree: ProofTree,
                       branch_extension_steps: int,
                       depth_limit: Optional[int] = None,
                       max_retry=100,
                       timeout=5) -> ProofTree:
        """ extend branches of the tree

        Please make sure that generate_initial_tree_fn generate a completely new tree each time it is called.
        The reason is the following:
        (i) The current implementation of _extend_braches modifies the original tree.
        (ii) We try _extend_braches() multiple times if failed. Each trial needs a new tree.

        This is just the limiation of implications.
        For example we can omit generate_initial_tree_fn and use proof_tree as the argument,
        if we implement proof_tree.copy().
        However, the implementation of proof_tree.copy() cost a little and for now, we decided to bypass that.
        """
        return self._run(
            'extend_braches()',
            max_retry,
            timeout,
            self._extend_braches,
            generate_initial_tree_fn,
            branch_extension_steps,
            depth_limit=depth_limit,
        )

    def _run(self,
             log_name: str,
             max_retry: Optional[int],
             timeout: Optional[int],
             func: Callable,
             *args,
             **kwargs) -> Any:

        max_retry = max_retry or 9999
        timeout = timeout or 9999

        for i_trial in range(0, max_retry):
            logger.info('---- %s trial=%d ----', log_name, i_trial)
            try:
                with timeout_context(timeout, exception=TimeoutError):
                    result = func(*args, **kwargs)
                logger.info('-- %s succeeded!', log_name)
                return result
            except ProofTreeGenerationFailure as e:
                logger.warning('-- %s failed. The message of the LAST trial is the followings:', log_name)
                logger.warning('%s', str(e))
            except TimeoutError:
                logger.warning('-- %s the LAST trial failed with TimeoutError(timeout=%d)', log_name, timeout)
        raise ProofTreeGenerationFailure(f'-- {log_name} failed with max_retry={max_retry}.')

    def _generate_tree(self, depth: int, branch_extension_steps: int) -> Optional[ProofTree]:
        proof_tree = self._generate_stem(depth)
        proof_tree = self._extend_braches(lambda : proof_tree, branch_extension_steps, depth_limit=proof_tree.depth)
        return proof_tree

    def _generate_stem(self, depth: int) -> ProofTree:
        return _generate_stem(self.arguments,
                              depth,
                              PREDICATES,
                              CONSTANTS,
                              argument_weights=self.argument_weights,
                              elim_dneg=self.elim_dneg)

    def _extend_braches(self,
                        generate_initial_tree_fn: Callable[[], ProofTree],
                        branch_extension_steps: int,
                        depth_limit: Optional[int] = None) -> ProofTree:
        return _extend_braches(generate_initial_tree_fn(),
                               self.arguments,
                               branch_extension_steps,
                               PREDICATES,
                               CONSTANTS,
                               depth_limit=depth_limit,
                               argument_weights=self.argument_weights,
                               elim_dneg=self.elim_dneg)


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
               assumption_nodes: List[Optional[ProofNode]],
               conclusion_node: ProofNode,
               argument: Argument,
               proof_tree: ProofTree):

        for premise_node in premise_nodes:
            conclusion_node.add_child(premise_node)

        for assumption_node in assumption_nodes:
            conclusion_node.add_assump_child(assumption_node)

        conclusion_node.argument = argument

        for node in premise_nodes\
                + [node for node in assumption_nodes if node is not None]\
                + [conclusion_node]:
            proof_tree.add_node(node)

    for cur_arg in _shuffle_arguments(arguments, weights=argument_weights):  # try all the argument as starting point
        if len(cur_arg.assumptions) > 0:
            # the node with assumptions can not be used as the first node.
            continue

        proof_tree = ProofTree()
        cur_conclusion_node = ProofNode(cur_arg.conclusion)
        cur_premise_nodes = [ProofNode(premise) for premise in cur_arg.premises]
        update(cur_premise_nodes, [], cur_conclusion_node, cur_arg, proof_tree)

        is_tree_done = False
        while True:
            log_traces = []
            rejection_stats = defaultdict(int)
            # delayed_logger = DelayedLogger(logger, delayed=_LOG_ONLY_WHEN_FAILED)

            if proof_tree.depth >= depth:
                is_tree_done = True
                break

            formulas_in_tree = [node.formula for node in proof_tree.nodes]

            cur_conclusion = cur_conclusion_node.formula
            cur_assumption_nodes = [node for node in cur_conclusion_node.descendants if node.is_leaf]
            log_traces.append(f'   | cur_conclusion {cur_conclusion}')

            # Choose next argument
            chainable_args = []
            for arg in arguments:
                one_premise_matched = False
                for premise in arg.premises:
                    if not formula_is_identical_to(premise, cur_conclusion):
                        continue

                    if premise in arg.assumptions:
                        assumption = arg.assumptions[premise]
                        if not any(formula_is_identical_to(cur_assumption_node.formula, assumption)
                                   for cur_assumption_node in cur_assumption_nodes):
                            continue

                    one_premise_matched = True
                    break

                if one_premise_matched:
                    chainable_args.append(arg)

            if len(chainable_args) == 0:
                rejection_stats['len(chainable_args) == 0'] += 1

            is_arg_done = False
            next_arg_pulled = None
            for next_arg in _shuffle_arguments(chainable_args, argument_weights):
                if is_arg_done:
                    break
                log_traces.append(f'   |   | next_arg {next_arg}')

                # Choose mapping
                # The outer loops are for speedup: first build mappings on small variabl set and then use it for filtering out the mappings on large variable set.
                for premise in _shuffle(next_arg.premises):
                    if is_arg_done:
                        break
                    log_traces.append(f'   |   |   | premise {premise}')

                    assumption = next_arg.assumptions.get(premise, None)
                    for premise_mapping in generate_mappings_from_formula(
                        [premise] + ([assumption] if assumption is not None else []),
                        [cur_conclusion] + [node.formula for node in cur_assumption_nodes],
                        block_shuffle=True,
                    ):
                        if is_arg_done:
                            break
                        premise_pulled = interprete_formula(premise, premise_mapping, elim_dneg=elim_dneg)
                        assumption_pulled = interprete_formula(assumption, premise_mapping, elim_dneg=elim_dneg) if assumption is not None else None
                        log_traces.append(f'   |   |   | premise_pulled {premise_pulled}')
                        log_traces.append(f'   |   |   | assumption_pulled {assumption_pulled}')

                        if premise_pulled.rep != cur_conclusion.rep:  # chainable or not
                            rejection_stats['premise_pulled.rep != cur_conclusion.rep'] += 1
                            continue

                        if assumption_pulled is not None:
                            # print(0)
                            if all(assumption_pulled.rep != cur_assumption_node.formula.rep
                                   for cur_assumption_node in cur_assumption_nodes):
                                rejection_stats['assumption_pulled.rep != cur_assumption_node.formula.rep'] += 1
                                continue

                        # for early rejection
                        if not is_ok_formula_set([premise_pulled] + formulas_in_tree):
                            rejection_stats['not is_ok_formula_set([premise_pulled] + formulas_in_tree)'] += 1
                            continue

                        for mapping in generate_mappings_from_formula(
                            next_arg.all_formulas,
                            [cur_conclusion] + [Formula(' '.join(constant_pool + predicate_pool))],
                            constraints=premise_mapping,
                            block_shuffle=True,
                        ):
                            if is_arg_done:
                                break

                            next_arg_pulled = interprete_argument(next_arg, mapping, elim_dneg=elim_dneg)

                            if not is_argument_senseful(next_arg_pulled):
                                rejection_stats['not is_argument_senseful(next_arg_pulled)'] += 1
                                continue

                            if not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree):
                                rejection_stats['not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree)'] += 1
                                continue

                            if not _is_formula_new(next_arg_pulled.conclusion, formulas_in_tree):
                                rejection_stats['not _is_formula_new(next_arg_pulled.conclusion, formulas_in_tree)'] += 1
                                continue

                            other_premises = [premise for premise in next_arg_pulled.premises
                                              if premise.rep != cur_conclusion.rep]
                            if not _is_formulas_new(other_premises, formulas_in_tree):
                                # If any of other premises already exists in the tree, it will lead to a loop.
                                # We want to avoid a loop.
                                rejection_stats['not _is_formulas_new(other_premises, formulas_in_tree)'] += 1
                                continue

                            is_arg_done = True
                            break

            if is_arg_done:
                # Update
                next_assumption_nodes = []
                for i_premise, premise in enumerate(next_arg_pulled.premises):
                    if premise.rep == cur_conclusion.rep:
                        next_arg_pulled.premises[i_premise] = cur_conclusion  # refer to the unique object.
                    if premise in next_arg_pulled.assumptions:
                        assumption = next_arg_pulled.assumptions[premise]
                        for cur_assumption_node in cur_assumption_nodes:
                            if assumption.rep == cur_assumption_node.formula.rep:
                                next_arg_pulled.assumptions[premise] = cur_assumption_node.formula  # refer to the unique object.
                                next_assumption_nodes.append(cur_assumption_node)

                next_conclusion_node = ProofNode(next_arg_pulled.conclusion)
                next_conclusion_node.argument = next_arg_pulled
                next_premise_nodes = [
                    cur_conclusion_node if premise.rep == cur_conclusion.rep else ProofNode(premise)
                    for premise in next_arg_pulled.premises
                ]
                update(next_premise_nodes, next_assumption_nodes, next_conclusion_node, next_arg_pulled, proof_tree)

                cur_conclusion_node = next_conclusion_node
                cur_premise_nodes = next_premise_nodes
            else:
                rejection_stats_msg = '\n'.join([f'    {line}' for line in pformat(dict(rejection_stats)).split('\n')])
                log_traces_msg = '\n'.join(log_traces)
                msg = '\n'.join([
                    '_generate_stem() failed. The statistics are the followings:',
                    # f'start_arg          :    {start_arg}',  # start_arg is not that informative
                    f'cur_premise_nodes    :    {cur_premise_nodes}',
                    f'cur_conclusion_node  :    {cur_conclusion_node}',

                    'log trace:        :',
                    log_traces_msg,

                    'rejection stats   :',
                    rejection_stats_msg,
                ])
                raise ProofTreeGenerationFailure(msg)

        if is_tree_done:
            return proof_tree

    raise Exception('Unexpected')


def _extend_braches(proof_tree: ProofTree,
                    arguments: List[Argument],
                    num_steps: int,
                    predicate_pool: List[str],
                    constant_pool: List[str],
                    argument_weights: Optional[Dict[Argument, float]] = None,
                    depth_limit: Optional[int] = None,
                    elim_dneg=False) -> ProofTree:
    """ Extend branches of the proof_tree tree in a bottom-up manner.

    The steps are:
    (i) Choose a leaf node in the tree.
    (ii) Choose an argument where the conclusion of the argument matched the leaf node chosen in (i)
    (iii) Add the psemises of the chosen argument into tree.
    (iv) Repeat (ii) and (iii)
    """

    cur_step = 0
    while True:
        if cur_step >= num_steps:
            break

        formulas_in_tree = [node.formula for node in proof_tree.nodes]

<<<<<<< HEAD
        leaf_nodes = [
            node for node in proof_tree.leaf_nodes
            if proof_tree.get_node_depth(node) < proof_tree.depth
            and node.assump_parent is None  # assumptions shoud keep beeing leaf
        ]
=======
        leaf_nodes = [node for node in proof_tree.leaf_nodes]
        if depth_limit is not None:
            leaf_nodes = [node for node in leaf_nodes
                          if proof_tree.get_node_depth(node) < depth_limit]
>>>>>>> honoka-dev
        if len(leaf_nodes) == 0:
            logger.warning('Couldn\'t extend branch since the tree have no leaf nodes.')
            return proof_tree

        is_leaf_node_done = False
        next_arg_pulled = None
        target_leaf_node = None
        for leaf_node in _shuffle(leaf_nodes):
            log_traces = []
            rejection_stats = defaultdict(int)

            log_traces.append(f'   | leaf_node {leaf_node}')

            if is_leaf_node_done:
                break

            target_leaf_node = leaf_node

            # Choose next argument
<<<<<<< HEAD
            chainable_args = [
                arg for arg in arguments
                if formula_is_identical_to(arg.conclusion, leaf_node.formula)
                and len(arg.assumptions) == 0  # by it's logic, the argument with premise assumptions can not be applied in branch extension
            ]
=======
            chainable_args = []
            for arg in arguments:
                if formula_is_identical_to(arg.conclusion, leaf_node.formula):
                    chainable_args.append(arg)
>>>>>>> honoka-dev
            if len(chainable_args) == 0:
                rejection_stats['len(chainable_args) == 0'] += 1

            for next_arg in _shuffle_arguments(chainable_args, weights=argument_weights):

                if is_leaf_node_done:
                    break
                log_traces.append(f'   |   | next_arg {next_arg}')

                # Choose mapping
                # The following two nested loop is for speedup:
                # 1. First, we generate the small number of mappings by using small number of symbols. Then, we find appropriate sub-mappings
                # 2. Second, we generate full number of mappings, using the sub-mappings as filters.
                for conclusion_mapping in generate_mappings_from_formula(
                        [next_arg.conclusion],
                        # [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                        [leaf_node.formula],
                        block_shuffle=True,
                ):
                    if is_leaf_node_done:
                        break

                    conclusion_pulled = interprete_formula(next_arg.conclusion, conclusion_mapping, elim_dneg=elim_dneg)
                    log_traces.append(f'   |   |   | conclusion_pulled {conclusion_pulled}')

                    if conclusion_pulled.rep != leaf_node.formula.rep:
                        rejection_stats['conclusion_pulled.rep != leaf_node.formula.rep'] += 1
                        continue

                    # for early rejection
                    if not is_ok_formula_set([conclusion_pulled] + formulas_in_tree):
                        rejection_stats['not is_ok_formula_set([conclusion_pulled] + formulas_in_tree)'] += 1
                        continue

                    for mapping in generate_mappings_from_formula(
                        next_arg.all_formulas,
                        [leaf_node.formula] + [Formula(' '.join(constant_pool + predicate_pool))],
                        constraints=conclusion_mapping,
                        block_shuffle=True,
                    ):
                        next_arg_pulled = interprete_argument(next_arg, mapping, elim_dneg=elim_dneg)

                        if not is_argument_senseful(next_arg_pulled):
                            rejection_stats['is_argument_nonsense(next_arg_pulled)'] += 1
                            continue

                        if not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree):
                            rejection_stats['not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree)'] += 1
                            continue

                        if not _is_formulas_new(next_arg_pulled.premises, formulas_in_tree):
                            # If any of the premises are already in the tree, it will lead to a loop.
                            # We want to avoid a loop.
                            rejection_stats['not _is_formulas_new(next_arg_pulled.premises, formulas_in_tree)'] += 1
                            continue

                        is_leaf_node_done = True
                        break

        if is_leaf_node_done:
            # Upate tree
            next_arg_pulled.conclusion = target_leaf_node.formula  # refer to the sampe object
            target_leaf_node.argument = next_arg_pulled
            next_premise_nodes = [ProofNode(premise)
                                  for premise in next_arg_pulled.premises]
            for premise_node in next_premise_nodes:
                proof_tree.add_node(premise_node)
                target_leaf_node.add_child(premise_node)
            cur_step += 1
        else:
            rejection_stats_msg = '\n'.join([f'    {line}' for line in pformat(dict(rejection_stats)).split('\n')])
            log_traces_msg = '\n'.join(log_traces)
            msg = '\n'.join([
                '_extend_braches() failed. The statistics are the followings:',
                f'leaf_node:    {leaf_node}',

                'log trace:        :',
                log_traces_msg,

                'rejection stats   :',
                rejection_stats_msg,

            ])
            raise ProofTreeGenerationFailure(msg)

    return proof_tree


def _is_argument_new(argument: Argument, arguments: List[Argument]) -> bool:
    is_already_added = False
    for existent_argument in arguments:
        if argument_is_identical_to(argument, existent_argument):
            logger.info('-- Argument is identical to the already added argument. Will be skipped. --')
            logger.info('tried to add  : %s', str(argument))
            logger.info('already added : %s', str(existent_argument))
            is_already_added = True
            break
    return not is_already_added


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
