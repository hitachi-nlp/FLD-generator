from typing import Optional, Iterable, List, Union
from enum import Enum, EnumMeta
from string import ascii_uppercase
from abc import ABC, abstractmethod
from itertools import chain
from functools import lru_cache
import logging
from ordered_set import OrderedSet

import line_profiling

logger = logging.getLogger(__name__)


class POS(Enum):
    # from nltk/corpus/reader/wordnet.py
    VERB = 'VERB'            # verbs (all tenses and modes)

    ADJ = 'ADJ'       # adjectives
    ADJ_SAT = 'ADJ_SAT'

    # He is running at the park
    # Note that we differenciate this from "VERB.ing"
    # as PRESENT_PARTICLE imply that the verb form "must be" PRESENT_PARTICLE_PARTICLE_particle form
    PRESENT_PARTICLE = 'PRESENT_PARTICLE'

    # an iron is "used" for cleaning
    PAST_PARTICLE = 'PAST_PARTICLE'

    ADV = 'ADV'       # adverbs

    NOUN = 'NOUN'     # nouns (common and proper)

    OTHERS = 'OTHERS'


class ATTR(Enum):
    can_be_transitive_verb = 'can_be_transitive_verb'
    can_be_intransitive_verb = 'can_be_intransitive_verb'

    can_be_event_noun = 'can_be_event_noun'
    can_be_entity_noun = 'can_be_entity_noun'


class WordBank(ABC):

    # implemente in the sub classes
    VerbForm: EnumMeta
    AdjForm: EnumMeta
    PresentForm: EnumMeta
    PastForm: EnumMeta
    NounForm: EnumMeta
    # INTERMEDIATE_CONSTANT_PREFIXES: List[str]

    def __init__(self):
        # self._intermediate_constant_words = OrderedSet([
        #     f'{prefix}-{alphabet}'
        #     for alphabet in ascii_uppercase
        #     for prefix in self.INTERMEDIATE_CONSTANT_PREFIXES
        # ])
        self._intermediate_constant_words = OrderedSet(
            ['X', 'Y', 'Z', 'W'] +
            ['X' + str(i) for i in range(2, 10)] +
            ['Y' + str(i) for i in range(2, 10)] +
            ['Z' + str(i) for i in range(2, 10)] +
            ['W' + str(i) for i in range(2, 10)]
        )

    def get_words(self) -> Iterable[str]:
        # enumerate base form of words
        yield from chain(self.get_intermediate_constant_words(), self._get_all_lemmas())

    @abstractmethod
    def _get_all_lemmas(self) -> Iterable[str]:
        # enumerate base form of words
        pass

    def get_intermediate_constant_words(self) -> Iterable[str]:
        return self._intermediate_constant_words

    @profile
    def get_pos(self, word: str, not_found_warning=True) -> List[POS]:
        if word in self._intermediate_constant_words:
            return [POS.NOUN]
        pos = self._get_pos(word)
        if not_found_warning and len(pos) == 0:
            logger.warning('pos not found for word "%s"', word)
        return pos

    @abstractmethod
    def _get_pos(self, word: str) -> List[POS]:
        pass

    def get_forms(self, pos: POS) -> List[str]:
        if pos == POS.VERB:
            return [e.value for e in self.VerbForm]
        elif pos in [POS.ADJ, POS.ADJ_SAT]:
            return [e.value for e in self.AdjForm]
        elif pos == POS.NOUN:
            return [e.value for e in self.NounForm]
        else:
            raise NotImplementedError()

    def change_word_form(self,
                         word: str,
                         pos: POS,
                         form: str,
                         force=False) -> List[str]:
        # This guard should not be the role of this function, as users may want to force some POS
        # if pos not in self.get_pos(word):
        #     raise ValueError(f'The worf {word} do not have pos={pos.value}')

        if pos == POS.VERB:
            return self._change_verb_form(word, self.VerbForm(form), force=force)
        elif pos in [POS.ADJ, POS.ADJ_SAT]:
            return self._change_adj_form(word, self.AdjForm(form), force=force)
        elif pos == POS.NOUN:
            return self._change_noun_form(word, self.NounForm(form), force=force)
        elif pos == POS.PRESENT_PARTICLE:
            return self._change_present_particle_form(word, self.PresentForm(form), force=force)
        elif pos == POS.PAST_PARTICLE:
            return self._change_past_particle_form(word, self.PastForm(form), force=force)
        else:
            raise Exception()

    @abstractmethod
    def _change_verb_form(self, verb: str, form: Enum, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_adj_form(self, adj: str, form: Enum, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_present_particle_form(self, adj: str, form: Enum, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_past_particle_form(self, adj: str, form: Enum, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_noun_form(self, noun: str, form: Enum, force=False) -> List[str]:
        pass

    @lru_cache(1000000)
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
