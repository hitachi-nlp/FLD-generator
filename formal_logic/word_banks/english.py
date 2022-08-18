from typing import Optional, Iterable, Dict, List
import re
import logging
from itertools import chain
from collections import defaultdict

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from pyinflect import getInflection
from .base import WordBank, POS, VerbForm, AdjForm, NounForm

logger = logging.getLogger(__name__)


class EnglishWordBank(WordBank):

    _pos_wb_to_wn = {
        POS.VERB: wn.VERB,
        POS.NOUN: wn.NOUN,
        POS.ADJ: wn.ADJ,
    }

    _verb_inflation_mapping = {
        VerbForm.NORMAL: 'VB',
        VerbForm.ING: 'VBG',
        VerbForm.S: 'VBZ',
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
                for antonym in lemma.antonyms():
                    if antonym.name() not in antonyms:
                        antonyms.append(antonym.name())
        return antonyms

    def get_negnyms(self, word) -> List[str]:
        # See [here](https://langsquare.exblog.jp/28548624/) for the following detection rules.
        negnyms = []
        negation_prefixes = ['in', 'im', 'il', 'ir', 'un', 'dis', 'non']
        negation_postfixes = ['less']

        for antonym in self.get_antonyms(word):
            if any([antonym == f'{prefix}{word}' for prefix in negation_prefixes])\
                    or any([antonym == f'{word}{postfix}' for postfix in negation_postfixes]):
                negnyms.append(antonym)

            if any([word.startswith(prefix) and word.lstrip(prefix) in self._cached_word_list[None]
                    for prefix in negation_prefixes])\
                or any([word.endswith(postfix) and word.rstrip(postfix) in self._cached_word_list[None]
                        for postfix in negation_postfixes]):
                negnyms.append(antonym)
        return negnyms

    def _get_words_wo_cache(self, pos: Optional[POS] = None) -> Iterable[str]:
        done_lemmas = set()
        wn_pos = self._pos_wb_to_wn[pos] if pos is not None else None
        for s in self._get_sensets_by_pos(wn_pos=wn_pos):
            for lemma in self._get_standard_lemmas(s):
                lemma_str = lemma.name()
                if lemma_str in done_lemmas:
                    continue

                yield lemma_str
                done_lemmas.add(lemma_str)
                break

    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        # see https://github.com/bjascob/pyInflect for available forms
        results = getInflection(verb,
                                tag=self._verb_inflation_mapping[form])
        if results is not None:
            return results[0]
        else:
            if force:
                if form == VerbForm.NORMAL:
                    # watch
                    inflated_verb = verb
                elif form == VerbForm.ING:
                    # [現在分詞](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo82.htm)
                    if re.match('.*[^aeiou]e$', verb):
                        # date -> dating
                        inflated_verb = verb[:-1] + 'ing'
                    elif re.match('.*[^aeiou][aeiou][^aeiou]$', verb):
                        # sit -> sitting
                        inflated_verb = verb + verb[-1] + 'ing'
                    else:
                        inflated_verb = verb + 'ing'
                elif form == VerbForm.S:
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
                return inflated_verb
            else:
                return None

    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        if form == AdjForm.NORMAL:
            return adj
        elif form == AdjForm.NESS:
            if adj.endswith('y'):
                # peaky -> peakiness
                ness_adj = adj[:-1] + 'iness'
            else:
                ness_adj = adj + 'ness'
            if force or ness_adj in self._cached_word_list[None]:
                return ness_adj
            else:
                return None
        elif form == AdjForm.NEG:
            negnyms = self.get_negnyms(adj)
            if len(negnyms) == 0:
                if force:
                    return f'non-{adj}'
                else:
                    return None
            else:
                return negnyms[0]
        else:
            raise ValueError(f'Unknown form {form}')

    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        if form == NounForm.NORMAL:
            return noun
        else:
            raise ValueError(f'Unknown form {form}')

    def _can_be_intransitive_verb(self, verb: str) -> bool:
        return any([self._can_be_transitive_verb_synset(s)
                    for s in self._get_synsets_by_word(verb)])

    def _get_synsets_by_word(self, word: str, pos: Optional[str] = None ) -> Iterable[Synset]:
        return wn.synsets(word, pos=pos)

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

    def _can_be_eventive_noun(self, noun: str) -> bool:
        """ Decide whether a noun can represent a event.

        References:
        1. [nlp - How to extract words based on wordnet event synset? - Stack Overflow](https://stackoverflow.com/questions/44856220/how-to-extract-words-based-on-wordnet-event-synset)
        2. [The first two levels of the WordNet 1.5 ontology of noun meanings](http://www.phmartin.info/CGKAT/ontologies/coWordNet.html)
        """

        # We chose the following root synsets based on reference 1 and 2.
        event_synset_root_names = [
            'event.n.01',
            'event.n.02',
            'event.n.03',
            'consequence.n.01',

            'act.n.02',

            'phenomenon.n.01',

            # 'state.n.02',   # exclude this since precision is not that high
        ]

        event_root_synsets = [wn.synset(name) for name in event_synset_root_names]

        return any((
            ancestor_syn in event_root_synsets
            for syn in self._get_synsets_by_word(noun)
            for ancestor_syn in self._get_ancestor_synsets(syn)
        ))

    def _get_ancestor_synsets(self, syn: Synset) -> List[Synset]:
        ancestors = []
        for hypernym in syn.hypernyms():
            if hypernym not in ancestors:
                ancestors.append(hypernym)
            for ancestor in self._get_ancestor_synsets(hypernym):
                if ancestor not in ancestors:
                    ancestors.append(ancestor)
        return ancestors

    def _get_descendant_synsets(self, syn: Synset) -> List[Synset]:
        descendants = []
        for hypernym in syn.hypernyms():
            if hypernym not in descendants:
                descendants.append(hypernym)
            for descendant in self._get_descendant_synsets(hypernym):
                if descendant not in descendants:
                    descendants.append(descendant)
        return descendants
