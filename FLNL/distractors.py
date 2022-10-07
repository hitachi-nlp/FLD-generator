from typing import List
from abc import abstractmethod, ABC
import random
import math

import logging
from typing import Optional
from .proof import ProofTree, ProofNode
from .formula import Formula, PREDICATES, CONSTANTS, negate, ContradictionNegationError
from .utils import shuffle
from .interpretation import generate_mappings_from_predicates_and_constants, interprete_formula, eliminate_double_negation
from .formula_checkers import (
    is_ok_set as is_ok_formula_set,
    is_consistent_set as is_consistent_formula_set,
)
from .proof_tree_generators import ProofTreeGenerator
from .exception import FormalLogicExceptionBase
from .proof_tree_generators import ProofTreeGenerationFailure

logger = logging.getLogger(__name__)


class DistractorGenerationFailure(FormalLogicExceptionBase):
    pass


class FormalLogicDistractor(ABC):

    def __init__(self, num_distractor_factor: float):
        self.num_distractor_factor = num_distractor_factor

    @abstractmethod
    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        pass


class UnkownPASDistractor(FormalLogicDistractor):

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]

        known_zeroary_predicates = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.zeroary_predicates
        })
        unused_predicates = shuffle(list(set(PREDICATES) - set(known_zeroary_predicates)))

        num_zeroary_distractors = len(known_zeroary_predicates) * self.num_distractor_factor
        distractor_zeroary_predicates = unused_predicates[:int(num_zeroary_distractors)]
        zeroary_distractors = [Formula(f'{predicate}') for predicate in distractor_zeroary_predicates]

        unary_PASs = sorted({
            PAS.rep
            for formula in leaf_formulas
            for PAS in formula.unary_interprand_PASs
        })
        known_unary_predicates = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.unary_predicates
        })
        unused_predicates = sorted(set(PREDICATES) - set(known_unary_predicates) - set(distractor_zeroary_predicates))

        known_constants = sorted({
            pred.rep
            for formula in leaf_formulas
            for pred in formula.constants
        })
        unused_constants = sorted(set(CONSTANTS) - set(known_constants))

        in_domain_unused_PASs: List[Formula] = []
        for predicate in known_unary_predicates:
            for constant in known_constants:
                fact_rep = f'{predicate}{constant}'

                if all((fact_rep not in formula.rep for formula in leaf_formulas + in_domain_unused_PASs)):
                    in_domain_unused_PASs.append(Formula(fact_rep))

        outof_domain_unused_PASs = []
        for predicate in unused_predicates:
            for constant in known_constants:
                outof_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))
        for predicate in known_unary_predicates:
            for constant in unused_constants:
                fact_rep = f'{predicate}{constant}'
                outof_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))

        in_domain_unused_PASs = shuffle(in_domain_unused_PASs)
        outof_domain_unused_PASs = shuffle(outof_domain_unused_PASs)
        num_unary_distractors = len(unary_PASs) * self.num_distractor_factor
        unary_distractors = (in_domain_unused_PASs + outof_domain_unused_PASs)[:int(num_unary_distractors)]

        return zeroary_distractors + unary_distractors


class SameFormUnkownInterprandsDistractor(FormalLogicDistractor):
    """ Generate the same form formula with unknown predicates or constants """

    def __init__(self,
                 num_distractor_factor: float,
                 max_retry: int = 100):
        super().__init__(num_distractor_factor)
        self.max_retry = max_retry

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        formulas_in_tree = [node.formula for node in proof_tree.nodes]
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
        original_tree_is_consistent = is_consistent_formula_set(formulas_in_tree)

        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        logger.info('==== (SameFormUnkownInterprandsDistractor) Try to generate %d distractors ====', num_distractors)

        if num_distractors == 0:
            return []

        leaf_formulas = shuffle(leaf_formulas)
        distractor_formulas: List[Formula] = []

        trial = 0
        while True:
            if trial >= self.max_retry:
                logger.warning(
                    'Could not generate %d distractors. return only %d distractors.',
                    num_distractors,
                    len(distractor_formulas),
                )
                return distractor_formulas

            if len(distractor_formulas) >= num_distractors:
                break

            src_formula = leaf_formulas[trial % len(leaf_formulas)]

            used_predicates = list({pred.rep for pred in src_formula.predicates})
            used_constants = list({pred.rep for pred in src_formula.constants})
            unused_predicates = shuffle(list(set(PREDICATES) - set(used_predicates)))
            unused_constants = shuffle(list(set(CONSTANTS) - set(used_constants)))

            # It is possible that (used_predicates, used_constants) pair produces a new formula,
            # e.g., "{B}{b} -> {A}{a}" when src_formula is "{A}{a} -> {B}{b}"
            # We guess, however, that such transoformation leads to many inconsistent or not senseful formula set, as the above.
            # We may still filter out such a formula by some heuristic method, but this is costly.
            # Thus, we decided not ot use used_predicates + used_predicates pair.
            if trial % 3 in [0, 1]:
                # We guess (unused_predicates, used_constants) pair, that produces the formula of the known object plus unknown predicate,
                # is more distractive than the inverse pair.
                # We sample it more often than the inverseed pair,
                tgt_space = [
                    (unused_predicates, used_constants),
                    (used_predicates, unused_constants),
                    (unused_predicates, unused_constants)
                ]
            else:
                tgt_space = [
                    (used_predicates, unused_constants),
                    (unused_predicates, used_constants),
                    (unused_predicates, unused_constants)
                ]

            is_found = False
            found_formula = None
            for tgt_predicates, tgt_constants in tgt_space:
                for mapping in generate_mappings_from_predicates_and_constants(
                    [p.rep for p in src_formula.predicates],
                    [c.rep for c in src_formula.constants],
                    tgt_predicates,
                    tgt_constants,
                    block_shuffle=True
                ):
                    transformed_formula = interprete_formula(src_formula, mapping, elim_dneg=True)

                    if not is_ok_formula_set([transformed_formula] + distractor_formulas + formulas_in_tree):  # SLOW, called many times
                        continue

                    if not is_consistent_formula_set([transformed_formula] + distractor_formulas):
                        continue

                    # The tree will become inconsistent by ADDING distractor formulas.
                    if original_tree_is_consistent and\
                            not is_consistent_formula_set([transformed_formula] + distractor_formulas + formulas_in_tree):
                        continue

                    if any(transformed_formula.rep == existent_formula
                           for existent_formula in distractor_formulas + formulas_in_tree):
                        # is not new
                        continue

                    found_formula = transformed_formula
                    is_found = True
                    break
                if is_found:
                    break

            if is_found:
                distractor_formulas.append(found_formula)

            trial += 1

        return distractor_formulas


class NegatedHypothesisTreeDistractor(FormalLogicDistractor):
    """ Generate sentences which are the partial facts to derive negative of hypothesis.

    At least one leaf formula is excluded to make the tree incomplete.
    """

    def __init__(self,
                 num_distractor_factor: float,
                 generator: ProofTreeGenerator,
                 generator_max_retry: int = 5,
                 max_retry: int = 100):
        super().__init__(num_distractor_factor)

        if generator.complicated_arguments_weight < 0.01:
            raise ValueError('Generator with too small "complicated_arguments_weight" will lead to generation failure, since we try to generate a tree with negated hypothesis, which is only in the complicated arguments.')
        self.generator = generator
        self.generator_max_retry = generator_max_retry
        self.max_retry = max_retry

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        formulas_in_tree = [node.formula for node in proof_tree.nodes]
        original_tree_is_consistent = is_consistent_formula_set(formulas_in_tree)

        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        logger.info('==== (NegatedHypothesisTreeDistractor) Try to generate %d distractors ====', num_distractors)

        if num_distractors == 0:
            return []

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
                    num_distractors,
                    len(the_most_distractor_formulas),
                )
                if the_most_tree is not None:
                    logger.info('The negative tree is the following:\n%s', the_most_tree.format_str)
                return the_most_distractor_formulas

            # gradually increase the number of extension steps to find the "just in" size tree.
            branch_extension_steps_factor = min(0.5 + 0.1 * n_trial, max_branch_extension_factor)
            branch_extension_steps = math.ceil(num_distractors * branch_extension_steps_factor)
            logger.info('-- (NegatedHypothesisTreeDistractor) trial=%d    branch_extension_steps=%d', n_trial, branch_extension_steps)

            try:
                neg_tree = self.generator.extend_braches(
                    generate_initial_negative_tree,
                    branch_extension_steps,
                    max_retry=self.generator_max_retry,
                )
            except ProofTreeGenerationFailure as e:
                raise DistractorGenerationFailure(f'Distractor generation failed since self.generator.extend_braches() failed. The original message is the followings\n:{str(e)}')

            neg_leaf_formulas = [node.formula for node in neg_tree.leaf_nodes]
            if len(neg_leaf_formulas) - 1 == 0:
                n_trial += 1
                logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial since no negatieve leaf formulas are found.')
                continue
            elif len(neg_leaf_formulas) - 1 < num_distractors:
                if branch_extension_steps_factor < max_branch_extension_factor:
                    logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial with increased tree size, since number of negatieve leaf formulas %d < num_distractors=%d',
                                len(neg_leaf_formulas),
                                num_distractors)
                    n_trial += 1
                    continue
            # else:
            #     logger.info('%d formulas in negative tree found. We will select appropriate ones from these formulas.', len(neg_leaf_formulas))

            distractor_formulas: List[Formula] = []
            # We sample at most len(neg_leaf_formulas) - 1, since at least one distractor must be excluded so that the negated hypothesis can not be derived.
            for distractor_formula in random.sample(neg_leaf_formulas, len(neg_leaf_formulas) - 1):
                if len(distractor_formulas) >= num_distractors:
                    break

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

                if any(distractor_formula.rep == existent_formula
                       for existent_formula in distractor_formulas + formulas_in_tree):
                    continue

                distractor_formulas.append(distractor_formula)

            if len(distractor_formulas) > len(the_most_distractor_formulas):
                the_most_distractor_formulas = distractor_formulas
                the_most_tree = neg_tree

            if len(the_most_distractor_formulas) >= num_distractors:
                logger.info('(NegatedHypothesisTreeDistractor) generating %d formulas succeeded!', num_distractors)
                if the_most_tree is not None:
                    logger.info('The negative tree is the following:\n%s', the_most_tree.format_str)
                return the_most_distractor_formulas
            else:
                logger.info('(NegatedHypothesisTreeDistractor) Continue to the next trial since, only %d (< num_distractors=%d) negative leaf formulas are appropriate.',
                            len(distractor_formulas),
                            num_distractors)
                n_trial += 1
                continue


class MixtureDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float, distractors: List[FormalLogicDistractor]):
        super().__init__(num_distractor_factor)
        self._distractors = distractors

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        logger.info('==== (MixtureDistractor) Try to generate %d distractors ====', num_distractors)

        if num_distractors == 0:
            return []

        distractor_formulas = []
        for distractor in self._distractors:
            distractor_formulas += distractor.generate(proof_tree)

        if len(distractor_formulas) < num_distractors:
            logger.warning(
                '(MixtureDistractor) Could not generate %d formulas. Return only %d formulas.',
                num_distractors,
                len(distractor_formulas),
            )
            return distractor_formulas
        else:
            return random.sample(distractor_formulas, num_distractors)


class FallBackDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float, distractors: List[FormalLogicDistractor]):
        super().__init__(num_distractor_factor)
        self._distractors = distractors

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        logger.info('==== (FallBackDistractor) Try to generate %d distractors ====', num_distractors)

        if num_distractors == 0:
            return []

        distractor_formulas: List[Formula] = []
        for distractor in self._distractors:
            if len(distractor_formulas) >= num_distractors:
                break
            try:
                _distractors = distractor.generate(proof_tree)
                distractor_formulas.extend(_distractors)
            except DistractorGenerationFailure as e:
                logger.warning('Generating distractors by %s failed with the following message:', distractor.__class__)
                logger.warning(str(e))

        if len(distractor_formulas) < num_distractors:
            logger.warning(
                '(FallBackDistractor) Could not generate %d formulas. Return only %d formulas.',
                num_distractors,
                len(distractor_formulas),
            )
            return distractor_formulas
        else:
            return distractor_formulas[:num_distractors]


def _get_num_distractors(proof_tree: ProofTree, num_distractor_factor: float) -> int:
    leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
    return int(len(leaf_formulas) * num_distractor_factor)


AVAILABLE_DISTRACTORS = [
    'unknown_PAS',
    'unknown_interprands',
    'negated_hypothesis_tree',
    'mixture.unknown_interprands.negated_hypothesis_tree',
    'fallback.negated_hypothesis_tree.unknown_interprands',
]


def build(type_: str,
          num_distractor_factor: float,
          generator: Optional[ProofTreeGenerator] = None):
    if type_ not in AVAILABLE_DISTRACTORS:
        raise ValueError(f'Unknown distractor type {type_}')

    if type_ == 'unknown_PAS':
        return UnkownPASDistractor(num_distractor_factor=num_distractor_factor)
    elif type_ == 'unknown_interprands':
        return SameFormUnkownInterprandsDistractor(num_distractor_factor)
    elif type_ == 'negated_hypothesis_tree':
        if generator is None:
            raise ValueError()
        return NegatedHypothesisTreeDistractor(num_distractor_factor, generator)
    elif type_ == 'mixture.unknown_interprands.negated_hypothesis_tree':
        return MixtureDistractor(
            num_distractor_factor,
            [
                SameFormUnkownInterprandsDistractor(num_distractor_factor),
                NegatedHypothesisTreeDistractor(num_distractor_factor, generator),
            ]
        )
    elif type_ == 'fallback.negated_hypothesis_tree.unknown_interprands':
        return FallBackDistractor(
            num_distractor_factor,
            [
                NegatedHypothesisTreeDistractor(num_distractor_factor, generator),
                SameFormUnkownInterprandsDistractor(num_distractor_factor),
            ]
        )
