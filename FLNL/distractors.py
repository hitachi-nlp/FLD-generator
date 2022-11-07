from typing import List, Any, Iterable
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
)
from .formula_checkers import (
    is_ok_set as is_ok_formula_set,
    is_senseful,
    is_consistent_set as is_consistent_formula_set,
    is_new as is_formula_new,
)
from .proof_tree_generators import ProofTreeGenerator
from .exception import FormalLogicExceptionBase
from .proof_tree_generators import ProofTreeGenerationFailure
from FLNL.utils import run_with_timeout_retry, RetryAndTimeoutFailure
import kern_profiler


logger = logging.getLogger(__name__)


class DistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class FormalLogicDistractor(ABC):

    def generate(self,
                 proof_tree: ProofTree,
                 size: int,
                 max_retry: Optional[int] = None,
                 timeout: Optional[int] = None) -> List[Formula]:
        max_retry = max_retry or self.default_max_retry
        timeout = timeout or self.default_timeout
        try:
            return run_with_timeout_retry(
                self._generate,
                func_args=[proof_tree, size],
                func_kwargs={},
                retry_exception_class=DistractorGenerationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='_generate()',
            )
        except RetryAndTimeoutFailure as e:
            raise DistractorGenerationFailure(str(e))

    @property
    @abstractmethod
    def default_max_retry(self) -> int:
        pass

    @property
    @abstractmethod
    def default_timeout(self) -> int:
        pass

    @abstractmethod
    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        pass


class UnkownPASDistractor(FormalLogicDistractor):

    @profile
    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
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

        return shuffle(zeroary_distractors + unary_distractors)[:size]

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 10


class SameFormUnkownInterprandsDistractor(FormalLogicDistractor):
    """ Generate the same form formula with unknown predicates or constants injected.

    This class is superior to UnkownPASDistractor, which does not consider the similarity of the forms of formulas.
    """

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 10

    @profile
    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        logger.info('==== (SameFormUnkownInterprandsDistractor) Try to generate %d distractors ====', size)
        if size == 0:
            return []

        formulas_in_tree = [node.formula for node in proof_tree.nodes]
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
        original_tree_is_consistent = is_consistent_formula_set(formulas_in_tree)

        leaf_formulas = shuffle(leaf_formulas)
        distractor_formulas: List[Formula] = []

        trial = 0
        max_trial = size * 10
        for trial in range(max_trial):
            if trial >= max_trial:
                logger.warning(
                    'Could not generate %d distractors. return only %d distractors.',
                    size,
                    len(distractor_formulas),
                )
                return distractor_formulas

            if len(distractor_formulas) >= size:
                break

            src_formula = leaf_formulas[trial % len(leaf_formulas)]

            used_predicates = shuffle(list({pred.rep for pred in src_formula.predicates}))
            used_constants = shuffle(list({pred.rep for pred in src_formula.constants}))

            # use subset of unused predicates and constant so that generate_mappings_from_predicates_and_constants() does not generate too large list
            # * 3 comes from the intuition that a formula may contain 3 predicates or constants on maximum like {A}{a} v {B}{b} -> {C}{c}
            unused_predicates = shuffle(list(set(PREDICATES) - set(used_predicates)))[:size * 3]
            unused_constants = shuffle(list(set(CONSTANTS) - set(used_constants)))[:size * 3]

            # mix unsed predicates constants a little
            used_unused_predicates = shuffle(used_predicates + unused_predicates)
            used_unused_constants = shuffle(used_constants + unused_constants)

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
                    # (used_predicates, used_constants),
                    (used_unused_predicates, used_constants),
                    (used_unused_predicates, used_unused_constants),
                    (unused_predicates, unused_constants)
                ]
            else:
                tgt_space = [
                    # (used_predicates, used_constants),
                    (used_predicates, used_unused_constants),
                    (used_unused_predicates, used_unused_constants),
                    (unused_predicates, unused_constants)
                ]

            do_print = False
            is_found = False
            found_formula = None
            for tgt_predicates, tgt_constants in tgt_space:
                # import pudb; pudb.set_trace()
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

                    if not is_formula_new(transformed_formula,
                                          distractor_formulas + formulas_in_tree):
                        continue

                    if not is_ok_formula_set([transformed_formula] + distractor_formulas + formulas_in_tree):  # SLOW, called many times
                        if do_print:
                            print('!! not is_ok_formula_set()')
                            # print('    mapping:', mapping)
                            print('    src_formula:', src_formula)
                            print('    tgt_predicates:', tgt_predicates)
                            print('    tgt_constants:', tgt_constants)
                            print('    transformed_formula:', transformed_formula)
                            print('    is_senseful:', is_senseful(transformed_formula))
                        continue

                    if not is_consistent_formula_set([transformed_formula] + distractor_formulas):
                        continue

                    # The tree will become inconsistent by ADDING distractor formulas.
                    if original_tree_is_consistent and\
                            not is_consistent_formula_set([transformed_formula] + distractor_formulas + formulas_in_tree):
                        continue

                    found_formula = transformed_formula
                    is_found = True
                    break
                if is_found:
                    break

            if is_found:
                distractor_formulas.append(found_formula)

        return distractor_formulas


class VariousFormUnkownInterprandsDistractor(FormalLogicDistractor):
    """
    Unlike SameFormUnkownInterprandsDistractor:
    (i) we sample the formula prototypes not from the tree but from all possible prototypes specified by the user.
        we think this is more appropriate.
    (ii) we sample predicates and constants from the tree, rather than a sampled leaf formula.
    (iii) we reject distractor formula all the PASs of which are the used ones.

    (ii) and (iii) makes distractors more "safe", i.e., fewer chance of having another proof due to the new formulas.
    However, this makes distractors less distractive, of course.

    We are confident that (i) is better.
    We are not that confident about (ii) and (iii) since it makes less distractive.
    """

    def __init__(self,
                 prototype_formulas: Optional[List[Formula]] = None,
                 sample_hard_negatives=False):
        self._prototype_formulas = prototype_formulas
        self._sample_hard_negatives = sample_hard_negatives

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 10

    @profile
    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        logger.info('==== (VariousFormUnkownInterprandsDistractor) Try to generate %d distractors ====', size)
        if size == 0:
            return []

        leaf_formulas_in_tree = [node.formula for node in proof_tree.leaf_nodes]
        original_tree_is_consistent = is_consistent_formula_set(leaf_formulas_in_tree)

        used_PASs = {PAS.rep
                     for formula in leaf_formulas_in_tree
                     for PAS in formula.PASs}
        used_pairs = {(PAS.predicates[0].rep, PAS.constants[0].rep)
                      for formula in leaf_formulas_in_tree
                      for PAS in formula.PASs
                      if len(PAS.constants) > 0}

        num_zeroary_predicates = {zeroary_predicate.rep
                                  for formula in leaf_formulas_in_tree
                                  for zeroary_predicate in formula.zeroary_predicates}
        num_unary_predicates = {unary_predicate.rep
                                for formula in leaf_formulas_in_tree
                                for unary_predicate in formula.unary_predicates}

        used_predicates = {pred.rep
                           for formula in leaf_formulas_in_tree
                           for pred in formula.predicates}
        used_constants = {constant.rep
                          for formula in leaf_formulas_in_tree
                          for constant in formula.constants}

        unused_predicates = set(PREDICATES) - set(used_predicates)
        unused_constants = set(CONSTANTS) - set(used_constants)

        if self._prototype_formulas is not None:
            prototype_formulas = self._prototype_formulas
            logger.info('sample from %d prototype formulas specified by the user', len(prototype_formulas))
        else:
            prototype_formulas = [node.formula for node in proof_tree.nodes]
            logger.info('sample from %d prototype formulas found in the tree', len(prototype_formulas))

        # FIXME: this is logic only works for trees where the predicate arity is the same for all the formulas.
        if num_zeroary_predicates > num_unary_predicates:
            tree_predicate_type = 'zeroary'
        elif num_zeroary_predicates < num_unary_predicates:
            tree_predicate_type = 'unary'
        elif num_zeroary_predicates == num_unary_predicates:
            tree_predicate_type = 'unknown'

        # max_PASs_per_formula = 3
        # if tree_predicate_type == 'zeroary':
        #     estimated_predicates_required = size * max_PASs_per_formula
        #     estimated_constants_required = size * max_PASs_per_formula
        # elif tree_predicate_type == 'unary':
        #     estimated_predicates_required = int(math.ceil(math.sqrt(size * max_PASs_per_formula)))
        #     estimated_constants_required = int(math.ceil(math.sqrt(size * max_PASs_per_formula)))
        # elif tree_predicate_type == 'unknown':
        #     estimated_predicates_required = size * max_PASs_per_formula
        #     estimated_constants_required = size * max_PASs_per_formula

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
                logger.warning(
                    'Could not generate %d distractors. return only %d distractors.',
                    size,
                    len(distractor_formulas),
                )
                return distractor_formulas

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

            tgt_space = []
            if self._sample_hard_negatives:
                # It is possible that (used_predicates, used_constants) pair produces a new formula,
                # e.g., "{B}{b} -> {A}{a}" when src_formula is "{A}{a} -> {B}{b}"
                # We guess, however, that such transoformation leads to many inconsistent or not senseful formula set, as the above.
                # thus here, we make it as optional.
                tgt_space.extend([
                    (used_paired_predicates_samples, used_paired_constants_samples),
                    (used_predicates_samples, used_constants_samples),
                ])
            if trial % 2 == 0:
                tgt_space.extend([
                    (used_predicates_samples, used_unused_constants_samples),
                    (used_unused_predicates_samples, used_unused_constants_samples),
                ])
            else:
                tgt_space.extend([
                    (used_unused_predicates_samples, used_constants_samples),
                    (used_unused_predicates_samples, used_unused_constants_samples),
                ])
            tgt_space.extend([
                (unused_predicates_samples, unused_constants_samples)
            ])

            is_found = False
            found_formula = None
            for tgt_predicates, tgt_constants in tgt_space:
                # import pudb; pudb.set_trace()
                for mapping in generate_mappings_from_predicates_and_constants(
                    [p.rep for p in src_formula.predicates],
                    [c.rep for c in src_formula.constants],
                    tgt_predicates,
                    tgt_constants,
                    shuffle=True,
                    allow_many_to_one=False,
                ):
                    distractor_formula = interpret_formula(src_formula, mapping, elim_dneg=True)

                    if not is_formula_new(distractor_formula,
                                          distractor_formulas + leaf_formulas_in_tree):
                        continue

                    if all(distractor_PAS.rep in used_PASs
                           for distractor_PAS in distractor_formula.PASs):
                        # if all the distractor PASs are in tree,
                        # we have high chance of (i) producing nonsens formula set (ii) producing other proof tree.
                        # we want to prevent such possiblity.
                        continue

                    if not is_ok_formula_set([distractor_formula] + distractor_formulas + leaf_formulas_in_tree):  # SLOW, called many times
                        continue

                    if not is_consistent_formula_set([distractor_formula] + distractor_formulas):
                        continue

                    # The tree will become inconsistent by ADDING distractor formulas.
                    if original_tree_is_consistent and\
                            not is_consistent_formula_set([distractor_formula] + distractor_formulas + leaf_formulas_in_tree):
                        continue

                    found_formula = distractor_formula
                    is_found = True
                    break
                if is_found:
                    break

            if is_found:
                distractor_formulas.append(found_formula)

        return distractor_formulas


class NegatedHypothesisTreeDistractor(FormalLogicDistractor):
    """ Generate sentences which are the partial facts to derive negative of hypothesis.

    At least one leaf formula is excluded to make the tree incomplete.
    """

    def __init__(self,
                 generator: ProofTreeGenerator,
                 generator_max_retry: int = 5,
                 max_retry: int = 100):
        super().__init__()

        if generator.complicated_arguments_weight < 0.01:
            raise ValueError('Generator with too small "complicated_arguments_weight" will lead to generation failure, since we try to generate a tree with negated hypothesis, which is only in the complicated arguments.')
        self.generator = generator
        self.generator_max_retry = generator_max_retry
        self.max_retry = max_retry

    @property
    def default_max_retry(self) -> int:
        return 3

    @property
    def default_timeout(self) -> int:
        return 10

    @profile
    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        logger.info('==== (NegatedHypothesisTreeDistractor) Try to generate %d distractors ====', size)
        if size == 0:
            return []

        formulas_in_tree = [node.formula for node in proof_tree.nodes]
        original_tree_is_consistent = is_consistent_formula_set(formulas_in_tree)

        def generate_initial_negative_tree() -> ProofTree:
            try:
                neg_hypothesis = negate(proof_tree.root_node.formula)
            except ContradictionNegationError as e:
                raise ProofTreeGenerationFailure(str(e))
            if self.generator.elim_dneg:
                neg_hypothesis = eliminate_double_negation(neg_hypothesis)
            return ProofTree([ProofNode(neg_hypothesis)])

        n_trial = 0
        the_most_distractor_formulas: List[Formula] = []
        the_most_tree: Optional[ProofTree] = None
        max_branch_extension_factor = 3.0
        while True:
            if n_trial >= self.max_retry:
                logger.warning(
                    '(NegatedHypothesisTreeDistractor) Could not generate %d distractor formulas. return only %d distractors.',
                    size,
                    len(the_most_distractor_formulas),
                )
                if the_most_tree is not None:
                    logger.info('The negative tree is the following:\n%s', the_most_tree.format_str)
                return the_most_distractor_formulas

            # gradually increase the number of extension steps to find the "just in" size tree.
            branch_extension_steps_factor = min(0.5 + 0.1 * n_trial, max_branch_extension_factor)
            branch_extension_steps = math.ceil(size * branch_extension_steps_factor)
            logger.info('-- (NegatedHypothesisTreeDistractor) trial=%d    branch_extension_steps=%d', n_trial, branch_extension_steps)

            try:
                neg_tree = self.generator.extend_branches(
                    generate_initial_negative_tree,
                    branch_extension_steps,
                    max_retry=self.generator_max_retry,
                )
            except ProofTreeGenerationFailure as e:
                raise DistractorGenerationFailure(str(e))

            neg_leaf_formulas = [node.formula for node in neg_tree.leaf_nodes]
            if len(neg_leaf_formulas) - 1 == 0:
                n_trial += 1
                logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial since no negatieve leaf formulas are found.')
                continue
            elif len(neg_leaf_formulas) - 1 < size:
                if branch_extension_steps_factor < max_branch_extension_factor:
                    logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial with increased tree size, since number of negatieve leaf formulas %d < size=%d',
                                len(neg_leaf_formulas) - 1,
                                size)
                    n_trial += 1
                    continue
            # else:
            #     logger.info('%d formulas in negative tree found. We will select appropriate ones from these formulas.', len(neg_leaf_formulas))

            distractor_formulas: List[Formula] = []
            # We sample at most len(neg_leaf_formulas) - 1, since at least one distractor must be excluded so that the negated hypothesis can not be derived.
            for distractor_formula in random.sample(neg_leaf_formulas, len(neg_leaf_formulas) - 1):
                if len(distractor_formulas) >= size:
                    break

                if not is_formula_new(distractor_formula,
                                      distractor_formulas + formulas_in_tree):
                    continue

                if not is_ok_formula_set([distractor_formula] + distractor_formulas + formulas_in_tree):
                    continue

                # We do not check the consistency between distractor_formulas.
                # They must be consistent since they comes from the leaf nodes of the generated tree, which guarantee the consistency.

                # We check the formulas become inconsistent by ADDING distractor_formulas to the original tree.
                # This logic have false negative, the case where the original tree is inconsistent AND adding distractors yields another inconsistency.
                # Since the detection of such logic is complicated and such case is rare, we abandon the detection.
                if original_tree_is_consistent and\
                        not is_consistent_formula_set([distractor_formula] + distractor_formulas + formulas_in_tree):
                    continue

                distractor_formulas.append(distractor_formula)

            if len(distractor_formulas) > len(the_most_distractor_formulas):
                the_most_distractor_formulas = distractor_formulas
                the_most_tree = neg_tree

            if len(the_most_distractor_formulas) >= size:
                logger.info('(NegatedHypothesisTreeDistractor) generating %d formulas succeeded!', size)
                if the_most_tree is not None:
                    logger.info('The negative tree is the following:\n%s', the_most_tree.format_str)
                return the_most_distractor_formulas
            else:
                logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial since, only %d (< size=%d) negative leaf formulas are appropriate.',
                            len(distractor_formulas),
                            size)
                n_trial += 1
                continue


class MixtureDistractor(FormalLogicDistractor):

    def __init__(self, distractors: List[FormalLogicDistractor]):
        super().__init__()
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

    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        logger.info('==== (MixtureDistractor) Try to generate %d distractors ====', size)
        if size == 0:
            return []

        distractor_formulas = []
        for distractor in self._distractors:
            try:
                distractor_formulas += distractor.generate(proof_tree, size)
            except DistractorGenerationFailure as e:
                logger.warning('Generating distractors by %s failed with the following message:', distractor.__class__)
                logger.warning('\n%s', str(e))

        if len(distractor_formulas) < size:
            logger.warning(
                '(MixtureDistractor) Could not generate %d formulas. Return only %d formulas.',
                size,
                len(distractor_formulas),
            )
            return distractor_formulas
        else:
            return random.sample(distractor_formulas, size)


class FallBackDistractor(FormalLogicDistractor):

    def __init__(self, distractors: List[FormalLogicDistractor]):
        super().__init__()
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

    def _generate(self, proof_tree: ProofTree, size: int) -> List[Formula]:
        logger.info('==== (FallBackDistractor) Try to generate %d distractors ====', size)
        if size == 0:
            return []

        distractor_formulas: List[Formula] = []
        for distractor in self._distractors:
            if len(distractor_formulas) >= size:
                break
            try:
                _distractors = distractor.generate(proof_tree, size)
                distractor_formulas.extend(_distractors)
            except DistractorGenerationFailure as e:
                logger.warning('Generating distractors by %s failed with the following message:', distractor.__class__)
                logger.warning('\n%s', str(e))

        if len(distractor_formulas) < size:
            logger.warning(
                '(FallBackDistractor) Could not generate %d formulas. Return only %d formulas.',
                size,
                len(distractor_formulas),
            )
            return distractor_formulas
        else:
            return distractor_formulas[:size]


AVAILABLE_DISTRACTORS = [
    'unknown_PAS',
    'unknown_interprands',
    'various_form',
    'negated_hypothesis_tree',
    'fallback.unknown_interprands.negated_hypothesis_tree',
    'fallback.various_form.negated_hypothesis_tree',
    'fallback.negated_hypothesis_tree.unknown_interprands',
    'mixture.unknown_interprands.negated_hypothesis_tree',
    'mixture.various_form.negated_hypothesis_tree',
]


def build(type_: str,
          generator: Optional[ProofTreeGenerator] = None,
          sample_hard_negatives=False,
          sample_prototype_formulas_from_tree=False):
    if type_ not in AVAILABLE_DISTRACTORS:
        raise ValueError(f'Unknown distractor type {type_}')

    prototype_formulas: Optional[List[Formula]] = None
    if type_.find('various_form') >= 0 and not sample_prototype_formulas_from_tree:
        if generator is not None:
            prototype_formulas = []
            logger.info('collecting prototype formulas from arguments to build the distractor ...')
            for argument in generator.arguments:
                for formula in argument.all_formulas:
                    if all(not formula_is_identical_to(formula, existent_formula)
                           for existent_formula in prototype_formulas):
                        prototype_formulas.append(formula)
            logger.info('collecting prototype formulas from arguments to build the distractor done!')
        else:
            logger.warning('generator is not specified. Thus, the VariousFormUnkownInterprandsDistractor will use formulas in tree as prototype formulas.')

    if type_ == 'unknown_PAS':
        return UnkownPASDistractor()
    elif type_ == 'unknown_interprands':
        return SameFormUnkownInterprandsDistractor()
    elif type_ == 'various_form':
        return VariousFormUnkownInterprandsDistractor(
            prototype_formulas=prototype_formulas,
            sample_hard_negatives=sample_hard_negatives,
        )
    elif type_ == 'negated_hypothesis_tree':
        if generator is None:
            raise ValueError()
        return NegatedHypothesisTreeDistractor(generator)

    elif type_ == 'fallback.unknown_interprands.negated_hypothesis_tree':
        return FallBackDistractor(
            [
                SameFormUnkownInterprandsDistractor(),
                NegatedHypothesisTreeDistractor(generator),
            ]
        )
    elif type_ == 'fallback.various_form.negated_hypothesis_tree':
        return FallBackDistractor(
            [
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                ),
                NegatedHypothesisTreeDistractor(generator),
            ]
        )

    elif type_ == 'fallback.negated_hypothesis_tree.unknown_interprands':
        return FallBackDistractor(
            [
                NegatedHypothesisTreeDistractor(generator),
                SameFormUnkownInterprandsDistractor(),
            ]
        )

    elif type_ == 'mixture.unknown_interprands.negated_hypothesis_tree':
        return MixtureDistractor(
            [
                SameFormUnkownInterprandsDistractor(),
                NegatedHypothesisTreeDistractor(generator),
            ]
        )
    elif type_ == 'mixture.various_form.negated_hypothesis_tree':
        return MixtureDistractor(
            [
                VariousFormUnkownInterprandsDistractor(
                    prototype_formulas=prototype_formulas,
                    sample_hard_negatives=sample_hard_negatives,
                ),
                NegatedHypothesisTreeDistractor(generator),
            ]
        )
