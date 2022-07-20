import re
from typing import List, Optional


class Formula:

    def __init__(self, formula_str: str):
        # formula_str is like "(x): (${F}x v ${H}x) -> ${G}x"
        self._formula_str = formula_str

    @property
    def rep(self) -> str:
        return self._formula_str

    def __str__(self) -> str:
        # only for printing
        return f'Formula("{self._formula_str}")'

    def __repr__(self) -> str:
        # only for printing
        return f'Formula("{self._formula_str}")'

    @property
    def premise(self) -> Optional['Formula']:
        if self._formula_str.find('->') < 0:
            return None
        return Formula(' -> '.join(self._formula_str.split(' -> ')[:-1]))

    @property
    def conclusion(self) -> Optional['Formula']:
        if self._formula_str.find('->') < 0:
            return None
        return Formula(self._formula_str.split(' -> ')[-1])

    @property
    def predicates(self) -> List['Formula']:
        matches = re.finditer(r'\${[^}]*}', self._formula_str)
        unique_preds = set(
            [m.group() for m in matches
             if m.group().isupper()]
        )
        return [Formula(rep)
                for rep in sorted(unique_preds)]

    @property
    def constants(self) -> List['Formula']:
        matches = re.finditer(r'\${[^}]*}', self._formula_str)
        unique_constants = set([m.group() for m in matches
                                if m.group().islower()])

        return [Formula(rep)
                for rep in sorted(unique_constants)]

    @property
    def variables(self) -> List['Formula']:
        unique_variables = set()

        # "(x)"
        matches = re.finditer(r'\([xyz]*\)', self._formula_str)
        unique_variables = unique_variables.union(
            set([m.group()[1] for m in matches])
        )

        # "(Ex)"
        matches = re.finditer(r'\(E[xyz]*\)', self._formula_str)
        unique_variables = unique_variables.union(
            set([m.group()[2] for m in matches])
        )

        return [Formula(rep)
                for rep in sorted(unique_variables)]
