from typing import List
from abc import abstractmethod, ABC
import random

from .formula import Formula, PREDICATES, CONSTANTS


class FormalLogicDistractor(ABC):

    @abstractmethod
    def generate(self, formulas: List[Formula]) -> List[Formula]:
        pass


class UnknownFactDistractor(FormalLogicDistractor):

    def __init__(self, num_distractor_factor: float = 1.0):
        self.num_distractor_factor = num_distractor_factor

    def generate(self, formulas: List[Formula]) -> List[Formula]:
        known_zeroary_predicates = sorted({
            pred.rep
            for formula in formulas
            for pred in formula.zeroary_predicates
        })
        unused_predicates = sorted(set(PREDICATES) - set(known_zeroary_predicates))
        random.shuffle(unused_predicates)

        num_zeroary_distractors = len(known_zeroary_predicates) * self.num_distractor_factor
        distractor_zeroary_predicates = unused_predicates[:int(num_zeroary_distractors)]
        zeroary_distractors = [Formula(f'{predicate}') for predicate in distractor_zeroary_predicates]

        unary_PASs = sorted({
            PAS.rep
            for formula in formulas
            for PAS in formula.unary_interprand_PASs
        })
        known_unary_predicates = sorted({
            pred.rep
            for formula in formulas
            for pred in formula.unary_predicates
        })
        unused_predicates = sorted(set(PREDICATES) - set(known_unary_predicates) - set(distractor_zeroary_predicates))

        known_constants = sorted({
            pred.rep
            for formula in formulas
            for pred in formula.constants
        })
        unused_constants = sorted(set(CONSTANTS) - set(known_constants))

        in_domain_unused_PASs: List[Formula] = []
        for predicate in known_unary_predicates:
            for constant in known_constants:
                fact_rep = f'{predicate}{constant}'

                if all((fact_rep not in formula.rep for formula in formulas + in_domain_unused_PASs)):
                    in_domain_unused_PASs.append(Formula(fact_rep))

        outof_domain_unused_PASs = []
        for predicate in unused_predicates:
            for constant in known_constants:
                outof_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))
        for predicate in known_unary_predicates:
            for constant in unused_constants:
                fact_rep = f'{predicate}{constant}'
                outof_domain_unused_PASs.append(Formula(f'{predicate}{constant}'))

        random.shuffle(in_domain_unused_PASs)
        random.shuffle(outof_domain_unused_PASs)
        num_unary_distractors = len(unary_PASs) * self.num_distractor_factor
        unary_distractors = (in_domain_unused_PASs + outof_domain_unused_PASs)[:int(num_unary_distractors)]

        return zeroary_distractors + unary_distractors
