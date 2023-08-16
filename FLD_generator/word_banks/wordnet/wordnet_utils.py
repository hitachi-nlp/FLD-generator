from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional, Iterable, Dict, List, Set, Tuple
import re
import logging
import nltk

from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import WordNetCorpusReader, wordnet as wn_instance
from FLD_generator.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm
from FLD_generator.utils import starts_with_vowel_sound, make_pretty_msg

logger = logging.getLogger(__name__)


class WordNetUtil:

    VERB    = WordNetCorpusReader.VERB     # verbs (all tenses and modes)
    NOUN    = WordNetCorpusReader.NOUN     # nouns (common and proper)
    ADJ     = WordNetCorpusReader.ADJ       # adjectives
    ADJ_SAT = WordNetCorpusReader.ADJ_SAT
    ADV     = WordNetCorpusReader.ADV       # adverbs

    def __init__(self, language: str):
        self.wn = wn_instance
        self._language = language
        self._cached_entity_noun_synsets: Optional[Set[Synset]] = None
        self._cached_event_noun_synsets: Optional[Set[Synset]] = None

    def get_all_synsets(self) -> Iterable[Synset]:
        return self.wn.all_synsets(lang=self._language)

    def get_lemma(self, syn: Synset) -> Optional[Lemma]:
        # syn.lemmas returns lemmas of synsets.
        # We will return the first (~ best match) lemma
        for lemma in syn.lemmas(lang=self._language):
            if self.is_ok_lemma(lemma):
                return lemma
        return None

    def is_ok_lemma(self, lemma: Lemma) -> bool:
        # exclude words like "drawing_card"
        return '_' not in lemma.name() and '-' not in lemma.name()

    def get_event_noun_synsets(self) -> Set[Synset]:
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
                root_synset = self._get_synset_exact(root_synset_name)
                self._cached_event_noun_synsets = self._cached_event_noun_synsets.union(
                    self.get_descendant_synsets(root_synset))
            logger.info('loading event nouns done!')
        return self._cached_event_noun_synsets

    def get_entity_noun_synsets(self) -> Set[Synset]:
        root_synset_names = [
            # 'entity.n.01',  # too general, e.g., it includes "then", which is a time.
            'physical_entity.n.01',
        ]

        if self._cached_entity_noun_synsets is None:
            logger.info('loading entity nouns once ...')
            self._cached_entity_noun_synsets = set()
            for root_synset_name in root_synset_names:
                root_synset = self._get_synset_exact(root_synset_name)
                self._cached_entity_noun_synsets = self._cached_entity_noun_synsets.union(
                    self.get_descendant_synsets(root_synset))
            logger.info('loading entity nouns once ... done!')
        return self._cached_entity_noun_synsets

    def get_ancestor_synsets(self, syn: Synset) -> Set[Synset]:
        ancestors = set()
        for hypernym in syn.hypernyms():
            if hypernym in ancestors:
                continue
            ancestors.add(hypernym)
            for ancestor in self.get_ancestor_synsets(hypernym):
                if ancestor not in ancestors:
                    ancestors.add(ancestor)
        return ancestors

    def get_descendant_synsets(self, syn: Synset) -> Set[Synset]:
        descendants = set()
        for hyponym in syn.hyponyms():
            if hyponym in descendants:
                continue
            descendants.add(hyponym)
            for descendant in self.get_descendant_synsets(hyponym):
                if descendant not in descendants:
                    descendants.add(descendant)
        return descendants

    def get_synsets(self, word: str, pos: Optional[str] = None) -> List[Synset]:
        return self.wn.synsets(word, pos=pos)

    def _get_synset_exact(self, word: str) -> Synset:
        return self.wn.synset(word)
