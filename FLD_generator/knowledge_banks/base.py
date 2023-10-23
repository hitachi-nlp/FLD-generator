from typing import List, Dict, Optional, Tuple
from abc import abstractmethod, ABC
import logging
from pydantic import BaseModel

from FLD_generator.exception import FormalLogicExceptionBase
from FLD_generator.formula import Formula
from FLD_generator.word_banks import POS
from FLD_generator.translators.base import Phrase

logger = logging.getLogger(__name__)


class KnowledgeMappingFailure(FormalLogicExceptionBase):
    pass


class KnowledgeMappingImpossible(FormalLogicExceptionBase):
    pass


class KnowledgeBankBase(ABC):

    @abstractmethod
    def is_acceptable(self, formulas: List[Formula]) -> bool:
        pass

    def sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Tuple[Phrase, Optional[POS]]], List[bool]]:
        if not self.is_acceptable(formulas):
            raise KnowledgeMappingImpossible()
        return self._sample_mapping(formulas)

    @abstractmethod
    def _sample_mapping(self, formulas: List[Formula]) -> Tuple[Dict[str, Tuple[Phrase, Optional[POS]]], List[bool]]:
        pass


class Statement(BaseModel):
    subj: str
    subj_left_modif: Optional[str] = None
    subj_right_modif: Optional[str] = None

    verb: str
    verb_left_modif: Optional[str] = None
    verb_right_modif: Optional[str] = None


class IfThenStatement(BaseModel):
    if_statement: Statement
    then_statement: Statement
