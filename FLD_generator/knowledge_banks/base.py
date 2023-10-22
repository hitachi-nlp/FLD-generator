from typing import List, Dict, Optional, Tuple
from abc import abstractmethod, ABC
import logging

from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.formula import Formula
from FLD_generator.word_banks import POS
from FLD_generator.translators.base import (
    Phrase,
    PredicatePhrase,
    ConstantPhrase,
)

logger = logging.getLogger(__name__)


class KnowledgeMappingFailure(FormalLogicExceptionBase):
    pass


class KnowledgeMappingImpossible(FormalLogicExceptionBase):
    pass


class KnowledgeBankBase(ABC):

    @abstractmethod
    def is_acceptable(self, formulas: List[Formula]) -> bool:
        pass

    def sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Phrase], Dict[str, POS], List[bool]]:
        if not self.is_acceptable(formulas):
            raise KnowledgeMappingImpossible()
        return self._sample_mapping(formulas)

    @abstractmethod
    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Phrase], Dict[str, POS], List[bool]]:
        pass
