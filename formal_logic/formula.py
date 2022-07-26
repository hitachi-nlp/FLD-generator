import re
from typing import List, Optional


PREDICATE_POOL = ['F', 'G', 'H', 'I', 'J',
                  'K', 'L', 'M', 'N', 'O',
                  'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W']
CONSTANT_POOL = ['a', 'b', 'c', 'd', 'e',
                 'f', 'g', 'h', 'i', 'j',
                 'k', 'l', 'm', 'n', 'o',
                 'p', 'q', 'r', 's', 't',
                 'u', 'v', 'w']


class Formula:

    def __init__(self, formula_str: str):
        if _is_template(formula_str):
            raise Exception('The input string is template. De-template it by detemplatify().')
        # formula_str is like "(x): (${F}x v ${H}x) -> ${G}x"
        self._formula_str = formula_str

    @property
    def rep(self) -> str:
        return self._formula_str

    def __str__(self) -> str:
        return f'Formula("{self._formula_str}")'

    def __repr__(self) -> str:
        return f'Formula("{self._formula_str}")'

    # def __eq__(self, other):
    #     return self.rep == other.rep

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


def templatify(rep: str) -> str:
    converted = ''
    variables = _get_variables(rep)
    for char in rep:
        if _is_predicate_char(char) or (_is_individual_char(char) and char not in variables):
            converted += '${' + char + '}'
        else:
            converted += char
    return converted


def detemplatify(rep: str) -> str:
    return re.sub(r'[{}\$]', '', re.sub(r'\$', '', rep))


def _get_premise(rep) -> Optional[str]:
    if rep.find('->') < 0:
        return None
    return ' -> '.join(rep.split(' -> ')[:-1])


def _get_conclusion(rep) -> Optional[str]:
    if rep.find('->') < 0:
        return None
    return rep.split(' -> ')[-1]


def _get_predicates(rep) -> List[str]:
    predicate_reps = set()
    for char in rep:
        if _is_predicate_char(char):
            predicate_reps.add(char)
    return sorted(predicate_reps)


def _get_constants(rep: str) -> List[str]:
    constant_reps = set()
    variables = _get_variables(rep)
    for char in rep:
        if _is_individual_char(char) and char not in variables:
            constant_reps.add(char)
    return sorted(constant_reps)


def _get_variables(rep: str) -> List[str]:
    unique_variables = set()

    # "(x)"
    matches = re.finditer(r'\([a-z]*\)', rep)
    unique_variables = unique_variables.union(
        set([m.group()[1] for m in matches])
    )

    # "(Ex)"
    matches = re.finditer(r'\(E[a-z]*\)', rep)
    unique_variables = unique_variables.union(
        set([m.group()[2] for m in matches])
    )

    return sorted(unique_variables)


def _is_predicate_char(char: str) -> bool:
    return re.match(r'[A-Z]', char) is not None


def _is_individual_char(char: str) -> bool:
    """ individuals = constants + variables """
    return re.match(r'[a-z]', char) is not None


def _is_template(rep: str) -> bool:
    return re.match(r'[{}\$]', rep) is not None


def is_satisfiable(formulas: List[Formula]) -> bool:
    # TODO: きちんとやる．今は，{Ga, ¬Ga} のチェックのみを行っている．
    single_terms = [formula.rep for formula in formulas]
    for i_this_term, this_term in enumerate(single_terms):
        for that_term in single_terms[i_this_term + 1:]:
            if this_term == f'¬{that_term}' or that_term == f'¬{this_term}':
                return False
    return True
