import re
from typing import List, Optional
from functools import lru_cache

from FLD_generator.exception import FormalLogicExceptionBase
import line_profiling


IMPLICATION = '->'
CONJUNCTION = '&'
DISJUNCTION = 'v'
NEGATION = '¬'
DERIVE = '⊢'
CONTRADICTION = '#F#'

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
][:200]
_PREDICATE_REGEXP = re.compile('|'.join(PREDICATES))

# XXX: do not use 'v', which is reserved for OR.
# XXX: The number of symbols of constants must be similar to that of predicates
# to make sure that when we sample symbols from constants + predicates, it is unique.
# for example we sample symbols in distractors.UnkownPASDistractor or distractors.SameFormUnkownInterprandsDistractor
_CONSTANT_ALPHABETS = [
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u',
]
CONSTANTS = [
    f'{{{char}}}'
    for char in _CONSTANT_ALPHABETS
] + [
    f'{{{char0}{char1}}}'
    for char0 in _CONSTANT_ALPHABETS
    for char1 in _CONSTANT_ALPHABETS
][:200]
# CONSTANTS = [
#     '{a}', '{b}', '{c}', '{d}', '{e}',
#     '{f}', '{g}', '{h}', '{i}', '{j}',
#     '{k}', '{l}', '{m}', '{n}', '{o}',
#     '{p}', '{q}', '{r}', '{s}', '{t}', '{u}',
# ]  # do not use 'v' = OR


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

_QUANTIFIER_INTRO_REGEXP = re.compile(
    '|'.join([f'\({variable}\): ' for variable in VARIABLES]\
             + [f'\(E{variable}\): ' for variable in VARIABLES])
)


class ContradictionNegationError(FormalLogicExceptionBase):
    pass


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
    def quantifiers(self) -> List[str]:
        return self.existential_quantifiers + self.universal_quantifiers

    @property
    def existential_quantifiers(self) -> List[str]:
        return _EXISTENTIAL_QUENTIFIER_REGEXP.findall(self.rep)

    @property
    def universal_quantifiers(self) -> List[str]:
        return _UNIVERSAL_QUENTIFIER_REGEXP.findall(self.rep)

    @property
    def wo_quantifier(self) -> 'Formula':
        return Formula(strip_quantifier(self.rep))

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
    return Formula(re.sub(f'{NEGATION}{NEGATION}', '', formula.rep))


def negate(formula: Formula,
           require_brace_for_single_predicate=False,
           require_brace_for_negated_formula=False) -> Formula:
    if is_contradiction_symbol(formula):
        raise ContradictionNegationError(f'Contradiction {CONTRADICTION} can not be negated.')

    if require_outer_brace(formula,
                           require_for_single_predicate=require_brace_for_single_predicate,
                           require_for_negated_formula=require_brace_for_negated_formula):
        return Formula(NEGATION + '(' + formula.rep + ')')
    else:
        return Formula(NEGATION + formula.rep)


def require_outer_brace(formula: Formula,
                        require_for_single_predicate=False,
                        require_for_negated_formula=False) -> bool:
    if not require_for_single_predicate\
            and len(formula.PASs) == 1 and formula.rep == formula.PASs[0].rep:
        # "{A}"
        # "{A}{a}'
        return False

    elif not require_for_negated_formula and formula.rep.startswith(NEGATION):
        # "¬({A} v {B})" vs "¬{A} & {B}"
        return require_outer_brace(Formula(formula.rep.lstrip(NEGATION)),
                                   require_for_single_predicate=require_for_single_predicate,
                                   require_for_negated_formula=require_for_negated_formula)

    elif formula.rep.startswith('('):
        level = 0
        for i_char, char in enumerate(formula.rep):
            if i_char == 0:
                level += 1
                continue

            if char == '(':
                level += 1
            elif char == ')':
                level -= 1

            is_final_char = i_char == len(formula.rep) - 1

            if level == 0 and not is_final_char:
                # "({A} & {B}) & C"
                return True

            if is_final_char:
                if level == 0:
                    # "({A} & {B})"
                    return False
                else:
                    raise ValueError(f'formula {formula.rep} has unbalanced braces ().')

        raise Exception('The program must not pass here.')

    else:
        return True


def is_contradiction_symbol(formula: Formula) -> bool:
    return formula.rep == CONTRADICTION


def has_contradiction_symbol(formula: Formula) -> bool:
    return formula.rep.find(CONTRADICTION) >= 0


@lru_cache(maxsize=10000000)
def strip_quantifier(rep: str) -> str:
    return _QUANTIFIER_INTRO_REGEXP.sub('', rep)
