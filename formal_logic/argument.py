from typing import List

from .formula import Formula


class Argument:

    def __init__(self,
                 premises: List[Formula],
                 conclusion: Formula):
        self.premises = premises
        self.conclusion = conclusion

    def __str__(self) -> str:
        return f'Argument(premises={str(self.premises)}, conclusion={str(self.conclusion)})'

    def __repr__(self) -> str:
        return str(self)

    @property
    def all_formulas(self) -> List[Formula]:
        return self.premises + [self.conclusion]
