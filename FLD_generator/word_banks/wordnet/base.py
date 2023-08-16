from abc import abstractmethod
from collections import defaultdict
from typing import Optional, Iterable, Dict, List, Set, Tuple
import logging
import nltk

from nltk.corpus.reader.wordnet import Synset
from .wordnet_utils import WordNetUtil
from FLD_generator.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm

logger = logging.getLogger(__name__)


class WordNetWordBank(WordBank):

    language: str = '__THIS_IS_BASE_CLASS__'

    # nltk/corpus/reader/wordnet.py
    _pos_wb_to_wn = {
        POS.VERB    : WordNetUtil.VERB,
        POS.NOUN    : WordNetUtil.NOUN,
        POS.ADJ     : WordNetUtil.ADJ,
        POS.ADJ_SAT : WordNetUtil.ADJ_SAT,
        POS.ADV     : WordNetUtil.ADV,
    }

    def __init__(self,
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 vocab_restrictions: Optional[Dict[POS, Iterable[str]]] = None):
        self._transitive_verbs = set(verb.lower() for verb in transitive_verbs) if transitive_verbs is not None else None
        self._intransitive_verbs = set(verb.lower() for verb in intransitive_verbs) if intransitive_verbs is not None else None
        self._wn_util: WordNetUtil = WordNetUtil(self.language)

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

    def _load_words_once(self) -> Iterable[Tuple[str, str]]:
        for syn in self._wn_util.get_all_synsets():
            lemma = self._wn_util.get_lemma(syn)
            if lemma is None:
                continue
            lemma_str = lemma.name()
            yield lemma_str, syn.pos()

    def _get_real_words(self) -> Iterable[str]:
        yield from sorted(self._cached_word_set)

    @profile
    def _get_pos(self, word: str) -> List[POS]:
        word = self.get_lemma(word)
        wb_POSs = {
            (self._pos_wn_to_wb[syn.pos()] if syn.pos() in self._pos_wn_to_wb else POS.OTHERS)
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
    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> List[str]:
        pass

    @abstractmethod
    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> List[str]:
        pass

    def _can_be_intransitive_verb(self, verb: str) -> bool:
        for syn in self._get_synsets(verb):
            if self._intransitive_verbs is None:
                raise ValueError('Please specify intransitive verb list')

            lemma = self._wn_util.get_lemma(syn)
            if lemma is not None and lemma.name().lower() in self._intransitive_verbs:
                return True
        return False

    def _can_be_transitive_verb(self, verb: str) -> bool:
        for syn in self._get_synsets(verb):

            if self._can_be_intransitive_verb is None:
                raise ValueError('Please specify intransitive verb list')
            lemma = self._wn_util.get_lemma(syn)
            if lemma is not None and lemma.name().lower() in self._transitive_verbs:
                return True
        return False

    def _can_be_event_noun(self, noun: str) -> bool:
        event_noun_synsets = self._wn_util.get_event_noun_synsets()
        return any((syn in event_noun_synsets
                    for syn in self._get_synsets(noun)))

    def _can_be_entity_noun(self, noun: str) -> bool:
        entity_noun_synsets = self._wn_util.get_entity_noun_synsets()
        return any((syn in entity_noun_synsets
                    for syn in self._get_synsets(noun)))

    def get_synonyms(self, word: str) -> List[str]:
        synonyms = []
        for syn in self._get_synsets(word):
            lemma = self._wn_util.get_lemma(syn)
            if lemma is None:
                continue
            if lemma.name() not in synonyms:
                synonyms.append(lemma.name())
        return synonyms

    def get_antonyms(self, word: str) -> List[str]:
        antonyms = []
        for syn in self._get_synsets(word):
            lemma = self._wn_util.get_lemma(syn)
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
            for syn in self._wn_util.get_synsets(word, pos=wn_pos):
                yield syn
