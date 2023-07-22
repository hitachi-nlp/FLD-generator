from typing import List, Dict, Optional, Tuple
import re
from abc import abstractmethod, ABC
import logging
from string import ascii_uppercase

from FLD_generator.formula import Formula

from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.utils import run_with_timeout_retry, RetryAndTimeoutFailure

logger = logging.getLogger(__name__)


def calc_formula_specificity(formula: Formula) -> float:
    """ Caluculate the specificity of the formula.

    Examples:
        {F}{a} -> {G}{a} is more specific than {F}{a} -> {G}{b},
        since the former is constrained version of the latter as {a}={b}
    """
    return - float(len(formula.predicates) + len(formula.constants))


class TranslationFailure(FormalLogicExceptionBase):
    pass


class TranslationImpossible(FormalLogicExceptionBase):
    pass


class TranslationNotFoundError(FormalLogicExceptionBase):
    pass


class Translator(ABC):

    def __init__(self, log_stats=False):
        self.log_stats = log_stats

    @property
    @abstractmethod
    def acceptable_formulas(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def translation_names(self) -> List[str]:
        pass

    def translate(self,
                  formulas: List[Formula],
                  intermediate_constant_formulas: List[Formula],
                  raise_if_translation_not_found=True,
                  max_retry: Optional[int] = 3,
                  timeout_per_trial: Optional[int] = 20) -> Tuple[List[Tuple[Optional[str], Optional[str], Optional[Formula]]],
                                                        Dict[str, int]]:
        try:
            transls = run_with_timeout_retry(
                self._translate,
                func_args=[formulas, intermediate_constant_formulas],
                func_kwargs={'raise_if_translation_not_found': raise_if_translation_not_found},
                should_retry_exception=TranslationFailure,
                max_retry=max_retry,
                timeout_per_trial=timeout_per_trial,
                logger=logger,
                log_title='_translate()',
            )
            if len(transls) == 0:
                raise TranslationFailure()
            return transls[-1]
        except RetryAndTimeoutFailure as e:
            raise TranslationFailure(str(e))

    @abstractmethod
    def _translate(self,
                   formulas: List[Formula],
                   intermediate_constant_formulas: List[Formula],
                   raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str], Optional[Formula]]], Dict[str, int]]:
        pass
