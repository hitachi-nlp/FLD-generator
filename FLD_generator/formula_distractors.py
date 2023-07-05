from typing import List, Any, Iterable, Tuple, Dict
from abc import abstractmethod, ABC
from pprint import pprint
import random
import math
from collections import defaultdict

import logging
from typing import Optional
from .proof import ProofTree, ProofNode
from .formula import Formula, PREDICATES, CONSTANTS, negate, ContradictionNegationError, IMPLICATION
from .utils import shuffle
from .interpretation import (
    generate_mappings_from_predicates_and_constants,
    interpret_formula,
    eliminate_double_negation,
    formula_is_identical_to,
    generate_simplified_formulas,
)
from .formula_checkers import (
    is_consistent_set as is_consistent_formula_set,
    is_stronger,
    is_equiv,
    is_new as is_formula_new,
    is_trivial as is_formula_trivial,
    is_predicate_arity_consistent_set as is_predicate_arity_consistent_formula_set,
    is_stronger,
)
from FLD_generator.utils import provable_from_incomplete_facts, is_consistent_formula_set_with_logs, have_smaller_proofs_with_logs
from .proof_tree_generators import ProofTreeGenerator
from .exception import FormalLogicExceptionBase
from .proof_tree_generators import ExtendBranchesFailure, ExtendBranchesImpossible
from FLD_generator.utils import run_with_timeout_retry, RetryAndTimeoutFailure, make_pretty_msg
import line_profiling


logger = logging.getLogger(__name__)


class FormulaDistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class FormulaDistractorGenerationImpossible(FormalLogicExceptionBase):
    pass


class FormulaDistractor(ABC):

    @profile
    def generate(self,
                 proof_tree: ProofTree,
                 size: int,
                 existing_distractors: Optional[List[Formula]] = None,
                 allow_inconsistency=False,
                 allow_smaller_proofs=False,
                 max_retry: Optional[int] = None,
                 timeout_per_trial: Optional[int] = None,
                 best_effort=False,
                 no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        max_retry = max_retry or self.default_max_retry
        timeout_per_trial = timeout_per_trial or self.default_timeout_per_trial

        self._log(logging.INFO, f'try to generate {size} distractors', boundary_level=2)

        try:
            trial_results = run_with_timeout_retry(
                self._generate,
                func_args=[proof_tree, size],
                func_kwargs={
                    'no_warning': no_warning,
                    'existing_distractors': existing_distractors,
                    'allow_inconsistency': allow_inconsistency,
                    'allow_smaller_proofs': allow_smaller_proofs,
                    'best_effort': best_effort,
                },

                should_retry_func=lambda distractor_formulas_stats: len(distractor_formulas_stats[0]) < size,
                should_retry_exception=FormulaDistractorGenerationFailure,
                best_effort=best_effort,

                max_retry=max_retry,
                timeout_per_trial=timeout_per_trial,

                logger=logger,
                log_title='_generate()',
            )

        except RetryAndTimeoutFailure as e:
            raise FormulaDistractorGenerationFailure(str(e))

        if len(trial_results) == 0:
            formula_distractors, stats = [], {}
        else:
            best_result = sorted(
                trial_results,
                key = lambda formula_distractors_stats: len(formula_distractors_stats[0])
            )[-1]
            formula_distractors, stats = best_result

        self._validate_results(formula_distractors, size, best_effort=best_effort, no_warning=no_warning)

        return formula_distractors, stats

    @property
    @abstractmethod
    def default_max_retry(self) -> int:
        pass

    @property
    @abstractmethod
    def default_timeout_per_trial(self) -> int:
        pass

    @abstractmethod
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        pass

    def _log(self, log_level, msg: str, boundary_level = 1):
        msg = make_pretty_msg(title=self.__class__.__name__, msg=msg, boundary_level=boundary_level)

        if log_level in ['info', logging.INFO]:
            logger.info(msg)
        elif log_level in ['warning', logging.WARNING]:
            logger.warning(msg)
        else:
            raise NotImplementedError()

    def _validate_results(self, distractor_formulas: List[Formula], size, best_effort=False, no_warning=False) -> None:
        if len(distractor_formulas) < size:
            msg = self._insufficient_msg(distractor_formulas, size)
            if not best_effort:
                raise FormulaDistractorGenerationFailure(msg)
            elif not no_warning:
                self._log(logging.INFO, msg, boundary_level=2)

    def _insufficient_msg(self, distractors: List[Formula], size: int) -> str:
        return f'({self.__class__.__name__}) could not generate {size} distractors. return only {len(distractors)} distractors.'


@profile
def _new_distractor_formula_is_ok(new_distractor: Formula,
                                  existing_distractors: List[Formula],
                                  proof_tree: ProofTree,
                                  allow_inconsistency=False,
                                  allow_smaller_proofs=False) -> bool:

    formulas_in_tree = [node.formula for node in proof_tree.nodes]
    leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]
    hypothesis_formula = proof_tree.root_node.formula

    if is_formula_trivial(new_distractor):
        return False

    if not is_predicate_arity_consistent_formula_set(formulas_in_tree + existing_distractors + [new_distractor]):
        return False

    if not is_formula_new(formulas_in_tree + existing_distractors, new_distractor):
        return False

    intermediate_constant_reps = {constant.rep for constant in proof_tree.intermediate_constants}
    for distractor_constant in new_distractor.constants:
        if distractor_constant.rep in intermediate_constant_reps:
            return False

    if not allow_inconsistency:
        _is_consistent, logs = is_consistent_formula_set_with_logs(
            leaf_formulas_in_tree,
            existing_distractors + [new_distractor],
            [],
        )
        if not _is_consistent:
            logger.info('reject the new distractor because the formulas are inconsistent')
            for msg in logs:
                logger.info(msg)
            return False

    # if not allow_smaller_proofs and not tree_have_contradiction_arg:
    if not allow_smaller_proofs:
        _have_smaller_proofs, logs = have_smaller_proofs_with_logs(
            leaf_formulas_in_tree,
            [],
            [],
            hypothesis_formula,
            hypothesis_formula,
            distractor_formulas=existing_distractors + [new_distractor],
        )
        if _have_smaller_proofs:
            logger.info('reject the new distractor because we have smaller proofs')
            for log in logs:
                logger.info(log)
            return False

    return True


class VariousFormUnkownInterprandsDistractor(FormulaDistractor):
    """
    Unlike SameFormUnkownInterprandsDistractor:
    (i) we sample the formula prototypes not from the tree but from all possible prototypes specified by the user.
        we think this is more appropriate.
    (ii) we sample predicates and constants from the tree, rather than a sampled leaf formula.
    (iii) we reject distractor formula all the PASs of which are the used ones.

    (ii) and (iii) makes distractors more "safe", i.e., fewer chance of having multiple proofs due to the new formulas.
    However, this makes distractors less distractive, of course.

    We are confident that (i) is better.
    We are not that confident about (ii) and (iii) since it makes less distractive.
    """

    def __init__(self,
                 prototype_formulas: Optional[List[Formula]] = None,
                 sample_hard_negatives=False,
                 sample_only_unused_interprands=False,
                 use_simplified_formulas_as_prototype=False,
                 **kwargs):
        super().__init__(**kwargs)
        self._prototype_formulas = prototype_formulas
        self._sample_hard_negatives = sample_hard_negatives
        self._sample_only_unused_interprands = sample_only_unused_interprands

        self._use_simplified_formulas_as_prototype = use_simplified_formulas_as_prototype
        if self._use_simplified_formulas_as_prototype:
            self._simplify_distractor = SimplifiedFormulaDistractor()
        else:
            self._simplify_distractor = None

    @property
    def default_max_retry(self) -> int:
        return 5

    @property
    def default_timeout_per_trial(self) -> int:
        return 10

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        existing_distractors = existing_distractors or []
        if no_warning:
            raise NotImplementedError()

        if size == 0:
            return [], {}

        formulas_in_tree = [node.formula for node in proof_tree.nodes]

        used_PASs = {PAS.rep
                     for formula in formulas_in_tree
                     for PAS in formula.PASs}
        used_pairs = {(PAS.predicates[0].rep, PAS.constants[0].rep)
                      for formula in formulas_in_tree
                      for PAS in formula.PASs
                      if len(PAS.constants) > 0}

        used_predicates = {pred.rep
                           for formula in formulas_in_tree
                           for pred in formula.predicates}
        used_constants = {constant.rep
                          for formula in formulas_in_tree
                          for constant in formula.constants}

        unused_predicates = set(PREDICATES) - set(used_predicates)
        unused_constants = set(CONSTANTS) - set(used_constants)

        if self._prototype_formulas is not None:
            prototype_formulas = self._prototype_formulas

            self._log(logging.INFO, f'sample from {len(prototype_formulas)} prototype formulas specified by the user')
        else:
            prototype_formulas = [node.formula for node in proof_tree.nodes]
            if self._use_simplified_formulas_as_prototype:
                simplified_formulas = self._simplify_distractor.generate(
                    proof_tree,
                    99,
                    existing_distractors=existing_distractors,
                    allow_inconsistency=allow_inconsistency,
                    allow_smaller_proofs=allow_smaller_proofs,
                    best_effort=True,
                    no_warning=True,
                )[0]
                prototype_formulas.extend(simplified_formulas)
                # print('!!!')
                # print(simplified_formulas)
            self._log(logging.INFO, f'sample from len(prototype_formulas) prototype formulas found in the tree')

        # FIXME: this is logic only works for trees where the predicate arity is the same for all the formulas.
        num_zeroary_predicates = len({zeroary_predicate.rep
                                     for formula in formulas_in_tree
                                     for zeroary_predicate in formula.zeroary_predicates})
        num_unary_predicates = len({unary_predicate.rep
                                   for formula in formulas_in_tree
                                   for unary_predicate in formula.unary_predicates})
        if num_zeroary_predicates != 0 and num_unary_predicates != 0:
            raise NotImplementedError()

        if num_zeroary_predicates > 0:
            tree_predicate_type = 'zeroary'
        elif num_unary_predicates > 0:
            tree_predicate_type = 'unary'

        def sample_arity_typed_formula():
            # sample a formula the predicate arity of which is consistent of formulas in tree for speedup.
            while True:
                src_formula = random.sample(prototype_formulas, 1)[0]
                if tree_predicate_type == 'zeroary':
                    if len(src_formula.zeroary_predicates) >= len(src_formula.unary_predicates):
                        return src_formula
                elif tree_predicate_type == 'unary':
                    if len(src_formula.zeroary_predicates) <= len(src_formula.unary_predicates):
                        return src_formula
                elif tree_predicate_type == 'unknown':
                    return src_formula
                else:
                    raise ValueError()

        distractor_formulas: List[Formula] = []

        trial = 0
        max_trial = size * 10
        for trial in range(max_trial):
            if trial >= max_trial:
                break

            if len(distractor_formulas) >= size:
                break

            src_formula = sample_arity_typed_formula()
            num_predicate = len(src_formula.predicates)
            num_constant = len(src_formula.constants)

            def _sample_at_most(elems: Iterable[Any], num: int) -> List[Any]:
                return random.sample(elems, min(num, len(elems)))

            # mix unsed predicates constants a little

            used_pairs_shuffle = shuffle(used_pairs)
            used_paired_predicates_samples: List[str] = []
            used_paired_constants_samples: List[str] = []
            for used_pair in used_pairs_shuffle:
                if len(used_paired_predicates_samples) >= num_predicate\
                        and len(used_paired_constants_samples) >= num_constant:
                    break
                used_pair_predicate, used_pair_constant = used_pair
                if used_pair_predicate not in used_paired_predicates_samples:
                    used_paired_predicates_samples.append(used_pair_predicate)
                if used_pair_constant not in used_paired_constants_samples:
                    used_paired_constants_samples.append(used_pair_constant)

            used_predicates_samples = _sample_at_most(used_predicates, num_constant)
            used_constants_samples = _sample_at_most(used_constants, num_constant)

            unused_predicates_samples = _sample_at_most(unused_predicates, num_predicate)
            unused_constants_samples = _sample_at_most(unused_constants, num_predicate)

            used_unused_predicates_samples = shuffle(used_predicates_samples + unused_predicates_samples)
            used_unused_constants_samples = shuffle(used_constants_samples + unused_constants_samples)

            intermediate_constant_reps = {constant.rep for constant in proof_tree.intermediate_constants}

            def remove_intermediate_constants(constants: List[Formula]) -> List[Formula]:
                return [constant for constant in constants if constant not in intermediate_constant_reps]

            tgt_space = []
            if not self._sample_only_unused_interprands:
                if self._sample_hard_negatives:
                    # It is possible that (used_predicates, used_constants) pair produces a new formula,
                    # e.g., "{B}{b} -> {A}{a}" when src_formula is "{A}{a} -> {B}{b}"
                    # We guess, however, that such transoformation leads to many inconsistent or not senseful formula set, as the above.
                    # thus here, we make it as optional.
                    tgt_space.extend([
                        (used_paired_predicates_samples, remove_intermediate_constants(used_paired_constants_samples)),
                        (used_predicates_samples, remove_intermediate_constants(used_constants_samples)),
                    ])
                if trial % 2 == 0:
                    tgt_space.extend([
                        (used_predicates_samples, remove_intermediate_constants(used_unused_constants_samples)),
                        (used_unused_predicates_samples, remove_intermediate_constants(used_unused_constants_samples)),
                    ])
                else:
                    tgt_space.extend([
                        (used_unused_predicates_samples, remove_intermediate_constants(used_constants_samples)),
                        (used_unused_predicates_samples, remove_intermediate_constants(used_unused_constants_samples)),
                    ])
            tgt_space.extend([
                (unused_predicates_samples, remove_intermediate_constants(unused_constants_samples))
            ])

            is_found = False
            found_formula = None
            for tgt_predicates, tgt_constants in tgt_space:
                for mapping in generate_mappings_from_predicates_and_constants(
                    [p.rep for p in src_formula.predicates],
                    [c.rep for c in src_formula.constants],
                    tgt_predicates,
                    tgt_constants,
                    shuffle=True,
                    allow_many_to_one=False,
                ):
                    distractor_formula = interpret_formula(src_formula, mapping, elim_dneg=True)

                    if all(distractor_PAS.rep in used_PASs
                           for distractor_PAS in distractor_formula.PASs):
                        # if all the distractor PASs are in tree,
                        # we have high chance of (i) producing nonsens formula set (ii) producing multiple proof trees.
                        # we want to prevent such possiblity.
                        continue

                    if not _new_distractor_formula_is_ok(distractor_formula,
                                                         distractor_formulas + existing_distractors,
                                                         proof_tree,
                                                         allow_inconsistency=allow_inconsistency,
                                                         allow_smaller_proofs=allow_smaller_proofs):
                        continue

                    found_formula = distractor_formula
                    is_found = True
                    break
                if is_found:
                    break

            if is_found:
                distractor_formulas.append(found_formula)

        return distractor_formulas, {}


class SimplifiedFormulaDistractor(FormulaDistractor):

    @property
    def default_max_retry(self) -> int:
        # this class is deterministic and thus, only 1 trial is enough.
        return 1

    @property
    def default_timeout_per_trial(self) -> int:
        return 10

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        existing_distractors = existing_distractors or []
        if size == 0:
            return [], {}

        simplified_formulas: List[Formula] = []
        for node in proof_tree.nodes:
            for simplified_formula in generate_simplified_formulas(node.formula, elim_dneg=True):
                if not any(simplified_formula.rep == existing_simplified_formula
                           for existing_simplified_formula in simplified_formulas):
                    simplified_formulas.append(simplified_formula)

        distractor_formulas: List[Formula] = []
        for distractor_formula in random.sample(simplified_formulas, len(simplified_formulas)):
            if len(distractor_formulas) >= size:
                break

            # SLOW
            # if any(is_stronger(distractor_formula, leaf_node.formula) for leaf_node in proof_tree.leaf_nodes):
            #     continue

            if not _new_distractor_formula_is_ok(distractor_formula,
                                                 distractor_formulas + existing_distractors,
                                                 proof_tree,
                                                 allow_inconsistency=allow_inconsistency,
                                                 allow_smaller_proofs=allow_smaller_proofs):
                continue

            distractor_formulas.append(distractor_formula)

        return distractor_formulas, {}


class NegativeTreeDistractor(FormulaDistractor):
    """ Generate sentences which are the partial facts to derive negative of hypothesis.

    At least one leaf formula is excluded to make the tree incomplete.
    """

    def __init__(self,
                 generator: ProofTreeGenerator,
                 prototype_formulas: Optional[List[Formula]] = None,
                 negative_tree_negated_hypothesis_ratio=0.5,
                 **kwargs):
        super().__init__(**kwargs)

        if generator.complex_formula_arguments_weight < 0.01:
            raise ValueError('Generator with too small "complex_formula_arguments_weight" will lead to generation failure, since we try to generate a tree with negated hypothesis, which is only in the complicated arguments.')
        self.generator = generator
        self._various_form_distractor = VariousFormUnkownInterprandsDistractor(
            prototype_formulas=prototype_formulas,
            # sample_only_unused_interprands=True,
            sample_only_unused_interprands=False,
        )
        self.negative_tree_negated_hypothesis_ratio = negative_tree_negated_hypothesis_ratio
        self._initial_sampling = 'negated_hypothesis'

    @property
    def default_max_retry(self) -> int:
        return 5

    @property
    def default_timeout_per_trial(self) -> int:
        return 10

    @profile
    def generate(self, *args, **kwargs) -> Tuple[List[Formula], Dict[str, Any]]:
        # setting here is neccessary due to the following reason:
        # (i) if we switch initial_sampling in _generate(),
        #     the run_with_timeout_retry() in generate() will have multiple results from different initial_sampling method
        # (ii) However, the final result will provably taken from "various_form" because it tend to have the largest number of distractors.
        # (iii) (ii) contradicts to hour hope that various initial_sampling should be used
        if random.random() < self.negative_tree_negated_hypothesis_ratio:
            self._initial_sampling = 'negated_hypothesis'
        else:
            self._initial_sampling = 'various_form'
        return super().generate(*args, **kwargs)

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        existing_distractors = existing_distractors or []
        if no_warning:
            raise NotImplementedError()
        return self._generate_with_initial_sampling(proof_tree,
                                                    size,
                                                    self._initial_sampling,
                                                    existing_distractors=existing_distractors,
                                                    allow_inconsistency=allow_inconsistency,
                                                    allow_smaller_proofs=allow_smaller_proofs)

    @profile
    def _generate_with_initial_sampling(self,
                                        proof_tree: ProofTree,
                                        size: int,
                                        initial_sampling: str,
                                        allow_inconsistency=False,
                                        allow_smaller_proofs=False,
                                        existing_distractors: Optional[List[Formula]] = None) -> Tuple[List[Formula], Dict[str, Any]]:

        existing_distractors = existing_distractors or []
        if size == 0:
            return [], {'negative_tree': None, 'negative_tree_missing_nodes': None}

        n_trial = 0
        max_trial = 1  # max_trial >= 2 is too slow, thus we decided not to try multiple times
        while True:
            # gradually increase the number of extension steps to find the "just in" size tree.
            branch_extension_steps = size + (n_trial + 1) * 5
            self._log(logging.INFO, f'trial={n_trial}  branch_extension_steps={branch_extension_steps}')

            if initial_sampling == 'negated_hypothesis':
                try:
                    negative_tree_root_formula = negate(proof_tree.root_node.formula)
                except ContradictionNegationError as e:
                    raise Exception(str(e))
            elif initial_sampling == 'various_form':
                try:
                    various_fomulas, _ = self._various_form_distractor.generate(
                        proof_tree,
                        1,
                        existing_distractors=existing_distractors,
                        allow_inconsistency=allow_inconsistency,
                        allow_smaller_proofs=allow_smaller_proofs,
                        best_effort=False,
                    )
                    negative_tree_root_formula = various_fomulas[0]
                except FormulaDistractorGenerationFailure as e:
                    raise FormulaDistractorGenerationFailure(f'could not generate the root node of the negative tree by VariousFormUnkownInterprandsDistractor(). The original message is the following:\n{str(e)}')
            else:
                raise ValueError(f'Unsupported initial_sampling method "{initial_sampling}"')

            if self.generator.elim_dneg:
                negative_tree_root_formula = eliminate_double_negation(negative_tree_root_formula)

            negative_tree = ProofTree([ProofNode(negative_tree_root_formula)])

            try:
                negative_tree, _ = self.generator.extend_branches(
                    negative_tree,
                    branch_extension_steps,
                    ng_formulas=[node.formula for node in proof_tree.nodes],
                    max_retry=10,   # HONOKA: this value determines the total speed.
                    best_effort=True,
                    force_fix_illegal_intermediate_constants=True,
                )
            except ExtendBranchesFailure as e:
                raise FormulaDistractorGenerationFailure(str(e))
            except ExtendBranchesImpossible as e:
                raise FormulaDistractorGenerationImpossible(str(e))

            n_trial += 1
            negative_leaf_nodes = negative_tree.leaf_nodes
            if n_trial < max_trial and len(negative_leaf_nodes) - 1 < size:
                self._log(logging.INFO, f'continue to the next trial with increased branch_extension_steps, since number of negatieve leaf formulas - 1 = {len(negative_leaf_nodes) - 1} < size={size}')
                continue

            distractor_formulas: List[Formula] = []
            distractor_nodes: List[ProofNode] = []
            # We sample at most len(leaf_nodes) - 1, since at least one distractor must be excluded so that the negated hypothesis can not be derived.
            if initial_sampling == 'negated_hypothesis':
                leaf_node_at_most = len(negative_leaf_nodes) - 1  # should exclude at least one
            elif initial_sampling == 'various_form':
                leaf_node_at_most = len(negative_leaf_nodes)

            for distractor_node in random.sample(negative_leaf_nodes, leaf_node_at_most):
                distractor_formula = distractor_node.formula

                if len(distractor_formulas) >= size:
                    break

                if not _new_distractor_formula_is_ok(distractor_formula,
                                                     distractor_formulas + existing_distractors,
                                                     proof_tree,
                                                     allow_inconsistency=allow_inconsistency,
                                                     allow_smaller_proofs=allow_smaller_proofs):
                    continue

                distractor_formulas.append(distractor_formula)
                distractor_nodes.append(distractor_node)

            if negative_tree is not None:
                self._log(logging.INFO, f'The negative tree is the following:\n{negative_tree.format_str}', boundary_level=2)

            # logger.fatal('%d %d', size, len(distractor_formulas))
            return distractor_formulas, {'negative_tree': negative_tree, 'negative_tree_missing_nodes': [node for node in negative_tree.leaf_nodes if node not in distractor_nodes]}


class MixtureDistractor(FormulaDistractor):

    def __init__(self, distractors: List[FormulaDistractor], **kwargs):
        super().__init__(**kwargs)
        self._distractors = distractors
        self.distractors_max_enum = 3

    @property
    def default_max_retry(self) -> int:
        return 1

    @property
    def default_timeout_per_trial(self) -> int:
        timeout_sum = 0
        for distractor in self._distractors:
            timeout_sum += distractor.default_max_retry * distractor.default_timeout_per_trial * self.distractors_max_enum
        return timeout_sum

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        existing_distractors = existing_distractors or []
        if no_warning:
            raise NotImplementedError()

        if size == 0:
            return [], {}

        distractor_formulas = []
        others = defaultdict(list)
        remaining_size = size
        for enum in range(self.distractors_max_enum):
            for i_distrator, distractor in enumerate(random.sample(self._distractors, len(self._distractors))):
                if remaining_size <= 0:
                    break

                if i_distrator == len(self._distractors) - 1:
                    _size = remaining_size
                else:
                    _size = random.randint(1, remaining_size)

                try:
                    _distractor_formulas, _others = distractor.generate(proof_tree,
                                                                        _size,
                                                                        existing_distractors = existing_distractors + distractor_formulas,
                                                                        allow_inconsistency=allow_inconsistency,
                                                                        allow_smaller_proofs=allow_smaller_proofs,
                                                                        best_effort=best_effort)

                    distractor_formulas += _distractor_formulas
                    remaining_size -= len(_distractor_formulas)

                    for _other_key, _other_val in _others.items():
                        others[f'mixture_list.{_other_key}'].append(_other_val)

                except (FormulaDistractorGenerationFailure, FormulaDistractorGenerationImpossible) as e:
                    self._log(logging.INFO, f'sub distractor "{str(distractor)}" failed in generating distractors with the following message:' + '\n' + f'{str(e)}')

        return distractor_formulas, others


class FallBackDistractor(FormulaDistractor):

    def __init__(self, distractors: List[FormulaDistractor], **kwargs):
        super().__init__(**kwargs)
        self._distractors = distractors

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout_per_trial(self) -> int:
        timeout_sum = 0
        for distractor in self._distractors:
            timeout_sum += distractor.default_max_retry * distractor.default_timeout_per_trial
        return timeout_sum

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  existing_distractors: Optional[List[Formula]] = None,
                  allow_inconsistency=False,
                  allow_smaller_proofs=False,
                  best_effort=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        existing_distractors = existing_distractors or []
        if no_warning:
            raise NotImplementedError()

        if size == 0:
            return [], {}

        others = {}
        distractor_formulas: List[Formula] = []
        for distractor in self._distractors:
            if len(distractor_formulas) >= size:
                break
            try:
                _distractor_formulas, _others = distractor.generate(proof_tree,
                                                                    size,
                                                                    existing_distractors = existing_distractors + distractor_formulas,
                                                                    allow_inconsistency=allow_inconsistency,
                                                                    allow_smaller_proofs=allow_smaller_proofs,
                                                                    best_effort=best_effort)

                distractor_formulas += _distractor_formulas

                for _other_key, _other_val in _others.items():
                    if _other_key in others:
                        raise ValueError(f'Duplicated other key {_other_key}')
                    others[_other_key] = _other_val

            except (FormulaDistractorGenerationFailure, FormulaDistractorGenerationImpossible) as e:
                self._log(logging.WARNING, 'generating distractors failed with the following message:\n' + f'{str(e)}')

        return distractor_formulas[:size], others


def build(type_: str,
          generator: Optional[ProofTreeGenerator] = None,
          sample_hard_negatives=True,
          disallow_simplified_formulas_as_prototype=False,
          sample_prototype_formulas_from_all_possible_formulas=False,
          negative_tree_negated_hypothesis_ratio=0.5,
          **kwargs):

    # logger.fatal('--------------------- build_distractor -----------------------------')
    # logger.info(type_)
    # logger.info(sample_hard_negatives)
    # logger.info(disallow_simplified_formulas_as_prototype)
    # logger.info(sample_prototype_formulas_from_all_possible_formulas)
    # logger.info(negative_tree_negated_hypothesis_ratio)
    # from pprint import pformat
    # logger.info(pformat(kwargs))

    use_simplified_formulas_as_prototype = not disallow_simplified_formulas_as_prototype

    prototype_formulas: Optional[List[Formula]] = None
    if type_.find('various_form') >= 0 and sample_prototype_formulas_from_all_possible_formulas:
        if generator is not None:
            prototype_formulas = []
            logger.info(make_pretty_msg(title='build distractor',
                                        status='start',
                                        msg='collecting prototype formulas from arguments to build the distractor ...', boundary_level=0))
            for argument in generator.arguments:
                for formula in argument.all_formulas:
                    if all(not formula_is_identical_to(formula, existent_formula)
                           for existent_formula in prototype_formulas):
                        prototype_formulas.append(formula)
            logger.info(make_pretty_msg(title='build distractor',
                                        status='finish',
                                        msg='collecting prototype formulas from arguments to build the distractor', boundary_level=0))

        else:
            logger.warning(make_pretty_msg(title='build distractor',
                                           msg='generator is not specified. Thus, the VariousFormUnkownInterprandsDistractor will use formulas in tree as prototype formulas.', boundary_level=0))

    if type_ == 'various_form':
        return VariousFormUnkownInterprandsDistractor(
            prototype_formulas=prototype_formulas,
            sample_hard_negatives=sample_hard_negatives,
            use_simplified_formulas_as_prototype=use_simplified_formulas_as_prototype,
            **kwargs,
        )
    elif type_ == 'negative_tree':
        if generator is None:
            raise ValueError()
        return NegativeTreeDistractor(
            generator,
            prototype_formulas=prototype_formulas,
            negative_tree_negated_hypothesis_ratio=negative_tree_negated_hypothesis_ratio,
            **kwargs,
        )

    elif type_ == 'fallback.negative_tree.various_form':
        return FallBackDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=negative_tree_negated_hypothesis_ratio,
                    **kwargs,
                ),
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                    use_simplified_formulas_as_prototype=use_simplified_formulas_as_prototype,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'fallback.various_form.negative_tree':
        return FallBackDistractor(
            [
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                    use_simplified_formulas_as_prototype=use_simplified_formulas_as_prototype,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=negative_tree_negated_hypothesis_ratio,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'mixture.negative_tree.simplified_formula.various_form':
        return MixtureDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=negative_tree_negated_hypothesis_ratio,
                    **kwargs,
                ),
                SimplifiedFormulaDistractor(**kwargs,),
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                    use_simplified_formulas_as_prototype=use_simplified_formulas_as_prototype,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'mixture.negative_tree_double':
        return MixtureDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=1.0,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'mixture.negative_tree_triple':
        return MixtureDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=1.0,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'mixture.negative_tree_quadruple':
        return MixtureDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=1.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=1.0,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'mixture.negative_tree_double.simplified_formula.various_form':
        return MixtureDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=1.0,
                    **kwargs,
                ),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    negative_tree_negated_hypothesis_ratio=0.0,
                    **kwargs,
                ),
                SimplifiedFormulaDistractor(**kwargs,),
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                    use_simplified_formulas_as_prototype=use_simplified_formulas_as_prototype,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    else:
        raise ValueError(f'Unknown distractor type {type_}')
