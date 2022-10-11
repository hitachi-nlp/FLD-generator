from typing import Optional, Iterable, List, Union
from enum import Enum
from abc import ABC, abstractmethod


class POS(Enum):
    VERB = 'VERB'
    NOUN = 'NOUN'
    ADJ = 'ADJ'
    ADJ_SAT = 'ADJ_SAT'
    UNK = 'UNK'


class ATTR(Enum):
    can_be_transitive_verb = 'can_be_transitive_verb'
    can_be_intransitive_verb = 'can_be_intransitive_verb'

    can_be_event_noun = 'can_be_event_noun'
    can_be_entity_noun = 'can_be_entity_noun'


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
    SINGULAR = 's'
    SINGULAR_WITH_PARTICLE = 'swa'


def get_form_types(pos: POS) -> Union[VerbForm, AdjForm, NounForm]:
    if pos == POS.VERB:
        return VerbForm
    elif pos in [POS.ADJ, POS.ADJ_SAT]:
        return AdjForm
    elif pos == POS.NOUN:
        return NounForm
    elif pos == POS.UNK:
        return None
    else:
        raise ValueError(f'Unknown pos {pos}')


class WordBank(ABC):

    @abstractmethod
    def get_words(self) -> Iterable[str]:
        pass

    @abstractmethod
    def get_pos(self, word: str) -> List[POS]:
        pass

    def change_word_form(self,
                         word: str,
                         form: Union[VerbForm, AdjForm, NounForm],
                         force=False) -> Optional[str]:
        if form in VerbForm:
            if POS.VERB not in self.get_pos(word):
                raise ValueError(f'The pos of the form ({str(form)}) is Verb. The word {word} does not have this pos.')
            return self._change_verb_form(word, form, force=force)
        elif form in AdjForm:
            if POS.ADJ not in self.get_pos(word) and POS.ADJ_SAT not in self.get_pos(word):
                raise ValueError(f'The pos of the form ({str(form)}) is Adj. The word {word} does not have this pos.')
            return self._change_adj_form(word, form, force=force)
        elif form in NounForm:
            if POS.NOUN not in self.get_pos(word):
                raise ValueError(f'The pos of the form ({str(form)}) is Noun. The word {word} does not have this pos.')
            return self._change_noun_form(word, form, force=force)
        else:
            raise ValueError()

    @abstractmethod
    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        pass

    @abstractmethod
    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        pass

    @abstractmethod
    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        pass

    def get_attrs(self, word: str) -> List[ATTR]:
        attrs = []
        if POS.VERB in self.get_pos(word) and self._can_be_intransitive_verb(word):
            attrs.append(ATTR.can_be_intransitive_verb)
        if POS.VERB in self.get_pos(word) and self._can_be_transitive_verb(word):
            attrs.append(ATTR.can_be_transitive_verb)
        if POS.NOUN in self.get_pos(word) and self._can_be_event_noun(word):
            attrs.append(ATTR.can_be_event_noun)
        if POS.NOUN in self.get_pos(word) and self._can_be_entity_noun(word):
            attrs.append(ATTR.can_be_entity_noun)
        return attrs

    @abstractmethod
    def _can_be_intransitive_verb(self, verb: str) -> bool:
        pass

    @abstractmethod
    def _can_be_transitive_verb(self, verb: str) -> bool:
        pass

    @abstractmethod
    def _can_be_event_noun(self, noun: str) -> bool:
        pass

    @abstractmethod
    def _can_be_entity_noun(self, noun: str) -> bool:
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
