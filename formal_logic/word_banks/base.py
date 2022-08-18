from typing import Optional, Iterable, List, Dict
from enum import Enum
from abc import ABC, abstractmethod


class POS(Enum):
    VERB = 'VERB'
    NOUN = 'NOUN'
    ADJ = 'ADJ'


class VerbForm(Enum):
    """ https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html """
    NORMAL = 'normal'
    ING = 'ing'
    S = 's'


class AdjForm(Enum):
    NORMAL = 'normal'
    NESS = 'ness'
    NEG = 'neg'


class NounForm(Enum):
    NORMAL = 'normal'


class WordBank(ABC):

    @abstractmethod
    def get_words(self, pos: Optional[POS] = None) -> Iterable[str]:
        pass

    @abstractmethod
    def get_pos(self, word: str) -> List[POS]:
        pass

    @abstractmethod
    def get_synonyms(self, word: str) -> List[str]:
        pass

    @abstractmethod
    def get_antonyms(self, word: str) -> List[str]:
        pass

    @abstractmethod
    def get_negnyms(self, word: str) -> List[str]:
        # might be the subset of antonyms.
        # antonyms may include words such as alkaline being antonym to acidic.
        # negnym exclude such ones and include only the words like inaccrate being a negnym to accurate.
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

    def change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        if POS.NOUN not in self.get_pos(noun):
            raise ValueError()
        return self._change_noun_form(noun, form, force=force)

    @abstractmethod
    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        pass

    def can_be_intransitive_verb(self, verb: str) -> bool:
        if POS.VERB not in self.get_pos(verb):
            raise ValueError()
        return self._can_be_intransitive_verb(verb)

    @abstractmethod
    def _can_be_intransitive_verb(self, verb: str) -> bool:
        pass

    def can_be_event_noun(self, noun: str) -> bool:
        if POS.NOUN not in self.get_pos(noun):
            raise ValueError()
        return self._can_be_event_noun(noun)

    @abstractmethod
    def _can_be_event_noun(self, noun: str) -> bool:
        pass

    def can_be_entity_noun(self, noun: str) -> bool:
        if POS.NOUN not in self.get_pos(noun):
            raise ValueError()
        return self._can_be_entity_noun(noun)

    @abstractmethod
    def _can_be_entity_noun(self, noun: str) -> bool:
        pass
