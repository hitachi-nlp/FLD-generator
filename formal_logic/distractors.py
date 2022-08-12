from typing import List
from abc import abstractmethod, ABC
import random

from .formula import Formula, PREDICATES, CONSTANTS


class FormalLogicDistractor(ABC):

    @abstractmethod
    def generate(self, formulas: List[Formula], num: int) -> List[Formula]:
        pass


class UnknownFactDistractor(FormalLogicDistractor):
    """When {G}{a} is already in tree, we add {G}{b} or {H}{a}"""

    def generate(self, formulas: List[Formula], num: int) -> List[Formula]:
        known_predicates = sorted({
            pred.rep
            for formula in formulas
            for pred in formula.predicates
        })
        unknown_predicates = sorted(set(PREDICATES) - set(known_predicates))

        known_constants = sorted({
            pred.rep
            for formula in formulas
            for pred in formula.constants
        })
        unknown_constants = sorted(set(CONSTANTS) - set(known_constants))

        unknown_combinations: List[Formula] = []
        for predicate in known_predicates:
            for constant in known_constants:
                fact_rep = f'{predicate}{constant}'

                if all((fact_rep not in formula.rep for formula in formulas + unknown_combinations)):
                    unknown_combinations.append(Formula(fact_rep))

        other_unknown_combinations = []
        for predicate in unknown_predicates:
            for constant in known_constants:
                other_unknown_combinations.append(Formula(f'{predicate}{constant}'))
        for predicate in known_predicates:
            for constant in unknown_constants:
                fact_rep = f'{predicate}{constant}'
                other_unknown_combinations.append(Formula(f'{predicate}{constant}'))

        random.shuffle(unknown_combinations)
        random.shuffle(other_unknown_combinations)

        return (unknown_combinations + other_unknown_combinations)[:num]
