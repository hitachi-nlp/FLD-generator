from typing import Optional, Iterable, Dict, List
import re
import logging
from itertools import chain

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from pyinflect import getInflection
from .base import WordBank, POS, VerbForm, AdjForm

logger = logging.getLogger(__name__)


class EnglishWordBank(WordBank):

    _POS_WB_TO_WN = {
        POS.VERB: wn.VERB,
        POS.NOUN: wn.NOUN,
        POS.ADJ: wn.ADJ,
    }

    def __init__(self):
        logger.info('loading words ...')
        self._cached_word_list = {
            pos: list(self._get_words_wo_cache(pos))
            for pos in chain(POS, [None])
        }
        self._cached_word_sets = {
            pos: set(pos_list)
            for pos, pos_list in self._cached_word_list.items()
        }
        logger.info('loading words done!')

    def get_words(self, pos: Optional[POS] = None) -> Iterable[str]:
        yield from self._cached_word_list[pos]

    def get_pos(self, word: str) -> List[POS]:
        posses = []
        for pos in POS:
            if word in self._cached_word_sets[pos]:
                posses.append(pos)
        return posses

    def get_synonyms(self, word: str) -> List[str]:
        synonyms = []
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                if "_" not in lemma.name() and "-" not in lemma.name():
                    if lemma.name() not in synonyms:
                        synonyms.append(lemma.name())
        return synonyms

    def get_antonyms(self, word: str) -> List[str]:
        antonyms = []
        for syn in wn.synsets(word):
            for lemma in syn.lemmas():
                if lemma.antonyms():
                    for antonym in lemma.antonyms():
                        if antonym.name() not in antonyms:
                            antonyms.append(antonym.name())
        return antonyms

    def _get_words_wo_cache(self, pos: Optional[POS] = None) -> Iterable[str]:
        done_lemmas = set()
        wn_pos = self._POS_WB_TO_WN[pos] if pos is not None else None
        for s in self._get_sensets_by_pos(wn_pos=wn_pos):
            for lemma in self._get_standard_lemmas(s):
                lemma_str = lemma.name()
                if lemma_str in done_lemmas:
                    continue

                yield lemma_str
                done_lemmas.add(lemma_str)
                break

    def _change_verb_form(self, verb: str, form: VerbForm, force=True) -> Optional[str]:
        # see https://github.com/bjascob/pyInflect for available forms
        results = getInflection(verb, tag=form)
        if results is None:
            if force:
                if form == VerbForm.VB:
                    # watch
                    inflated_verb = verb
                elif form == VerbForm.VBG:
                    # [現在分詞](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo82.htm)
                    if re.match('.*[^aeiou]e$', verb):
                        # date -> dating
                        inflated_verb = verb[:-1] + 'ing'
                    elif re.match('.*[^aeiou][aeiou][^aeiou]$', verb):
                        # sit -> sitting
                        inflated_verb = verb + verb[-1] + 'ing'
                    else:
                        inflated_verb = verb + 'ing'
                elif form == VerbForm.VBZ:
                    # [３単現及び名詞の複数形の -s, -es](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo52.htm)
                    if re.match('.*(s|sh|ch|x|o)$', verb):
                        # wash -> washes
                        inflated_verb = verb + 'es'
                    elif re.match(r'.*[^aeiou]y$', verb):
                        # study -> studies
                        inflated_verb = verb[:-1] + 'ies'
                    else:
                        inflated_verb = verb + 's'
                else:
                    raise NotImplementedError()
                # logger.info('Will force changing verb form to %s by hand-made rules as: "%s" -> "%s"',
                #             form,
                #             verb,
                #             inflated_verb)
                return inflated_verb
            else:
                return None
        else:
            return results[0]

    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        if form == AdjForm.NORMAL:
            return adj
        elif form == AdjForm.NESS:
            if adj.endswith('y'):
                # peaky -> peakiness
                return adj[:-1] + 'iness'
            else:
                return adj + 'ness'
        else:
            raise ValueError(f'Unknown form {form}')

    def _can_be_intransitive_verb(self, verb: str) -> bool:
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
