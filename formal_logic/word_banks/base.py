from typing import Optional, Iterable, List
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


class AdjForm(Enum):
    NORMAL = 'NORMA'
    NESS = 'NESS'


class WordBank(ABC):

    @abstractmethod
    def get_words(self, pos: Optional[POS] = None) -> Iterable[str]:
        pass

    @abstractmethod
    def get_pos(self, word: str) -> List[POS]:
        pass

    def change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        if POS.VERB not in self.get_pos(verb):
            raise ValueError()
        return self._change_verb_form(verb, form, force=force)

    @abstractmethod
    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        pass

    def change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        if POS.ADJ not in self.get_pos(adj):
            raise ValueError()
        return self._change_adj_form(adj, form, force=force)

    @abstractmethod
    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        pass

    def can_be_intransitive_verb(self, verb: str) -> bool:
        if POS.VERB not in self.get_pos(verb):
            raise ValueError()
        return self._can_be_intransitive_verb(verb)

    @abstractmethod
    def _can_be_intransitive_verb(self, verb: str) -> bool:
        pass
