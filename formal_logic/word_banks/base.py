from typing import Optional, Iterable
from enum import Enum
from abc import ABC, abstractmethod


class POS(Enum):
    VERB = 'VERB'
    NOUN = 'NOUN'
    ADJ = 'ADJ'


class VerbForm(Enum):
    """ https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html """
    VB = 'VB'
    VBG = 'VBG'
    VBZ = 'VBZ'


class WordBank(ABC):

    @abstractmethod
    def get_words(self, pos: Optional[POS] = None) -> Iterable[str]:
        pass

    @abstractmethod
    def change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        pass

    @abstractmethod
    def can_be_intransitive_verb(self, verb: str) -> bool:
        pass
