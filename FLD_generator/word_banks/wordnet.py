from typing import Optional, Iterable, List, Set
import logging
from enum import Enum

from lemminflect import getInflection, getLemma
from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import WordNetCorpusReader, wordnet as _WN

logger = logging.getLogger(__name__)

# this load languages other than English
_WN.synsets('brabra', lang='jpn')


class WN_POS(Enum):
    VERB = WordNetCorpusReader.VERB     # verbs (all tenses and modes)
    NOUN = WordNetCorpusReader.NOUN     # nouns (common and proper)
    ADJ = WordNetCorpusReader.ADJ       # adjectives
    ADJ_SAT = WordNetCorpusReader.ADJ_SAT
    ADV = WordNetCorpusReader.ADV       # adverbs


_ENTITY_SYNSETS_CACHE: Optional[Set[Synset]] = None
_EVENT_SYNSETS_CACHE: Optional[Set[Synset]] = None


class SynsetOp:
    """Operation on Synse

    Note that most of the operations on Synsets do not depend on language.
    """

    def all(self) -> Iterable[Synset]:
        """ get all synsets.

        If "subset_lang" is specified, the subset of all the synsets that is used by the language is returned.
        """
        return _WN.all_synsets()

    def from_word(self,
                  word: str,
                  word_lang='eng',
                  exact=False,
                  pos: Optional[WN_POS] = None) -> List[Synset]:
        if exact:
            return [_WN.synset(word)]
        else:
            return _WN.synsets(word, pos=pos, lang=word_lang)

    def is_event(self, syn: Synset) -> bool:
        return syn in self._get_event_nouns()

    def _get_event_nouns(self) -> Set[Synset]:
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

        global _EVENT_SYNSETS_CACHE
        if _EVENT_SYNSETS_CACHE is None:
            logger.info('loading event nouns ...')
            _EVENT_SYNSETS_CACHE = set()
            for root_synset_name in root_synset_names:
                root_synset = self.from_word(root_synset_name, exact=True)[0]
                _EVENT_SYNSETS_CACHE = _EVENT_SYNSETS_CACHE.union(
                    self._descendants(root_synset))
            logger.info('loading event nouns done!')
        return _EVENT_SYNSETS_CACHE

    def is_entity(self, syn: Synset) -> bool:
        return syn in self._get_entities()

    def _get_entities(self) -> Set[Synset]:
        root_synset_names = [
            # 'entity.n.01',  # too general, e.g., it includes "then", which is a time.
            'physical_entity.n.01',
        ]

        global _ENTITY_SYNSETS_CACHE
        if _ENTITY_SYNSETS_CACHE is None:
            logger.info('loading entity nouns once ...')
            _ENTITY_SYNSETS_CACHE = set()
            for root_synset_name in root_synset_names:
                root_synset = self.from_word(root_synset_name, exact=True)[0]
                _ENTITY_SYNSETS_CACHE = _ENTITY_SYNSETS_CACHE.union(
                    self._descendants(root_synset))
            logger.info('loading entity nouns once ... done!')
        return _ENTITY_SYNSETS_CACHE

    def _ancestors(self, syn: Synset) -> Set[Synset]:
        ancestors = set()
        for hypernym in syn.hypernyms():
            if hypernym in ancestors:
                continue
            ancestors.add(hypernym)
            for ancestor in self._ancestors(hypernym):
                if ancestor not in ancestors:
                    ancestors.add(ancestor)
        return ancestors

    def _descendants(self, syn: Synset) -> Set[Synset]:
        descendants = set()
        for hyponym in syn.hyponyms():
            if hyponym in descendants:
                continue
            descendants.add(hyponym)
            for descendant in self._descendants(hyponym):
                if descendant not in descendants:
                    descendants.add(descendant)
        return descendants


class LemmaOp:

    def __init__(self):
        self._sn_op = SynsetOp()

    def from_syn(self, syn: Synset, lemma_lang='eng') -> List[Lemma]:
        lemmas: List[Lemma] = []
        for lemma in syn.lemmas(lang=lemma_lang):
            if self._is_ok_lemma(lemma):
                lemmas.append(lemma)
        return lemmas

    def from_word(self,
                  word: str,
                  word_lang: str,
                  lemma_lang='eng') -> List[Lemma]:
        lemmas: List[Lemma] = []
        for syn in self._sn_op.from_word(word,
                                         word_lang=word_lang):
            for lemma in self.from_syn(syn, lemma_lang=lemma_lang):
                if lemma not in lemmas:
                    if self._is_ok_lemma(lemma):
                        lemmas.append(lemma)
        return lemmas

    def to_syns(self, lemma: Lemma) -> Optional[Synset]:
        return self._sn_op.from_word(lemma.name(),
                                     word_lang=lemma.lang())

    def other_lang(self, lemma: Lemma, lang: str) -> List[Lemma]:
        lemmas: List[Lemma] = []
        for syn in self.to_syns(lemma):
            for _lemma in syn.lemmas(lang=lang):
                if self._is_ok_lemma(_lemma) and _lemma not in lemmas:
                    lemmas.append(_lemma)
        return lemmas

    def synonyms(self, lemma: Lemma) -> List[Lemma]:
        synonyms: List[Lemma] = []
        for syn in self.to_syns(lemma):
            for synonym in self.from_syn(syn, lemma_lang=lemma.lan()):
                if self._is_ok_lemma(synonym) and synonym not in synonyms:
                    synonyms.append(synonym)
        return synonyms

    def antonyms(self, lemma: Lemma) -> List[Lemma]:
        antonyms = []
        # need to bypass english to get antonyms
        if lemma.lang() == 'eng':
            for antonym in lemma.antonyms():
                if self._is_ok_lemma(antonym) and antonym not in antonyms:
                    antonyms.append(antonym)
        else:
            for lemma_eng in self.other_lang(lemma, lang='eng'):
                for antonym_eng in lemma_eng.antonyms():
                    for antonym in self.other_lang(antonym_eng, lang=lemma.lang()):
                        if self._is_ok_lemma(antonym) and antonym not in antonyms:
                            antonyms.append(antonym)
        return antonyms

    def _is_ok_lemma(self, lemma: Lemma) -> bool:
        # exclude words like "drawing_card"
        return '_' not in lemma.name() and '-' not in lemma.name()
