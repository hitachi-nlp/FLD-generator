from typing import List, Dict, Optional, Tuple
from abc import abstractmethod, ABC
import logging

from FLNL.formula import Formula

from FLNL.exception import FormalLogicExceptionBase

logger = logging.getLogger(__name__)


def calc_formula_specificity(formula: Formula) -> float:
    """ Caluculate the specificity of the formula.

    Examples:
        {F}{a} -> {G}{a} is more specific than {F}{a} -> {G}{b},
        since the former is constrained version of the latter as {a}={b}
    """
    return - float(len(formula.predicates) + len(formula.constants))


class TranslationNotFoundError(FormalLogicExceptionBase):
    pass


class Translator(ABC):

    @property
    @abstractmethod
    def acceptable_formulas(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def translation_names(self) -> List[str]:
        pass

    @abstractmethod
    def translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                               Dict[str, int]]:
        pass


