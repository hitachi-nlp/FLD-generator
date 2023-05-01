from typing import Optional, Iterable, List
import re
import logging

from FLD.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm
from nltk.corpus.reader.wordnet import Synset, Lemma
from .base import WordNetWordBank

logger = logging.getLogger(__name__)


class JapaneseWordBank(WordNetWordBank):

    language = 'jpn'

    @property
    def _unconditioned_constant_words(self) -> List[str]:
        raise NotImplementedError()

    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        raise NotImplementedError()

    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        raise NotImplementedError()

    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        raise NotImplementedError()

    def _can_be_transitive_verb_synset(self, syn: Synset) -> bool:
        raise NotImplementedError()

    def _can_be_intransitive_verb_synset(self, syn: Synset) -> bool:
        raise NotImplementedError()

    def get_negnyms(self, word) -> List[str]:
        raise NotImplementedError()
