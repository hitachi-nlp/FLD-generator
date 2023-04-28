from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional, Iterable, Dict, List, Set, Tuple
import re
import logging
import nltk

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from FLD.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm
from FLD.utils import starts_with_vowel_sound

logger = logging.getLogger(__name__)


class WordNetWordBank(WordBank):

    language: str = '__THIS_IS_BASE_CLASS__'

    # nltk/corpus/reader/wordnet.py
    _pos_wb_to_wn = {
        POS.VERB: wn.VERB,     # verbs (all tenses and modes)
        POS.NOUN: wn.NOUN,     # nouns (common and proper)
        POS.ADJ: wn.ADJ,       # adjectives
        POS.ADJ_SAT: wn.ADJ_SAT,
        POS.ADV: wn.ADV,       # adverbs
    }

    @profile
    def __init__(self, vocab_restrictions: Optional[Dict[POS, Iterable[str]]] = None):
        self._pos_wn_to_wb = {val: key for key, val in self._pos_wb_to_wn.items()}

        self._cached_word_set: Set[str] = set()
        self._cached_word_to_wn_pos: Dict[str, List[str]] = defaultdict(list)

        if vocab_restrictions is not None:
            logger.info('use restrected vocabulary')
            self.vocab_restrictions = {pos: set(words) for pos, words in vocab_restrictions.items()}  # make sure the words are in set. list is too slow.
        else:
            self.vocab_restrictions = None

        logger.info('loading words from WordNet ...')
        for word, wn_pos in self._load_words_once():
            if vocab_restrictions is not None:
                wb_POS = self._pos_wn_to_wb.get(wn_pos, None)
                if wb_POS in self.vocab_restrictions and word not in self.vocab_restrictions[wb_POS]:
                    continue
            self._cached_word_set.add(word)
            self._cached_word_to_wn_pos[word].append(wn_pos)
        logger.info('loading words from WordNet done!')

        self._cached_event_noun_synsets = None
        self._cached_entity_noun_synsets = None

    def _load_words_once(self) -> Iterable[Tuple[str, str]]:
        # done_lemmas = set()
        for syn in wn.all_synsets(lang=self.language):
            lemma = self._get_lemma(syn)
            if lemma is None:
                continue
            lemma_str = lemma.name()
            yield lemma_str, syn.pos()

    def get_words(self) -> Iterable[str]:
        yield from sorted(self._cached_word_set)

    def get_pos(self, word: str) -> List[POS]:
        word = self.get_lemma(word)
        wb_POSs = {
            (self._pos_wn_to_wb[syn.pos()] if syn.pos() in self._pos_wn_to_wb else POS.UNK)
            for syn in self._get_synsets(word)
        }
        if self.vocab_restrictions is not None:
            wb_POSs = {
                wb_POS for wb_POS in wb_POSs
                if wb_POS not in self.vocab_restrictions or word in self.vocab_restrictions[wb_POS]
            }
        
        return list(wb_POSs)

    @abstractmethod
    def get_lemma(self, word: str) -> str:
        pass

    @abstractmethod
    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> Optional[str]:
        pass

    @abstractmethod
    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> Optional[str]:
        pass

    @abstractmethod
    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> Optional[str]:
        pass

    def _can_be_intransitive_verb(self, verb: str) -> bool:
        return any((self._can_be_intransitive_verb_synset(syn)
                    for syn in self._get_synsets(verb)))

    def _can_be_transitive_verb(self, verb: str) -> bool:
        return any((self._can_be_transitive_verb_synset(syn)
                    for syn in self._get_synsets(verb)))

    def _get_lemma(self, syn: Synset) -> Optional[Lemma]:
        # syn.lemmas returns lemmas of synsets.
        # We will return the first (~ best match) lemma
        for lemma in syn.lemmas(lang=self.language):
            if lemma.name().find('_') < 0:  # exclude words like "drawing_card"
                return lemma
        return None

    @abstractmethod
    def _can_be_transitive_verb_synset(self, syn: Synset) -> bool:
        pass

    @abstractmethod
    def _can_be_intransitive_verb_synset(self, syn: Synset) -> bool:
        pass

    def _can_be_event_noun(self, noun: str) -> bool:
        """ Decide whether a noun can represent a event.

        # We implement this function based on reference 1 and 2.
        # We listed all the possible eventive root and then, filtered out the inappropriate ones as follows.

        > root_synset_names = [
        >     'event',
        >     'act',
        >     'phenomenon',
        >     'state',
        > ]
        > for root_synset_name in root_synset_name:
        >     for root_synset in wn.synsets(root_synset_name, pos=wn.NOUN):
        >         print(root_synset, root_synset.definition())

        Synset('event.n.01') something that happens at a given place and time
        Synset('event.n.02') a special set of circumstances
        Synset('event.n.03') a phenomenon located at a single point in space-time; the fundamental observational entity in relativity theory
        Synset('consequence.n.01') a phenomenon that follows and is caused by some previous phenomenon

        Synset('act.n.01') a legal document codifying the result of deliberations of a committee or society or legislative body
        Synset('act.n.02') something that people do or cause to happen
        Synset('act.n.03') a subdivision of a play or opera or ballet
        Synset('act.n.04') a short theatrical performance that is part of a longer program
        Synset('act.n.05') a manifestation of insincerity

        Synset('phenomenon.n.01') any state or process known through the senses rather than by intuition or reasoning
        Synset('phenomenon.n.02') a remarkable development

        Synset('state.n.01') the territory occupied by one of the constituent administrative districts of a nation
        Synset('state.n.02') the way something is with respect to its main attributes
        Synset('state.n.03') the group of people comprising the government of a sovereign state
        Synset('state.n.04') a politically organized body of people under a single government
        Synset('state_of_matter.n.01') (chemistry) the three traditional states of matter are solids (fixed shape and volume) and liquids (fixed volume and shaped by the container) and gases (filling the container)
        Synset('state.n.06') a state of depression or agitation
        Synset('country.n.02') the territory occupied by a nation
        Synset('department_of_state.n.01') the federal department in the United States that sets and maintains foreign policies


        References:
        1. [nlp - How to extract words based on wordnet event synset? - Stack Overflow](https://stackoverflow.com/questions/44856220/how-to-extract-words-based-on-wordnet-event-synset)
        2. [The first two levels of the WordNet 1.5 ontology of noun meanings](http://www.phmartin.info/CGKAT/ontologies/coWordNet.html)
        """

        root_synset_names = [
            'event.n.01',
            'event.n.02',
            'event.n.03',
            'consequence.n.01',

            'act.n.02',

            'phenomenon.n.01',

            # 'state.n.02',   # exclude this since precision is not that high
        ]

        if self._cached_event_noun_synsets is None:
            logger.info('loading event nouns ...')
            self._cached_event_noun_synsets = set()
            for root_synset_name in root_synset_names:
                root_synset = self._get_synset(root_synset_name)
                self._cached_event_noun_synsets = self._cached_event_noun_synsets.union(
                    self._get_descendant_synsets(root_synset))
            logger.info('loading event nouns done!')

        return any((syn in self._cached_event_noun_synsets
                    for syn in self._get_synsets(noun)))

    def _can_be_entity_noun(self, noun: str) -> bool:
        root_synset_names = [
            # 'entity.n.01',  # too general, e.g., it includes "then", which is a time.
            'physical_entity.n.01',
        ]

        if self._cached_entity_noun_synsets is None:
            logger.info('loading entity nouns once ...')
            self._cached_entity_noun_synsets = set()
            for root_synset_name in root_synset_names:
                root_synset = self._get_synset(root_synset_name)
                self._cached_entity_noun_synsets = self._cached_entity_noun_synsets.union(
                    self._get_descendant_synsets(root_synset))
            logger.info('loading entity nouns once ... done!')

        return any((syn in self._cached_entity_noun_synsets
                    for syn in self._get_synsets(noun)))

    def _get_ancestor_synsets(self, syn: Synset) -> Set[Synset]:
        ancestors = set()
        for hypernym in syn.hypernyms():
            if hypernym in ancestors:
                continue
            ancestors.add(hypernym)
            for ancestor in self._get_ancestor_synsets(hypernym):
                if ancestor not in ancestors:
                    ancestors.add(ancestor)
        return ancestors

    def _get_descendant_synsets(self, syn: Synset) -> Set[Synset]:
        descendants = set()
        for hyponym in syn.hyponyms():
            if hyponym in descendants:
                continue
            descendants.add(hyponym)
            for descendant in self._get_descendant_synsets(hyponym):
                if descendant not in descendants:
                    descendants.add(descendant)
        return descendants

    def get_synonyms(self, word: str) -> List[str]:
        synonyms = []
        for syn in self._get_synsets(word):
            lemma = self._get_lemma(syn)
            if lemma is None:
                continue

            if "_" not in lemma.name() and "-" not in lemma.name():
                if lemma.name() not in synonyms:
                    synonyms.append(lemma.name())
        return synonyms

    def get_antonyms(self, word: str) -> List[str]:
        antonyms = []
        for syn in self._get_synsets(word):
            lemma = self._get_lemma(syn)
            if lemma is None:
                continue

            for antonym in lemma.antonyms():
                if antonym.name() not in antonyms:
                    antonyms.append(antonym.name())
        return antonyms

    @abstractmethod
    def get_negnyms(self, word) -> List[str]:
        pass

    def _get_synsets(self, word: str) -> Iterable[Synset]:
        for wn_pos in self._cached_word_to_wn_pos[word]:
            for syn in wn.synsets(word, pos=wn_pos, lang=self.language):
                yield syn

    def _get_synset(self, word: str) -> Synset:
        return wn.synset(word)
