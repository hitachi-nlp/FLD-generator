from typing import Optional, Iterable, List, Union, Dict
from enum import Enum, EnumMeta
from string import ascii_uppercase
from abc import ABC, abstractmethod
from itertools import chain
from functools import lru_cache
import logging
from ordered_set import OrderedSet
from pydantic import BaseModel

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
    can_be_predicate_noun = 'can_be_predicate_noun'


class UserWord(BaseModel):
    lemma: str
    pos: POS

    # Note that "None" means "should behave as default"
    can_be_transitive_verb: Optional[bool] = None
    can_be_intransitive_verb: Optional[bool] = None

    can_be_event_noun: Optional[bool] = None
    can_be_entity_noun: Optional[bool] = None
    can_be_predicate_noun: Optional[bool] = None


class WordBank(ABC):

    # implemente in the sub classes
    VerbForm: EnumMeta
    AdjForm: EnumMeta
    PresentForm: EnumMeta
    PastForm: EnumMeta
    NounForm: EnumMeta
    # INTERMEDIATE_CONSTANT_PREFIXES: List[str]

    def __init__(self,
                 extra_vocab: Optional[List[UserWord]] = None,
                 intermediate_constant_prefix: Optional[str] = None):
        # to be used by translator, we make extra_vocab as public variable.
        # but it is not good a practice that the translator depends on the UserWord, which is the details of word bank.
        self.extra_vocab = extra_vocab
        self._extra_vocab_dict: Dict[str, UserWord] = (
            {word.lemma: word for word in extra_vocab} if extra_vocab is not None\
            else {}
        )

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
        if intermediate_constant_prefix is not None:
            self._intermediate_constant_words = OrderedSet([
                f'{intermediate_constant_prefix}{interm_constant}'
                for interm_constant in self._intermediate_constant_words
            ])

    def get_words(self, slice_='all') -> Iterable[str]:
        # enumerate base form of words
        if slice_ == 'all':
            yield from chain(self.get_intermediate_constant_words(), self._get_all_lemmas(), self._extra_vocab_dict)
        elif slice_ == 'extra':
            if len(self._extra_vocab_dict) == 0:
                logger.warning('extra_vocab is None. Will return empty list')
            yield from self._extra_vocab_dict or ()
        elif slice_ == 'extra_or_default':
            if len(self._extra_vocab_dict) > 0:
                yield from self._extra_vocab_dict
            else:
                yield from chain(self.get_intermediate_constant_words(), self._get_all_lemmas())
        else:
            raise ValueError(f'Unknown slice_={slice_}')

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

        def has_attr(name: str) -> bool:
            if word in self._extra_vocab_dict\
                    and getattr(self._extra_vocab_dict[word], name) is not None:  # not None means specified by user
                return getattr(self._extra_vocab_dict[word], name)
            else:
                return getattr(self, f'_{name}')(word)

        if POS.VERB in self.get_pos(word):
            if has_attr('can_be_intransitive_verb'):
                attrs.append(ATTR.can_be_intransitive_verb)
        if POS.VERB in self.get_pos(word):
            if has_attr('can_be_transitive_verb'):
                attrs.append(ATTR.can_be_transitive_verb)
        if POS.NOUN in self.get_pos(word):
            if has_attr('can_be_event_noun'):
                attrs.append(ATTR.can_be_event_noun)
        if POS.NOUN in self.get_pos(word):
            if has_attr('can_be_entity_noun'):
                attrs.append(ATTR.can_be_entity_noun)
        if POS.NOUN in self.get_pos(word):
            if has_attr('can_be_predicate_noun'):
                attrs.append(ATTR.can_be_predicate_noun)

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
    def _can_be_predicate_noun(self, noun: str) -> bool:
        pass
