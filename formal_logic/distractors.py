from typing import List
from abc import abstractmethod, ABC
import random

import logging
from .proof import ProofTree
from .formula import Formula, PREDICATES, CONSTANTS
from .utils import shuffle
from .interpretation import generate_mappings_from_predicates_and_constants, interprete_formula
from .formula_checkers import is_formula_set_nonsense

import kern_profiler

logger = logging.getLogger(__name__)


class FormalLogicDistractor(ABC):

    @abstractmethod
    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        pass


class UnkownPASDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float = 1.0):
        self.num_distractor_factor = num_distractor_factor

    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]
        all_formulas = [node.formula for node in proof_tree.nodes]

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
                 num_distractor_factor: int,
                 max_retry: int = 100):
        self.num_distractor_factor = num_distractor_factor
        self.max_retry = max_retry

    @profile
    def generate(self, proof_tree: ProofTree) -> List[Formula]:
        formulas_in_tree = [node.formula for node in proof_tree.nodes]
        leaf_formulas = [node.formula for node in proof_tree.leaf_nodes]

        num_distractors = int(len(leaf_formulas) * self.num_distractor_factor)

        leaf_formulas = shuffle(leaf_formulas)
        distractor_formulas: List[Formula] = []

        # TODO: constが変わるのに偏りすぎる

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

                    if is_formula_set_nonsense([transformed_formula] + distractor_formulas + formulas_in_tree):
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
