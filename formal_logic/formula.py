import re
from typing import List, Optional

IMPLICATION = '->'
AND = '&'
OR = 'v'
NOT = '¬'

_PREDICATE_ALPHABETS = [
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T', 'U',
]
PREDICATES = [
    f'{{{char}}}'
    for char in _PREDICATE_ALPHABETS
] + [
    f'{{{char0}{char1}}}'
    for char0 in _PREDICATE_ALPHABETS
    for char1 in _PREDICATE_ALPHABETS
]
_PREDICATE_REGEXP = re.compile('|'.join(PREDICATES))

CONSTANTS = [
    '{a}', '{b}', '{c}', '{d}', '{e}',
    '{f}', '{g}', '{h}', '{i}', '{j}',
    '{k}', '{l}', '{m}', '{n}', '{o}',
    '{p}', '{q}', '{r}', '{s}', '{t}', '{u}',
]  # do not use 'v' = OR
_CONSTANT_REGEXP = re.compile('|'.join(CONSTANTS))

VARIABLES = ['x', 'y', 'z']  # do not use 'v' = OR
_VARIABLE_REGEXP = re.compile('|'.join(VARIABLES))

PASs = [
    f'{pred}{arg}'
    for pred in PREDICATES
    for arg in CONSTANTS + VARIABLES + ['']
]
_PAS_REGEXP = re.compile('|'.join(PASs))

_UNARY_PAS_REGEXPs = {
    f'{pred}': re.compile(
        '|'.join([
            f'{pred}{arg}'
            for arg in CONSTANTS + VARIABLES
        ])
    )
    for pred in PREDICATES
}

_UNIVERSAL_QUENTIFIER_REGEXP = re.compile(
    '|'.join([f'\({variable}\)' for variable in VARIABLES])
)

_EXISTENTIAL_QUENTIFIER_REGEXP = re.compile(
    '|'.join([f'\(E{variable}\)' for variable in VARIABLES])
)


class Formula:

    def __init__(self,
                 formula_str: str,
                 translation: Optional[str] = None,
                 translation_name: Optional[str] = None):
        self._formula_str = formula_str
        self.translation = translation
        self.translation_name = translation_name

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
        if self.rep.find(IMPLICATION) < 0:
            return None
        else:
            return Formula(f' {IMPLICATION} '.join(self.rep.split(f' {IMPLICATION} ')[:-1]))

    @property
    def conclusion(self) -> Optional['Formula']:
        if self.rep.find(IMPLICATION) < 0:
            return None
        else:
            return Formula(self.rep.split(f' {IMPLICATION} ')[-1])

    @property
    def wo_quantifier(self) -> 'Formula':
        return Formula(self.rep.split(': ')[-1])

    @property
    def predicates(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find(_PREDICATE_REGEXP)]

    @property
    def zeroary_predicates(self) -> List['Formula']:
        unary_predicate_reps = {predicate.rep for predicate in self.unary_predicates}
        return [predicate for predicate in self.predicates
                if predicate.rep not in unary_predicate_reps]
        # return [predicate for predicate in self.predicates
        #         if all((f'{predicate.rep}{argument}' not in self.rep for argument in VARIABLES + CONSTANTS))]

    @property
    def unary_predicates(self) -> List['Formula']:
        return [predicate for predicate in self.predicates
                if _UNARY_PAS_REGEXPs[predicate.rep].search(self.rep)]

    @property
    def constants(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find(_CONSTANT_REGEXP)]

    @property
    def interprands(self) -> List['Formula']:
        return self.predicates + self.constants

    @property
    def variables(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find(_VARIABLE_REGEXP)]

    @property
    def existential_variables(self) -> List['Formula']:
        return [Formula(rep[2:-1]) for rep in self._find(_EXISTENTIAL_QUENTIFIER_REGEXP)]

    @property
    def universal_variables(self) -> List['Formula']:
        return [Formula(rep[1:-1]) for rep in self._find(_UNIVERSAL_QUENTIFIER_REGEXP)]

    @property
    def PASs(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find(_PAS_REGEXP)]

    @property
    def zeroary_PASs(self) -> List['Formula']:
        return self.zeroary_predicates

    @property
    def unary_PASs(self) -> List['Formula']:
        return [PAS for PAS in self.PASs
                if PAS not in self.zeroary_predicates]

    @property
    def interprand_PASs(self) -> List['Formula']:
        return [PAS for PAS in self.PASs
                if len(PAS.variables) == 0]

    @property
    def zeroary_interprand_PASs(self) -> List['Formula']:
        return self.zeroary_predicates

    @property
    def unary_interprand_PASs(self) -> List['Formula']:
        return [PAS for PAS in self.unary_PASs
                if len(PAS.variables) == 0]

    def _find(self, regexp) -> List[str]:
        return sorted(set(regexp.findall(self.rep)))


def eliminate_double_negation(formula: Formula) -> Formula:
    return Formula(re.sub(f'{NOT}{NOT}', '', formula.rep))
