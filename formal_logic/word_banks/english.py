from typing import Optional, Iterable
import re
import logging

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from pyinflect import getInflection
from .base import WordBank

logger = logging.getLogger(__name__)


class EnglishWordBank(WordBank):

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

    def change_verb_form(self, verb: str, form: str, force=True) -> Optional[str]:
        # see https://github.com/bjascob/pyInflect for available forms
        # and https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html for tag system.
        results = getInflection(verb, tag=form)
        if results is None:
            if force:
                if form == 'VB':
                    # watch
                    inflated_verb = verb
                elif form == 'VBG':
                    # [現在分詞](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo82.htm)
                    if re.match('.*[^aeiou]e$', verb):
                        # date -> dating
                        inflated_verb = verb[:-1] + 'ing'
                    elif re.match('.*[^aeiou][aeiou][^aeiou]$', verb):
                        # sit -> sitting
                        inflated_verb = verb + verb[-1] + 'ing'
                    else:
                        inflated_verb = verb + 'ing'
                elif form == 'VBZ':
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
                logger.info('Will force changing verb form to %s by hand-made rules as: "%s" -> "%s"',
                               form,
                               verb,
                               inflated_verb)
                return inflated_verb
            else:
                return None
        else:
            return results[0]

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
