from typing import List, Dict, Optional, Tuple
from abc import abstractmethod, ABC
import logging

from FLD.formula import Formula

from FLD.exception import FormalLogicExceptionBase
from FLD.utils import run_with_timeout_retry, RetryAndTimeoutFailure

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
                  raise_if_translation_not_found=True,
                  max_retry: Optional[int] = 3,
                  timeout: Optional[int] = 10) -> Tuple[List[Tuple[Optional[str], Optional[str], Optional[Formula]]],
                                                        Dict[str, int]]:
        try:
            return run_with_timeout_retry(
                self._translate,
                func_args=[formulas],
                func_kwargs={'raise_if_translation_not_found': raise_if_translation_not_found},
                retry_exception_class=TranslationFailure,
                max_retry=max_retry,
                timeout=timeout,
                logger=logger,
                log_title='_translate()',
            )
        except RetryAndTimeoutFailure as e:
            raise TranslationFailure(str(e))

    @abstractmethod
    def _translate(self, formulas: List[Formula], raise_if_translation_not_found=True) -> Tuple[List[Tuple[Optional[str], Optional[str]]],
                                                                                                Dict[str, int]]:
        pass
