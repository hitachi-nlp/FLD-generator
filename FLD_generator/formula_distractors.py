from typing import List, Any, Iterable, Tuple, Dict
from abc import abstractmethod, ABC
from pprint import pprint
import random
import math

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
    is_ok_set as is_ok_formula_set,
    is_senseful,
    is_consistent_set as is_consistent_formula_set,
    is_consistent_set_z3 as is_consistent_formula_set_z3,
    is_stronger_z3,
    is_equiv_z3,
    is_new as is_formula_new,
)
from .formula_checkers.z3_checkers import is_tautology, is_contradiction
from FLD_generator.utils import provable_from_incomplete_facts
from .proof_tree_generators import ProofTreeGenerator
from .exception import FormalLogicExceptionBase
from .proof_tree_generators import ProofTreeGenerationFailure, ProofTreeGenerationImpossible
from FLD_generator.utils import run_with_timeout_retry, RetryAndTimeoutFailure, make_pretty_msg
import kern_profiler


logger = logging.getLogger(__name__)


class FormulaDistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class FormulaDistractor(ABC):

    def generate(self,
                 proof_tree: ProofTree,
                 size: int,
                 formulas_to_be_sat: Optional[List[Formula]] = None,
                 allow_smaller_proofs=False,
                 max_retry: Optional[int] = None,
                 timeout: Optional[int] = None,
                 no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        max_retry = max_retry or self.default_max_retry
        timeout = timeout or self.default_timeout
        try:
            self._log(logging.INFO, f'try to generate {size} distractors', boundary_level=2)

            formula_distractors, stats = run_with_timeout_retry(
                self._generate,
                func_args=[proof_tree, size],
                func_kwargs={
                    'no_warning': no_warning,
                    'formulas_to_be_sat': formulas_to_be_sat,
                    'allow_smaller_proofs': allow_smaller_proofs,
                },
                retry_exception_class=FormulaDistractorGenerationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='_generate()',
            )

            if not no_warning and len(formula_distractors) < size:
                self._log(logging.WARNING, f'could not generate {size} distractors. return only {len(formula_distractors)} distractors.', boundary_level=2)

            return formula_distractors, stats
        except RetryAndTimeoutFailure as e:
            raise FormulaDistractorGenerationFailure(str(e))

    @property
    @abstractmethod
    def default_max_retry(self) -> int:
        pass

    @property
    @abstractmethod
    def default_timeout(self) -> int:
        pass

    @abstractmethod
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
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


@profile
def _new_distractor_formula_is_ok(new_distractor: Formula,
                                  existing_distractors: List[Formula],
                                  proof_tree: ProofTree,
                                  allow_smaller_proofs=False) -> bool:

    formulas_in_tree = [node.formula for node in proof_tree.nodes]
    leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]
    hypothesis_formula = proof_tree.root_node.formula

    if is_tautology(new_distractor) or is_contradiction(new_distractor):
        return False

    if not is_formula_new(new_distractor, existing_distractors + formulas_in_tree):
        return False

    if not is_ok_formula_set([new_distractor] + existing_distractors + formulas_in_tree):
        return False

    if not is_consistent_formula_set([new_distractor] + existing_distractors):
        return False

    if not is_consistent_formula_set_z3([new_distractor] + existing_distractors):
        logger.warning('reject new distractor because adding it will make distractors inconsistent')
        for dist in [new_distractor] + existing_distractors:
            logger.info(dist)
        return False

    # The tree will become inconsistent "by adding" distractor formulas.
    original_tree_is_consistent = is_consistent_formula_set(leaf_formulas_in_tree)
    if original_tree_is_consistent and\
            not is_consistent_formula_set([new_distractor] + existing_distractors + leaf_formulas_in_tree):
        return False

    # The tree will become inconsistent "by adding" distractor formulas.
    original_tree_is_consistent = is_consistent_formula_set_z3(leaf_formulas_in_tree)
    if original_tree_is_consistent and\
            not is_consistent_formula_set_z3([new_distractor] + existing_distractors + leaf_formulas_in_tree):
        logger.warning('reject new distractor because adding it will make leaf formulas and distractors inconsistent')
        for dist in [new_distractor] + existing_distractors + leaf_formulas_in_tree:
            logger.info(dist)
        return False

    intermediate_constant_reps = {constant.rep for constant in proof_tree.intermediate_constants}
    for distractor_constant in new_distractor.constants:
        if distractor_constant.rep in intermediate_constant_reps:
            # raise FormulaDistractorGenerationFailure(f'The intermediate_constant {distractor_constant.rep} is in a distractor {str(distractor_constant)}')
            return False

    if not allow_smaller_proofs:
        # -- we think this strength check is just less then the "other proof check" below --
        # for tree_formula in [node.formula for node in proof_tree.nodes]:
        #     if is_stronger_z3(new_distractor, tree_formula) or is_equiv_z3(new_distractor, tree_formula):
        #         logger.warning('reject new distractor %s because it is stronger or equals to a leaf formula %s',
        #                        new_distractor.rep,
        #                        tree_formula.rep)
        #         return False

        # -- other proof check --
        _have_smaller_proofs, droppable_formula = provable_from_incomplete_facts(
            leaf_formulas_in_tree,
            existing_distractors + [new_distractor],
            hypothesis_formula,
        )
        if _have_smaller_proofs:
            logger.warning('reject new distractor because smaller proofs exist')

            logger.info('positive formulas:')
            for formula in leaf_formulas_in_tree:
                logger.info('    ' + formula.rep)

            logger.info('distractor formulas:')
            for formula in existing_distractors + [new_distractor]:
                logger.info('    ' + formula.rep)

            logger.info('droppable formulas:')
            logger.info('    ' + droppable_formula.rep)

            logger.info('hypothesis:')
            logger.info('    ' + hypothesis_formula.rep)

            return False

    return True


class UnkownPASDistractor(FormulaDistractor):

    def __init__(self):
        raise NotImplementedError('not maintained.')

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
        if no_warning:
            raise NotImplementedError()
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]

        used_zeroary_predicates = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.zeroary_predicates
        })
        unused_predicates = shuffle(list(set(PREDICATES) - set(used_zeroary_predicates)))

        num_zeroary_distractors = size
        distractor_zeroary_predicates = unused_predicates[:int(num_zeroary_distractors)]
        zeroary_distractors = [Formula(f'{predicate}') for predicate in distractor_zeroary_predicates]

        used_unary_predicates = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.unary_predicates
        })
        unused_predicates = sorted(set(PREDICATES) - set(used_unary_predicates) - set(distractor_zeroary_predicates))

        used_constants = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.constants
        })
        unused_constants = sorted(set(CONSTANTS) - set(used_constants))

        in_domain_unused_PASs: List[Formula] = []
        for predicate in used_unary_predicates:
            for constant in used_constants:
                fact_rep = f'{predicate}{constant}'

                if all((fact_rep not in formula.rep for formula in leaf_formulas + in_domain_unused_PASs)):
                    in_domain_unused_PASs.append(Formula(fact_rep))

        out_of_domain_unused_PASs = []
        for predicate in unused_predicates:
            for constant in used_constants:
                out_of_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))
        for predicate in used_unary_predicates:
            for constant in unused_constants:
                fact_rep = f'{predicate}{constant}'
                out_of_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))

        in_domain_unused_PASs = shuffle(in_domain_unused_PASs)
        out_of_domain_unused_PASs = shuffle(out_of_domain_unused_PASs)
        num_unary_distractors = size
        unary_distractors = (in_domain_unused_PASs + out_of_domain_unused_PASs)[:int(num_unary_distractors)]

        return shuffle(zeroary_distractors + unary_distractors)[:size], {}

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 9999


class SameFormUnkownInterprandsDistractor(FormulaDistractor):
    """ Generate the same form formula with unknown predicates or constants injected.

    This class is superior to UnkownPASDistractor, which does not consider the similarity of the forms of formulas.
    """

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 9999

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
        if no_warning:
            raise NotImplementedError()
        if size == 0:
            return [], {}

        leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]

        leaf_formulas_in_tree = shuffle(leaf_formulas_in_tree)
        distractor_formulas: List[Formula] = []

        trial = 0
        max_trial = size * 10
        for trial in range(max_trial):
            if trial >= max_trial:
                return distractor_formulas, {}

            if len(distractor_formulas) >= size:
                break

            src_formula = leaf_formulas_in_tree[trial % len(leaf_formulas_in_tree)]

            used_predicates = shuffle(list({pred.rep for pred in src_formula.predicates}))
            used_constants = shuffle(list({pred.rep for pred in src_formula.constants}))

            # use subset of unused predicates and constant so that generate_mappings_from_predicates_and_constants() does not generate too large list
            # * 3 comes from the intuition that a formula may contain 3 predicates or constants on maximum like {A}{a} v {B}{b} -> {C}{c}
            unused_predicates = shuffle(list(set(PREDICATES) - set(used_predicates)))[:size * 3]
            unused_constants = shuffle(list(set(CONSTANTS) - set(used_constants)))[:size * 3]

            # mix unsed predicates constants a little
            used_unused_predicates = shuffle(used_predicates + unused_predicates)
            used_unused_constants = shuffle(used_constants + unused_constants)

            intermediate_constant_reps = {constant.rep for constant in proof_tree.intermediate_constants}

            def remove_intermediate_constants(constants: List[Formula]) -> List[Formula]:
                return [constant for constant in constants if constant not in intermediate_constant_reps]

            # It is possible that (used_predicates, used_constants) pair produces a new formula,
            # e.g., "{B}{b} -> {A}{a}" when src_formula is "{A}{a} -> {B}{b}"
            # We guess, however, that such transoformation leads to many inconsistent or not senseful formula set, as the above.
            # We may still filter out such a formula by some heuristic method, but this is costly.
            # Thus, we decided not ot use used_predicates + used_predicates pair.
            if trial % 3 in [0, 1]:
                # We guess (unused_predicates, used_constants) pair, that produces the formula of the known object plus unknown predicate,
                # is more distractive than the inverse pair.
                # Thus, we sample it more often than the inverseed pair,
                tgt_space = [
                    # (used_predicates, remove_intermediate_constants(used_constants)),
                    (used_unused_predicates, remove_intermediate_constants(used_constants)),
                    (used_unused_predicates, remove_intermediate_constants(used_unused_constants)),
                    (unused_predicates, remove_intermediate_constants(unused_constants)),
                ]
            else:
                tgt_space = [
                    # (used_predicates, remove_intermediate_constants(used_constants)),
                    (used_predicates, remove_intermediate_constants(used_unused_constants)),
                    (used_unused_predicates, remove_intermediate_constants(used_unused_constants)),
                    (unused_predicates, remove_intermediate_constants(unused_constants)),
                ]

            do_print = False
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
                    if do_print:
                        print('\n\n!!!!!!!!!!!!!!!!!!!! loop !!!!!!!!!!!!!!!!!!!!!!!')
                        print(mapping)
                    transformed_formula = interpret_formula(src_formula, mapping, elim_dneg=True)

                    if not _new_distractor_formula_is_ok(transformed_formula,
                                                         distractor_formulas + formulas_to_be_sat,
                                                         proof_tree,
                                                         allow_smaller_proofs=allow_smaller_proofs):
                        continue

                    found_formula = transformed_formula
                    is_found = True
                    break
                if is_found:
                    break

            if is_found:
                distractor_formulas.append(found_formula)

        return distractor_formulas, {}


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
        return 3

    @property
    def default_timeout(self) -> int:
        return 9999

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
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
                simplified_formulas = self._simplify_distractor.generate(proof_tree,
                                                                         9999,
                                                                         formulas_to_be_sat=formulas_to_be_sat,
                                                                         allow_smaller_proofs=allow_smaller_proofs,
                                                                         no_warning=True)[0]
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
                return distractor_formulas, {}

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
                                                         distractor_formulas + formulas_to_be_sat,
                                                         proof_tree,
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
        return 3

    @property
    def default_timeout(self) -> int:
        return 9999

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
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

            if not _new_distractor_formula_is_ok(distractor_formula,
                                                 distractor_formulas + formulas_to_be_sat,
                                                 proof_tree,
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
                 try_negated_hypothesis_first=True,
                 max_branch_extension_steps=10,
                 extend_branches_max_retry: int = 5,
                 **kwargs):
        super().__init__(**kwargs)

        if generator.complicated_arguments_weight < 0.01:
            raise ValueError('Generator with too small "complicated_arguments_weight" will lead to generation failure, since we try to generate a tree with negated hypothesis, which is only in the complicated arguments.')
        self.generator = generator
        self._various_form_distractor = VariousFormUnkownInterprandsDistractor(
            prototype_formulas=prototype_formulas,
            sample_only_unused_interprands=True,
        )
        self.try_negated_hypothesis_first = try_negated_hypothesis_first
        self.max_branch_extension_steps = max_branch_extension_steps
        self.extend_branches_max_retry = extend_branches_max_retry

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 9999

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
        if no_warning:
            raise NotImplementedError()
        if self.try_negated_hypothesis_first:
            distractors, others = self._generate_with_initial_sampling(proof_tree,
                                                                       size,
                                                                       'negated_hypothesis',
                                                                       formulas_to_be_sat=formulas_to_be_sat,
                                                                       allow_smaller_proofs=allow_smaller_proofs)
            if len(distractors) == 0:
                self._log(logging.INFO, 'creating negative tree with negated hypothesis root not failed. Will try root node sampled from various forms.')
                distractors, others = self._generate_with_initial_sampling(proof_tree,
                                                                           size,
                                                                           'various_form',
                                                                           formulas_to_be_sat=formulas_to_be_sat,
                                                                           allow_smaller_proofs=allow_smaller_proofs)
        else:
            distractors, others = self._generate_with_initial_sampling(proof_tree,
                                                                       size,
                                                                       'various_form',
                                                                       formulas_to_be_sat=formulas_to_be_sat,
                                                                       allow_smaller_proofs=allow_smaller_proofs)
        return distractors, others

    @profile
    def _generate_with_initial_sampling(self,
                                        proof_tree: ProofTree,
                                        size: int,
                                        initial_sampling: str,
                                        allow_smaller_proofs=False,
                                        formulas_to_be_sat: Optional[List[Formula]] = None) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
        if size == 0:
            return [], {'negative_tree': None, 'negative_tree_missing_nodes': None}

        n_trial = 0
        while True:
            # gradually increase the number of extension steps to find the "just in" size tree.
            branch_extension_steps = min(size + (n_trial + 1) * 2, self.max_branch_extension_steps)
            self._log(logging.INFO, f'trial={n_trial}  branch_extension_steps={branch_extension_steps}')

            try:
                if initial_sampling == 'negated_hypothesis':
                    try:
                        negative_tree_root_formula = negate(proof_tree.root_node.formula)
                    except ContradictionNegationError as e:
                        raise FormulaDistractorGenerationFailure(str(e))
                elif initial_sampling == 'various_form':
                    distractors, _ = self._various_form_distractor.generate(proof_tree, 1,
                                                                            formulas_to_be_sat=formulas_to_be_sat,
                                                                            allow_smaller_proofs=allow_smaller_proofs)
                    if len(distractors) == 0:
                        raise FormulaDistractorGenerationFailure('could not generate the root node of the negative tree by VariousFormUnkownInterprandsDistractor().')
                    else:
                        negative_tree_root_formula = distractors[0]

                if self.generator.elim_dneg:
                    negative_tree_root_formula = eliminate_double_negation(negative_tree_root_formula)

                negative_tree = ProofTree([ProofNode(negative_tree_root_formula)])

                # SLOW
                negative_tree = self.generator.extend_branches(
                    negative_tree,
                    branch_extension_steps,
                    ng_formulas=[node.formula for node in proof_tree.nodes],
                    max_retry=self.extend_branches_max_retry,
                    force_fix_illegal_intermediate_constants=True,
                )
            except (ProofTreeGenerationFailure, ProofTreeGenerationImpossible) as e:
                raise FormulaDistractorGenerationFailure(str(e))

            negative_leaf_nodes = negative_tree.leaf_nodes
            if len(negative_leaf_nodes) - 1 < size and branch_extension_steps < self.max_branch_extension_steps:
                self._log(logging.INFO, f'continue to the next trial with increased branch_extension_steps, since number of negatieve leaf formulas - 1 = {len(negative_leaf_nodes) - 1} < size={size}')
                n_trial += 1
                continue

            distractor_formulas: List[Formula] = []
            distractor_nodes: List[ProofNode] = []
            # We sample at most len(leaf_nodes) - 1, since at least one distractor must be excluded so that the negated hypothesis can not be derived.
            if initial_sampling == 'negated_hypothesis':
                leaf_node_at_most = len(negative_leaf_nodes) - 1  # should exclude at least one
            elif initial_sampling == 'various_form':
                leaf_node_at_most = random.sample([len(negative_leaf_nodes) - 1, len(negative_leaf_nodes)], 1)[0]

            for distractor_node in random.sample(negative_leaf_nodes, leaf_node_at_most):
                distractor_formula = distractor_node.formula

                if len(distractor_formulas) >= size:
                    break

                if not _new_distractor_formula_is_ok(distractor_formula,
                                                     distractor_formulas + formulas_to_be_sat,
                                                     proof_tree,
                                                     allow_smaller_proofs=allow_smaller_proofs):
                    continue

                distractor_formulas.append(distractor_formula)
                distractor_nodes.append(distractor_node)

            if negative_tree is not None:
                self._log(logging.INFO, f'The negative tree is the following:\n{negative_tree.format_str}', boundary_level=2)

            # self._log(logging.INFO, f'{len(distractor_formulas)} distractors are in the negative tree', boundary_level=2)
            return distractor_formulas, {'negative_tree': negative_tree, 'negative_tree_missing_nodes': [node for node in negative_tree.leaf_nodes if node not in distractor_nodes]}


class MixtureDistractor(FormulaDistractor):

    def __init__(self, distractors: List[FormulaDistractor], **kwargs):
        super().__init__(**kwargs)
        self._distractors = distractors

    @property
    def default_max_retry(self) -> int:
        return 1

    @property
    def default_timeout(self) -> int:
        timeout_sum = 0
        for distractor in self._distractors:
            timeout_sum += distractor.default_max_retry * distractor.default_timeout
        return timeout_sum

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
        if no_warning:
            raise NotImplementedError()

        if size == 0:
            return [], {}

        sizes: List[int] = []
        remaining_size = size
        num_distractors = len(self._distractors)
        for i_distractor in range(0, num_distractors):
            if i_distractor == num_distractors - 1:
                _size = remaining_size
            else:
                if remaining_size < 0:
                    _size = 0
                else:
                    _size = random.randint(0, remaining_size)
                    if _size > remaining_size:
                        _size = remaining_size
                    remaining_size -= _size
            sizes.append(_size)

        distractor_formulas = []
        others = {}
        for distractor, _size in zip(self._distractors, sizes):
            try:
                _distractor_formulas, _others = distractor.generate(proof_tree, _size,
                                                                    formulas_to_be_sat = formulas_to_be_sat + distractor_formulas,
                                                                    allow_smaller_proofs=allow_smaller_proofs)

                distractor_formulas += _distractor_formulas

                for _other_key, _other_val in _others.items():
                    if _other_key in others:
                        raise ValueError(f'Duplicated other key {_other_key}')
                    others[_other_key] = _other_val

            except FormulaDistractorGenerationFailure as e:
                self._log(logging.WARNING, 'generating distractors failed with the following message:\n' + f'{str(e)}')

        if len(distractor_formulas) < size:
            return distractor_formulas, others
        else:
            # subsampling will lead to inconsistency for NegativeTreeDistractor
            # return random.sample(distractor_formulas, size), others

            return distractor_formulas, others


class FallBackDistractor(FormulaDistractor):

    def __init__(self, distractors: List[FormulaDistractor], **kwargs):
        super().__init__(**kwargs)
        self._distractors = distractors

    @property
    def default_max_retry(self) -> int:
        return 1

    @property
    def default_timeout(self) -> int:
        timeout_sum = 0
        for distractor in self._distractors:
            timeout_sum += distractor.default_max_retry * distractor.default_timeout
        return timeout_sum

    @profile
    def _generate(self,
                  proof_tree: ProofTree,
                  size: int,
                  formulas_to_be_sat: Optional[List[Formula]] = None,
                  allow_smaller_proofs=False,
                  no_warning=False) -> Tuple[List[Formula], Dict[str, Any]]:
        formulas_to_be_sat = formulas_to_be_sat or []
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
                                                                    formulas_to_be_sat = formulas_to_be_sat + distractor_formulas,
                                                                    allow_smaller_proofs=allow_smaller_proofs)

                distractor_formulas += _distractor_formulas

                for _other_key, _other_val in _others.items():
                    if _other_key in others:
                        raise ValueError(f'Duplicated other key {_other_key}')
                    others[_other_key] = _other_val

            except FormulaDistractorGenerationFailure as e:
                self._log(logging.WARNING, 'generating distractors failed with the following message:\n' + f'{str(e)}')

        if len(distractor_formulas) < size:
            return distractor_formulas, others
        else:
            return distractor_formulas[:size], others


AVAILABLE_DISTRACTORS = [
    'unknown_PAS',
    'unknown_interprands',
    'various_form',
    'negative_tree',
    'fallback.unknown_interprands.negative_tree',
    'fallback.various_form.negative_tree',
    'fallback.negative_tree.unknown_interprands',
    'mixture.unknown_interprands.negative_tree',
    'mixture.various_form.negative_tree',
]


def build(type_: str,
          generator: Optional[ProofTreeGenerator] = None,
          sample_hard_negatives=False,
          use_simplified_formulas_as_prototype=False,
          sample_prototype_formulas_from_tree=False,
          try_negated_hypothesis_first=False,
          **kwargs):

    prototype_formulas: Optional[List[Formula]] = None
    if type_.find('various_form') >= 0 and not sample_prototype_formulas_from_tree:
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

    if type_ == 'unknown_PAS':
        return UnkownPASDistractor(**kwargs)
    elif type_ == 'unknown_interprands':
        return SameFormUnkownInterprandsDistractor(**kwargs)
    elif type_ == 'various_form':
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
            try_negated_hypothesis_first=try_negated_hypothesis_first,
            **kwargs,
        )

    elif type_ == 'fallback.unknown_interprands.negative_tree':
        return FallBackDistractor(
            [
                SameFormUnkownInterprandsDistractor(**kwargs),
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    try_negated_hypothesis_first=try_negated_hypothesis_first,
                    **kwargs,
                ),
            ],
            **kwargs,
        )

    elif type_ == 'fallback.negative_tree.unknown_interprands':
        return FallBackDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    try_negated_hypothesis_first=try_negated_hypothesis_first,
                    **kwargs,
                ),
                SameFormUnkownInterprandsDistractor(**kwargs),
            ],
            **kwargs,
        )

    elif type_ == 'fallback.negative_tree.various_form':
        return FallBackDistractor(
            [
                NegativeTreeDistractor(
                    generator,
                    prototype_formulas=prototype_formulas,
                    try_negated_hypothesis_first=try_negated_hypothesis_first,
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
                    try_negated_hypothesis_first=try_negated_hypothesis_first,
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
                    try_negated_hypothesis_first=try_negated_hypothesis_first,
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
