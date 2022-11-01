import random
import json
import logging
import math
from collections import defaultdict
from typing import List, Optional, Any, Iterable, Tuple, Dict, Union, Callable
from pprint import pformat, pprint
import logging

from .formula import (
    PREDICATES,
    CONSTANTS,
    Formula,
    OR,
)
from .formula_checkers import (
    is_ok_set as is_ok_formula_set,
    is_consistent_set as is_consistent_formula_set,
    is_new as is_formula_new,
)
from .argument import Argument
from .argument_checkers import (
    is_senseful as is_argument_senseful,
)
from .interpretation import (
    generate_mappings_from_formula,
    generate_formulas_in_target_space,
    generate_complicated_arguments,
    generate_partially_quantifier_arguments,
    interpret_formula,
    interpret_argument,
    formula_is_identical_to,
    argument_is_identical_to,
    generate_quantifier_axiom_arguments,
)
# from .utils import DelayedLogger
from .proof import ProofTree, ProofNode
from .exception import FormalLogicExceptionBase
from .utils import weighted_shuffle, run_with_timeout_retry, RetryAndTimeoutFailure

from .formula import (
    IMPLICATION,
    AND,
    OR,
    NEGATION,
    PREDICATES,
    CONSTANTS,
    VARIABLES,
    CONTRADICTION,
)
import kern_profiler

# _LOG_ONLY_WHEN_FAILED = True
logger = logging.getLogger(__name__)


class ProofTreeGenerationFailure(FormalLogicExceptionBase):
    pass


_REFERENCE_ARGUMENTS = [
    Argument(
        [Formula('{A}')],
        Formula('{A}'),
        {},
        id='reference.pred_only',
    ),
    Argument(
        [Formula('{A}{a}')],
        Formula('{A}{a}'),
        {},
        id='reference.pred_arg',
    ),
]


class ProofTreeGenerator:

    @profile
    def __init__(self,
                 arguments: List[Argument],
                 complicated_arguments_weight=0.0,
                 quantifier_arguments_weight=0.0,
                 quantifier_axiom_arguments_weight=0.0,
                 quantify_all_at_once=True,
                 or_arguments_factor=0.2,  # or is not that impotant for NLI
                 existential_arguments_factor=0.2,  # existential quantifier is not that impotant for NLI
                 universal_theorem_argument_factor=1.0,
                 elim_dneg=False,
                 disallow_contradiction_as_hypothesis=True,
                 allow_reference_arguments_when_depth_1=True):
        if not math.isclose(quantifier_arguments_weight, 0.0):
            raise NotImplementedError('Currently, the arguments generated by generate_partially_quantifier_arguments()'
                                      'such as "(x) Fx -> Ga" is not supported by the translation configuration.')

        self.elim_dneg = elim_dneg
        self.disallow_contradiction_as_hypothesis = disallow_contradiction_as_hypothesis

        self._complicated_arguments_weight = complicated_arguments_weight
        self.arguments, self.argument_weights = self._load_arguments(
            arguments,
            complicated_arguments_weight=self._complicated_arguments_weight,
            quantifier_arguments_weight=quantifier_arguments_weight,
            quantifier_axiom_arguments_weight=quantifier_axiom_arguments_weight,
            quantify_all_at_once=quantify_all_at_once,
            or_arguments_factor=or_arguments_factor,
            existential_arguments_factor=existential_arguments_factor,
            universal_theorem_argument_factor=universal_theorem_argument_factor,
            elim_dneg=elim_dneg,
            allow_reference_arguments_when_depth_1=allow_reference_arguments_when_depth_1,
        )

    @property
    def complicated_arguments_weight(self):
        return self._complicated_arguments_weight

    def _load_arguments(self,
                        arguments: List[Argument],
                        complicated_arguments_weight: float,
                        quantifier_arguments_weight: float,
                        quantifier_axiom_arguments_weight: float,
                        quantify_all_at_once: bool,
                        or_arguments_factor: float,
                        existential_arguments_factor: float,
                        universal_theorem_argument_factor: float,
                        elim_dneg: bool,
                        allow_reference_arguments_when_depth_1: bool) -> Tuple[List[Argument], List[Argument]]:
        logger.info('-- loading arguments ....')

        arguments = _REFERENCE_ARGUMENTS + arguments

        complicated_arguments: List[Argument] = []
        if complicated_arguments_weight > 0.0:
            for argument in arguments:
                for quantifier_argument, _, name in generate_complicated_arguments(argument,
                                                                                   elim_dneg=elim_dneg,
                                                                                   suppress_op_expansion_if_exists=True,
                                                                                   get_name=True):
                    if _is_argument_new(quantifier_argument, arguments + complicated_arguments):  # SLOW
                        quantifier_argument.id += f'.{name}'
                        complicated_arguments.append(quantifier_argument)

        quantified_arguments: List[Argument] = []
        if quantifier_arguments_weight > 0.0:
            for argument in arguments + complicated_arguments:
                for quantifier_type in ['universal', 'existential']:
                    for quantifier_argument, _, name in generate_partially_quantifier_arguments(argument,
                                                                                                quantifier_type,
                                                                                                elim_dneg=elim_dneg,
                                                                                                quantify_all_at_once_in_a_formula=True,  # current translation config does not support formulas such as (x) Ax v Ba
                                                                                                get_name=True):
                        if _is_argument_new(quantifier_argument, arguments + complicated_arguments + quantified_arguments):
                            quantified_arguments.append(quantifier_argument)
                            quantifier_argument.id += f'.{name}'

        quantifier_axiom_arguments: List[Argument] = []
        if quantifier_axiom_arguments_weight > 0.0:
            unique_formulas: List[Formula] = []
            for argument in arguments + complicated_arguments:
                for formula in argument.all_formulas:
                    if all(not formula_is_identical_to(formula, existent_formula) for existent_formula in unique_formulas):
                        unique_formulas.append(formula)

            for argument_type in [
                    'universal_quantifier_elim',

                    # we do not use existential_quantifier_intro since it has no chainable_args without existential_quantifier_elim, which is not implemented yet.
                    # 'existential_quantifier_intro',
            ]:
                for i_formula, formula in enumerate(unique_formulas):
                    if len(formula.variables) > 0:
                        continue
                    for quantifier_axiom_argument in generate_quantifier_axiom_arguments(argument_type, formula, id_prefix=f'fomula-{str(i_formula).zfill(6)}', quantify_all_at_once=quantify_all_at_once):
                        if _is_argument_new(quantifier_axiom_argument, arguments + complicated_arguments + quantifier_axiom_arguments):
                            quantifier_axiom_arguments.append(quantifier_axiom_argument)

        def calc_argument_weight(argument: Argument) -> float:
            if argument in arguments:
                return 1 / len(arguments) * (1 - complicated_arguments_weight - quantifier_arguments_weight - quantifier_axiom_arguments_weight) if len(arguments) > 0 else None
            elif argument in complicated_arguments:
                return 1 / len(complicated_arguments) * complicated_arguments_weight if len(complicated_arguments) > 0 else None
            elif argument in quantified_arguments:
                return 1 / len(quantified_arguments) * quantifier_arguments_weight if len(quantified_arguments) > 0 else None
            elif argument in quantifier_axiom_arguments:
                return 1 / len(quantifier_axiom_arguments) * complicated_arguments_weight if len(quantifier_axiom_arguments) > 0 else None
            else:
                raise NotImplementedError()

        _arguments = arguments + complicated_arguments + quantified_arguments + quantifier_axiom_arguments
        _argument_weights = {argument: calc_argument_weight(argument) for argument in _arguments}

        def is_or_formula(formula: Formula) -> bool:
            return formula.rep.find(f' {OR} ') >= 0

        def is_or_argument(argument: Argument) -> bool:
            return any(is_or_formula(formula) for formula in argument.all_formulas)

        def is_existential_argument(argument: Argument) -> bool:
            return argument.id.startswith('existential')

        def is_universal_theorem_argument(argument: Argument) -> bool:
            return argument.id.startswith('universal_theorem')

        _argument_weights = {
            argument: (weight * or_arguments_factor if is_or_argument(argument) else weight)
            for argument, weight in _argument_weights.items()
        }

        _argument_weights = {
            argument: (weight * existential_arguments_factor if is_existential_argument(argument) else weight)
            for argument, weight in _argument_weights.items()
        }

        _argument_weights = {
            argument: (weight * universal_theorem_argument_factor if is_universal_theorem_argument(argument) else weight)
            for argument, weight in _argument_weights.items()
        }

        logger.info('------- loaded arguments ------')
        for argument in _arguments:
            logger.info('weight: %f    %s', _argument_weights[argument], str(argument))

        return _arguments, _argument_weights

    def generate_tree(self,
                      depth: int,
                      branch_extension_steps: int,
                      max_retry=100,
                      timeout=5) -> Optional[ProofTree]:
        if depth == 1:
            logger.info('do only generate_stem() since depth=1 tree can not be extend_branches()')
            return self.generate_stem(depth, max_retry=max_retry, timeout=timeout)
        else:
            try:
                return run_with_timeout_retry(
                    self._generate_tree,
                    func_args=[depth, branch_extension_steps],
                    func_kwargs={},
                    retry_exception_class=ProofTreeGenerationFailure,
                    max_retry=max_retry,
                    timeout=timeout,
                    logger=logger,
                    log_title='generate_tree()',
                )
            except RetryAndTimeoutFailure as e:
                raise ProofTreeGenerationFailure(str(e))

    def generate_stem(self,
                      depth: int,
                      max_retry=100,
                      timeout=5) -> Optional[ProofTree]:
        try:
            return run_with_timeout_retry(
                self._generate_stem,
                func_args=[depth],
                func_kwargs={},
                retry_exception_class=ProofTreeGenerationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='generate_stem()',
            )
        except RetryAndTimeoutFailure as e:
            raise ProofTreeGenerationFailure(str(e))

    def extend_branches(self,
                        generate_initial_tree_fn: Callable[[], ProofTree],
                        # proof_tree: ProofTree,
                        branch_extension_steps: int,
                        depth_limit: Optional[int] = None,
                        max_retry=100,
                        timeout=5) -> ProofTree:
        """ extend branches of the tree

        Please make sure that generate_initial_tree_fn generate a completely new tree each time it is called.
        The reason is the following:
        (i) The current implementation of _extend_branches modifies the original tree.
        (ii) We try _extend_branches() multiple times if failed. Each trial needs a new tree.

        This is just the limiation of implications.
        For example we can omit generate_initial_tree_fn and use proof_tree as the argument,
        if we implement proof_tree.copy().
        However, the implementation of proof_tree.copy() cost a little and for now, we decided to bypass that.
        """
        try:
            return run_with_timeout_retry(
                self._extend_branches,
                func_args=[generate_initial_tree_fn, branch_extension_steps],
                func_kwargs={'depth_limit': depth_limit},
                retry_exception_class=ProofTreeGenerationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='extend_branches()',
            )
        except RetryAndTimeoutFailure as e:
            raise ProofTreeGenerationFailure(str(e))

    def _generate_tree(self, depth: int, branch_extension_steps: int) -> Optional[ProofTree]:
        proof_tree = self._generate_stem(depth)
        proof_tree = self._extend_branches(lambda : proof_tree, branch_extension_steps, depth_limit=proof_tree.depth)
        return proof_tree

    def _generate_stem(self, depth: int) -> ProofTree:
        return _generate_stem(self.arguments,
                              depth,
                              PREDICATES,
                              CONSTANTS,
                              argument_weights=self.argument_weights,
                              elim_dneg=self.elim_dneg,
                              disallow_contradiction_as_hypothesis=self.disallow_contradiction_as_hypothesis)

    def _extend_branches(self,
                         generate_initial_tree_fn: Callable[[], ProofTree],
                         branch_extension_steps: int,
                         depth_limit: Optional[int] = None) -> ProofTree:
        return _extend_branches(generate_initial_tree_fn(),
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
                   elim_dneg=False,
                   disallow_contradiction_as_hypothesis=False,
                   allow_reference_arguments_when_depth_1=True) -> Optional[ProofTree]:
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
        if cur_arg.id.startswith('reference') and (depth != 1 or not allow_reference_arguments_when_depth_1):
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
            leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]

            cur_conclusion = cur_conclusion_node.formula
            cur_possible_assumption_nodes = [node
                                             for node in cur_conclusion_node.descendants
                                             if node.is_leaf and node.assump_parent is None]
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
                                   for cur_assumption_node in cur_possible_assumption_nodes):
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
                        [cur_conclusion] + [node.formula for node in cur_possible_assumption_nodes],
                        shuffle=True,
                    ):
                        if is_arg_done:
                            break
                        premise_pulled = interpret_formula(premise, premise_mapping, elim_dneg=elim_dneg)
                        assumption_pulled = interpret_formula(assumption, premise_mapping, elim_dneg=elim_dneg) if assumption is not None else None
                        log_traces.append(f'   |   |   | premise_pulled {premise_pulled}')
                        log_traces.append(f'   |   |   | assumption_pulled {assumption_pulled}')

                        if premise_pulled.rep != cur_conclusion.rep:  # chainable or not
                            rejection_stats['premise_pulled.rep != cur_conclusion.rep'] += 1
                            continue

                        if assumption_pulled is not None:
                            if all(assumption_pulled.rep != cur_assumption_node.formula.rep
                                   for cur_assumption_node in cur_possible_assumption_nodes):
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
                            shuffle=True,
                        ):
                            if is_arg_done:
                                break

                            next_arg_pulled = interpret_argument(next_arg, mapping, elim_dneg=elim_dneg)

                            if not is_argument_senseful(next_arg_pulled):
                                rejection_stats['not is_argument_senseful(next_arg_pulled)'] += 1
                                continue

                            if not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree):
                                rejection_stats['not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree)'] += 1
                                continue

                            if not is_formula_new(next_arg_pulled.conclusion, formulas_in_tree):
                                # if next_arg_pulled.id.startswith('negation_intro.pred_only'):  # HONOKA
                                #     import pudb; pudb.set_trace()
                                rejection_stats['not _is_formula_new(next_arg_pulled.conclusion, formulas_in_tree)'] += 1
                                continue

                            other_premises = [premise for premise in next_arg_pulled.premises
                                              if premise.rep != cur_conclusion.rep]
                            if not _is_formulas_new(other_premises, formulas_in_tree):
                                # If any of other premises already exists in the tree, it will lead to a loop.
                                # We want to avoid a loop.
                                rejection_stats['not _is_formulas_new(other_premises, formulas_in_tree)'] += 1
                                continue

                            if not is_consistent_formula_set(other_premises + leaf_formulas_in_tree):
                                # other_premises can be the leaf of the tree.
                                # We reject tree with inconsistent formulas.
                                # Such tree is formally allowed, but we think the inconsistent leafs are not senseful in natural language.
                                # Notice that we stil allow inconsistency between non-leaf nodes
                                rejection_stats['is_consistent_formula_set(other_premises + leaf_formulas_in_tree)'] += 1
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
                        for cur_assumption_node in cur_possible_assumption_nodes:
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

            if disallow_contradiction_as_hypothesis and proof_tree.root_node.formula.rep == CONTRADICTION:
                raise ProofTreeGenerationFailure(f'Contradiction {CONTRADICTION} as the hypothesis is disallowed.')

            _check_leaf_consistency(proof_tree)

            return proof_tree

    raise Exception('Unexpected')


def _extend_branches(proof_tree: ProofTree,
                     arguments: List[Argument],
                     num_steps: int,
                     predicate_pool: List[str],
                     constant_pool: List[str],
                     argument_weights: Optional[Dict[Argument, float]] = None,
                     depth_limit: Optional[int] = None,
                     elim_dneg=False,
                     allow_reference_arguments_when_depth_1=True) -> ProofTree:
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
        leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]

        leaf_nodes = [
            node for node in proof_tree.leaf_nodes
            if node.assump_parent is None  # assumptions shoud keep beeing leaf
        ]
        if depth_limit is not None:
            leaf_nodes = [node for node in leaf_nodes
                          if proof_tree.get_node_depth(node) < depth_limit]
        if len(leaf_nodes) == 0:
            logger.warning('Couldn\'t extend branch since the tree have no leaf nodes under depth limit %d.', depth_limit)
            _check_leaf_consistency(proof_tree)
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
            chainable_args = [
                arg for arg in arguments
                if formula_is_identical_to(arg.conclusion, leaf_node.formula)
                and len(arg.assumptions) == 0  # by it's logic, the argument with premise assumptions can not be applied in branch extension
            ]
            if len(chainable_args) == 0:
                rejection_stats['len(chainable_args) == 0'] += 1

            for next_arg in _shuffle_arguments(chainable_args, weights=argument_weights):
                if next_arg.id.startswith('reference') and (depth_limit != 1 or not allow_reference_arguments_when_depth_1):
                    continue

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
                        shuffle=True,
                ):
                    if is_leaf_node_done:
                        break

                    conclusion_pulled = interpret_formula(next_arg.conclusion, conclusion_mapping, elim_dneg=elim_dneg)
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
                        shuffle=True,
                    ):
                        next_arg_pulled = interpret_argument(next_arg, mapping, elim_dneg=elim_dneg)

                        if not is_argument_senseful(next_arg_pulled):
                            rejection_stats['is_argument_nonsense(next_arg_pulled)'] += 1
                            continue

                        if not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree):
                            rejection_stats['not is_ok_formula_set(next_arg_pulled.all_formulas + formulas_in_tree)'] += 1
                            continue

                        if not is_consistent_formula_set(next_arg_pulled.premises + leaf_formulas_in_tree):
                            # We reject tree with inconsistent leaf nodes.
                            # Such tree is formally allowed, but we think the inconsistent leafs are not senseful in natural language.
                            # Notice that we stil allow inconsistency between non-leaf nodes
                            rejection_stats['is_consistent_formula_set(other_premises + leaf_formulas_in_tree)'] += 1
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
                '_extend_branches() failed. The statistics are the followings:',
                f'leaf_node:    {leaf_node}',

                'log trace:        :',
                log_traces_msg,

                'rejection stats   :',
                rejection_stats_msg,

            ])
            raise ProofTreeGenerationFailure(msg)

    _check_leaf_consistency(proof_tree)
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
    return all((is_formula_new(formula, existing_formulas)
                for formula in formulas))


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


def _check_leaf_consistency(proof_tree: ProofTree) -> None:
    # We have checked the consistency of the leaf nodes at each step, thus, the leaf nodes must be consistent at the end.
    assert is_consistent_formula_set([node.formula for node in proof_tree.leaf_nodes])


def load_arguments(config_paths: List[str]) -> List[Argument]:
    arguments = []
    for config_path in config_paths:
        arguments.extend([Argument.from_json(json_obj)
                          for json_obj in json.load(open(config_path))
                          if not json_obj['id'].startswith('__')])
    return arguments


def build(config_paths: List[str],
          elim_dneg=False,
          complication=0.0,
          quantification=0.0):
    arguments = load_arguments(config_paths)
    generator = ProofTreeGenerator(
        arguments,
        elim_dneg=elim_dneg,
        complicated_arguments_weight=complication,
        quantifier_axiom_arguments_weight=quantification,
    )
    return generator
