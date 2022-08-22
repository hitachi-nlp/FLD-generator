import re
from typing import List, Optional, Set

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

PREDICATE_ARGUMENTS = [
    f'{pred}{arg}'
    for pred in PREDICATES
    for arg in CONSTANTS + VARIABLES + ['']
]
_PREDICATE_ARGUMENT_REGEXP = re.compile('|'.join(PREDICATE_ARGUMENTS))

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
        if self._find_premise_rep(self.rep) is not None:
            return Formula(self._find_premise_rep(self.rep))
        else:
            return None

    def _find_premise_rep(self, rep) -> Optional[str]:
        if rep.find(IMPLICATION) < 0:
            return None
        return f' {IMPLICATION} '.join(rep.split(f' {IMPLICATION} ')[:-1])

    @property
    def conclusion(self) -> Optional['Formula']:
        if self._find_conclusion_rep(self.rep) is not None:
            return Formula(self._find_conclusion_rep(self.rep))
        else:
            return None

    def _find_conclusion_rep(self, rep) -> Optional[str]:
        if rep.find(IMPLICATION) < 0:
            return None
        return rep.split(f' {IMPLICATION} ')[-1]

    @property
    def predicates(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find_predicate_reps(self.rep)]

    def _find_predicate_reps(self, rep: str) -> List[str]:
        return sorted(set(_PREDICATE_REGEXP.findall(rep)))

    @property
    def zeroary_predicates(self) -> List['Formula']:
        return [predicate for predicate in self.predicates
                if all((f'{predicate.rep}{argument}' not in self.rep for argument in VARIABLES + CONSTANTS))]

    @property
    def unary_predicates(self) -> List['Formula']:
        return [predicate for predicate in self.predicates
                if any((f'{predicate.rep}{argument}' in self.rep for argument in VARIABLES + CONSTANTS))]

    @property
    def constants(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find_constant_reps(self.rep)]

    def _find_constant_reps(self, rep: str) -> List[str]:
        return sorted(set(_CONSTANT_REGEXP.findall(rep)))

    @property
    def PASs(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find_PAS_reps(self.rep)]

    def _find_PAS_reps(self, rep: str) -> List[str]:
        return sorted(set(_PREDICATE_ARGUMENT_REGEXP.findall(rep)))

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

    @property
    def variables(self) -> List['Formula']:
        return [Formula(rep) for rep in self._find_variable_reps(self.rep)]

    def _find_variable_reps(self, rep: str) -> List[str]:
        return sorted(set(_VARIABLE_REGEXP.findall(rep)))

    @property
    def existential_variables(self) -> List['Formula']:
        return [Formula(rep[2:-1]) for rep in self._find_existential_quantifier_reps(self.rep)]

    def _find_existential_quantifier_reps(self, rep: str) -> List[str]:
        return sorted(set(_EXISTENTIAL_QUENTIFIER_REGEXP.findall(rep)))

    @property
    def universal_variables(self) -> List['Formula']:
        return [Formula(rep[1:-1]) for rep in self._find_universal_quantifier_reps(self.rep)]

    def _find_universal_quantifier_reps(self, rep: str) -> List[str]:
        return sorted(set(_UNIVERSAL_QUENTIFIER_REGEXP.findall(rep)))

    @property
    def wo_quantifier(self) -> 'Formula':
        return Formula(self.rep.split(': ')[-1])

    @property
    def interprands(self) -> List['Formula']:
        return self.predicates + self.constants



def eliminate_double_negation(formula: Formula) -> Formula:
    return Formula(re.sub(f'{NOT}{NOT}', '', formula.rep))
