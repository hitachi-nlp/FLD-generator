import re
from typing import List, Optional

IMPLICATION = '->'
AND = '&'
OR = 'v'
NOT = '¬'

PREDICATE_SYMBOLS = [
    '{A}', '{B}', '{C}', '{D}', '{E}',
    '{F}', '{G}', '{H}', '{I}', '{J}',
    '{K}', '{L}', '{M}', '{N}', '{O}',
    '{P}', '{Q}', '{R}', '{S}', '{T}', '{U}',
]
_PREDICATE_REGEXP = re.compile('|'.join(PREDICATE_SYMBOLS))

CONSTANT_SYMBOLS = [
    '{a}', '{b}', '{c}', '{d}', '{e}',
    '{f}', '{g}', '{h}', '{i}', '{j}',
    '{k}', '{l}', '{m}', '{n}', '{o}',
    '{p}', '{q}', '{r}', '{s}', '{t}', '{u}',
]  # do not use 'v' = OR
_CONSTANT_REGEXP = re.compile('|'.join(CONSTANT_SYMBOLS))

VARIABLE_SYMBOLS = ['x', 'y', 'z']  # do not use 'v' = OR
_VARIABLE_REGEXP = re.compile('|'.join(VARIABLE_SYMBOLS))


class Formula:

    def __init__(self,
                 formula_str: str,
                 translation: Optional[str] = None):
        self._formula_str = formula_str
        self.translation = translation

    @property
    def rep(self) -> str:
        return self._formula_str

    def __str__(self) -> str:
        transl_repr = '"' + self.translation + '"' if self.translation is not None else 'None'
        return f'Formula("{self._formula_str}", transl={transl_repr})'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def premise(self) -> Optional['Formula']:
        if _get_premise(self.rep) is not None:
            return Formula(_get_premise(self.rep))
        else:
            return None

    @property
    def conclusion(self) -> Optional['Formula']:
        if _get_conclusion(self.rep) is not None:
            return Formula(_get_conclusion(self.rep))
        else:
            return None

    @property
    def predicates(self) -> List['Formula']:
        return [Formula(rep) for rep in _get_predicates(self.rep)]

    @property
    def constants(self) -> List['Formula']:
        return [Formula(rep) for rep in _get_constants(self.rep)]

    @property
    def variables(self) -> List['Formula']:
        return [Formula(rep) for rep in _get_variables(self.rep)]


def _get_premise(rep) -> Optional[str]:
    if rep.find('->') < 0:
        return None
    return ' -> '.join(rep.split(' -> ')[:-1])


def _get_conclusion(rep) -> Optional[str]:
    if rep.find('->') < 0:
        return None
    return rep.split(' -> ')[-1]


def _get_predicates(rep: str) -> List[str]:
    return sorted(set(_PREDICATE_REGEXP.findall(rep)))


def _get_constants(rep: str) -> List[str]:
    return sorted(set(_CONSTANT_REGEXP.findall(rep)))


def _get_variables(rep: str) -> List[str]:
    return sorted(set(_VARIABLE_REGEXP.findall(rep)))


def is_satisfiable(formulas: List[Formula]) -> bool:
    # TODO: きちんとやる．今は，{Ga, ¬Ga} のチェックのみを行っている．
    single_terms = [formula.rep for formula in formulas]
    for i_this_term, this_term in enumerate(single_terms):
        for that_term in single_terms[i_this_term + 1:]:
            if this_term == f'¬{that_term}' or that_term == f'¬{this_term}':
                return False
    return True
