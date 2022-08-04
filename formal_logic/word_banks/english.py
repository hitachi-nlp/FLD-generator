from typing import Optional, Iterable
import re

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from pyinflect import getAllInflections, getInflection
from .base import WordBank


class EnglishWordBank(WordBank):

    VERB = 'VERB'
    NOUN = 'NOUN'
    ADJ = 'ADJ'
    _POS_WB_TO_WN = {
        'VERB': wn.VERB,
        'NOUN': wn.NOUN,
        'ADJ': wn.ADJ,
    }

    def get_words(self, pos: Optional[str] = None) -> Iterable[str]:
        if pos not in self._POS_WB_TO_WN:
            raise ValueError()

        done_lemmas = set()
        wn_pos = self._POS_WB_TO_WN[pos]
        for s in self._get_sensets_by_pos(wn_pos=wn_pos):
            for lemma in self._get_standard_lemmas(s):
                lemma_str = lemma.name()
                if lemma_str in done_lemmas:
                    continue

                yield lemma_str
                done_lemmas.add(lemma_str)
                break

    def change_verb_form(self, verb: str, form: str) -> Optional[str]:
        # see https://github.com/bjascob/pyInflect for available forms
        results = getInflection(verb, tag=form)
        return results[0] if results is not None else None

    def can_be_intransitive_verb(self, verb: str) -> bool:
        return any([self._can_be_transitive_verb_synset(s)
                    for s in self._get_synsets_by_word(verb)])

    def _get_synsets_by_word(self, word: str) -> Iterable[Synset]:
        return wn.synsets(word)

    def _get_sensets_by_pos(self, wn_pos: Optional[str] = None) -> Iterable[Synset]:
        yield from wn.all_synsets(wn_pos)

    def _get_standard_lemmas(self, s: Synset) -> Iterable[Lemma]:
        # exclude words like "drawing_card"
        for lemma in s.lemmas():
            if lemma.name().find('_') < 0:
                yield lemma

    def _can_be_transitive_verb_synset(self, s: Synset) -> bool:
        if s.pos() != wn.VERB:
            return False

        # Transitive verb if the verb details is like "Someone eat something"
        if any([re.match('.*Some.*some.*', verb_info) is None
                for lemma in self._get_standard_lemmas(s)
                for verb_info in lemma.frame_strings()]):
            return True

        return False
