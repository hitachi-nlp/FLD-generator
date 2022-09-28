from typing import List
from abc import abstractmethod, ABC
import random
import math

import logging
from typing import Optional
from .proof import ProofTree, ProofNode
from .formula import Formula, PREDICATES, CONSTANTS, negate
from .utils import shuffle
from .interpretation import generate_mappings_from_predicates_and_constants, interprete_formula, eliminate_double_negation
from .formula_checkers import is_ok_set as is_ok_formula_set
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

        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)

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
    """ Generate sentences which are the partial facts to derive negative of hypothesis """

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

        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)

        def generate_initial_negative_tree() -> ProofTree:
            neg_hypothesis = negate(proof_tree.root_node.formula)
            if self.generator.elim_dneg:
                neg_hypothesis = eliminate_double_negation(neg_hypothesis)
            return ProofTree([ProofNode(neg_hypothesis)])

        trial = 0
        the_most_distractor_formulas: List[Formula] = []
        while True:
            try:
                neg_tree = self.generator.extend_braches(
                    generate_initial_negative_tree,
                    math.ceil(num_distractors * 1.5),
                    max_retry=self.generator_max_retry,
                )
            except ProofTreeGenerationFailure as e:
                raise DistractorGenerationFailure('Distractor generation failed since self.generator.extend_braches() failed. The original message is the followings\n:%s', str(e))

            neg_leaf_formulas = [node.formula for node in neg_tree.leaf_nodes]
            _max_distractors = min(
                num_distractors,
                len(neg_leaf_formulas) - 1,  # at least one distractor must be excluded so that the negated hypothesis can not be derived
            )
            if _max_distractors == 0:
                return []

            distractor_formulas: List[Formula] = []
            for distractor_formula in random.sample(neg_leaf_formulas, len(neg_leaf_formulas)):
                if len(distractor_formulas) >= _max_distractors:
                    break

                if not is_ok_formula_set([distractor_formula] + distractor_formulas + formulas_in_tree):
                    continue

                if any(distractor_formula.rep == existent_formula
                       for existent_formula in distractor_formulas + formulas_in_tree):
                    continue

                distractor_formulas.append(distractor_formula)

            if len(distractor_formulas) > len(the_most_distractor_formulas):
                the_most_distractor_formulas = distractor_formulas

            if len(the_most_distractor_formulas) >= _max_distractors:
                return the_most_distractor_formulas

            trial += 1

            if trial >= self.max_retry:
                logger.warning(
                    'Could not generate %d distractors. return only %d distractors.',
                    num_distractors,
                    len(the_most_distractor_formulas),
                )
                return the_most_distractor_formulas


class MixtureDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float, distractors: List[FormalLogicDistractor]):
        super().__init__(num_distractor_factor)
        self._distractors = distractors

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        distractor_formulas = []
        for distractor in self._distractors:
            distractor_formulas += distractor.generate(proof_tree)
        return random.sample(distractor_formulas, num_distractors)


class FallBackDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float, distractors: List[FormalLogicDistractor]):
        super().__init__(num_distractor_factor)
        self._distractors = distractors

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        num_distractors = _get_num_distractors(proof_tree, self.num_distractor_factor)
        distractors = []
        for distractor in self._distractors:
            if len(distractors) >= num_distractors:
                break
            try:
                _distractors = distractor.generate(proof_tree)
                distractors.extend(_distractors)
            except DistractorGenerationFailure as e:
                logger.warning('Generating distractors by %s failed with the following message:', str(distractor))
                logger.warning(str(e))
        # raise DistractorGenerationFailure('The LAST distractor\'s message is the followings:%s', str(last_error))
        return distractors[:num_distractors]


def _get_num_distractors(proof_tree: ProofTree, num_distractor_factor: float) -> int:
    leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
    return int(len(leaf_formulas) * num_distractor_factor)


def build(type_: str,
          num_distractor_factor: float,
          generator: Optional[ProofTreeGenerator] = None):
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

    else:
        raise ValueError(f'Unknown distractor type {type_}')
