from abc import ABC
from collections import defaultdict
from typing import Optional, Iterable, Dict, List, Set, Tuple
import logging

from nltk.corpus.reader.wordnet import Synset, Lemma
from FLD_generator.word_banks.base import POS

from .wordnet import WN_POS, SynsetOp, LemmaOp

logger = logging.getLogger(__name__)

# nltk/corpus/reader/wordnet.py
_POS_WB_TO_WN = {
    POS.VERB    : WN_POS.VERB,
    POS.NOUN    : WN_POS.NOUN,
    POS.ADJ     : WN_POS.ADJ,
    POS.ADJ_SAT : WN_POS.ADJ_SAT,
    POS.ADV     : WN_POS.ADV,
}

_POS_WN_TO_WB = {val: key
                 for key, val in _POS_WB_TO_WN.items()}



class WordUtil:

    def __init__(self,
                 language: str,
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 vocab: Optional[Dict[POS, Set[str]]] = None):
        if language == 'jpn':
            logger.warning('Wordnet operations such as getting synonyms/antonyms may not produce good results for language=%s, due to not-yet-refined logic', language)

        self._language = language
        self._syn_op = SynsetOp()
        self._lemma_op = LemmaOp()

        if transitive_verbs is not None:
            self._transitive_verbs = set(verb.lower() for verb in transitive_verbs)
        else:
            self._transitive_verbs = None

        if intransitive_verbs is not None:
            self._intransitive_verbs = set(verb.lower() for verb in intransitive_verbs)
        else:
            self._intransitive_verbs = None

        if vocab is not None:
            logger.info('use restrected vocabulary')
            # make sure the words are in set. list is too slow.
            self._vocab = {_POS_WB_TO_WN[pos]: set(words)
                                        for pos, words in vocab.items()}
            self._is_user_vocab = True
        else:
            self._vocab = None
            self._is_user_vocab = False

        self._word_set: Set[str] = set()
        self._word_to_wn_pos: Dict[str, List[WN_POS]] = defaultdict(list)

        if self._vocab is not None:
            logger.info('loading words from specified vocab ...')
            for pos, words in self._vocab.items():
                for word in words:
                    self._word_set.add(word)
                    self._word_to_wn_pos[word].append(pos)
            logger.info('loading words from specified vocab done!')
        else:
            logger.info('loading words from WordNet ...')
            for word, wn_pos in self._load_all_lemmas_from_wn():
                if vocab is not None:
                    if wn_pos in self._vocab\
                            and word not in self._vocab[wn_pos]:
                        continue
                self._word_set.add(word)
                self._word_to_wn_pos[word].append(wn_pos)
            logger.info('loading words from WordNet done!')

    def _load_all_lemmas_from_wn(self) -> Iterable[Tuple[str, WN_POS]]:
        logger.info('loading lemmas...')
        done_lemmas: Set[Lemma] = set([])
        for syn in self._syn_op.all():
            lemmas = self._lemmas_from_syn(syn)
            if len(lemmas) == 0:
                continue

            # the first (might be the best) match lemma
            # lemma_str = lemmas[0].name()
            # yield lemma_str, syn.pos()

            for lemma in lemmas:
                if lemma in done_lemmas:
                    continue
                done_lemmas.add(lemma)
                lemma_str = lemma.name()
                for _syn in self._syn_op.from_word(lemma_str, word_lang=self._language):
                    yield lemma_str, _syn.pos()

    def get_lemma(self, word: str,
                  # False as default as lemmatization failure always occurs for noun but it is not a problem
                  warn_lemmatize_failure=False) -> str:
        # To avoid circular import
        from .japanese.parser import get_lemma as get_lemma_jpn
        from .english.parser import get_lemma as get_lemma_eng

        if self._language == 'eng':
            # Why not use wordnet?
            # -> maybe, we wanted to ensure that the lemmatization always succeeds
            lemma = get_lemma_eng(word)
            if lemma is not None:
                return lemma
            else:
                if warn_lemmatize_failure:
                    logger.warning('failed to lemmatize word: %s', word)
                return word

        elif self._language == 'jpn':
            return get_lemma_jpn(word)

        else:
            raise NotImplementedError()

    def get_synonym_lemmas(self, word: str) -> List[str]:
        lemmas: List[str] = []
        for syn in self._syns_from_word(word):
            _lemmas = self._lemmas_from_syn(syn)
            if len(_lemmas) > 0:
                # use the first (might be the best) match lemma
                lemmas.append(_lemmas[0].name())
        return lemmas

    def get_all_lemmas(self) -> Set[str]:
        return self._word_set

    def get_pos(self, word: str) -> List[POS]:
        if self._is_user_vocab:
            # for the user specified vocab, we stick to the used specified POS
            if word in self._word_to_wn_pos:
                wn_poss = self._word_to_wn_pos[word]
            elif self.get_lemma(word) in self._word_to_wn_pos:
                wn_poss = self._word_to_wn_pos[self.get_lemma(word)]
            else:
                raise ValueError()
        else:
            word = self.get_lemma(word)
            # HONOKA: I forget why we trace the synonyms here...
            wn_poss = [WN_POS(syn.pos()) for syn in self._syns_from_word(word)]
        return list(set(_POS_WN_TO_WB[wn_pos] for wn_pos in wn_poss))

    def can_be_intransitive_verb(self, verb: str) -> bool:
        if self._intransitive_verbs is None:
            raise ValueError('Please specify intransitive verb list')
        return any(lemma.lower() in self._intransitive_verbs
                   for lemma in self.get_synonym_lemmas(verb))

    def can_be_transitive_verb(self, verb: str) -> bool:
        if self.can_be_intransitive_verb is None:
            raise ValueError('Please specify intransitive verb list')
        return any(lemma.lower() in self._transitive_verbs
                   for lemma in self.get_synonym_lemmas(verb))

    def can_be_event_noun(self, noun: str) -> bool:
        return any((self._syn_op.is_event(syn)
                    for syn in self._syns_from_word(noun)))

    def can_be_entity_noun(self, noun: str) -> bool:
        return any((self._syn_op.is_entity(syn)
                    for syn in self._syns_from_word(noun)))

    def get_synonyms(self, word: str) -> List[str]:
        return list({
            lemma.name()
            for lemma in self._lemmas_from_word(word)
        })

    def get_antonyms(self, word: str) -> List[str]:
        return list({
            antonym.name()
            for lemma in self._lemmas_from_word(word)
            for antonym in self._lemma_op.antonyms(lemma)
        })

    def _syns_from_word(self, word: str) -> List[Synset]:
        syns: List[Synset] = []
        for wn_pos in self._word_to_wn_pos[word]:
            for syn in self._syn_op.from_word(word,
                                              pos=wn_pos,
                                              word_lang=self._language):
                syns.append(syn)
        return syns

    def _lemmas_from_word(self, word: str) -> List[Lemma]:
        lemmas: List[Lemma] = []
        for syn in self._syns_from_word(word):
            for lemma in self._lemmas_from_syn(syn):
                if lemma not in lemmas:
                    lemmas.append(lemma)
        return lemmas

    def _lemmas_from_syn(self, syn: Synset) -> List[Lemma]:
        return self._lemma_op.from_syn(syn, lemma_lang=self._language)
