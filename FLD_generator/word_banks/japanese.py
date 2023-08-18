from typing import Optional, Iterable, List, Dict
from string import ascii_uppercase
from collections import defaultdict

from FLD_generator.word_banks.base import (
    POS,
    VerbForm,
    AdjForm,
    NounForm,
)
from FLD_generator.word_banks.base import WordBank
import line_profiling

from .parsers.japanese import Morpheme
from .word_utils import WordUtil


class JapaneseWordBank(WordBank):

    __intermediate_constant_words  = [
        f'事物{alphabet}'
        for alphabet in ascii_uppercase
    ]

    _morphme_pos_to_POS = {
        '動詞': POS.VERB,
        '名詞': POS.NOUN,
        '形容詞': POS.ADJ,
        '副詞': POS.ADV,
    }

    def __init__(self,
                 morphemes: List[Morpheme],
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 vocab_restrictions: Optional[Dict[POS, Iterable[str]]] = None):
        self._morphemes = sorted(morphemes)

        self._surface2morpheme: Dict[str, List[Morpheme]] = defaultdict(list)
        # self._base_morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        self._base2katsuyous: Dict[str, List[Morpheme]] = defaultdict(list)
        for morpheme in morphemes:
            self._surface2morpheme[morpheme.surface].append(morpheme)
            if morpheme.katsuyou != '基本形':
                self._base2katsuyous[morpheme.base].append(morpheme)

        self._word_util = WordUtil(
            'jpn',
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            vocab_restrictions=vocab_restrictions,
        )

    def _get_all_lemmas(self) -> Iterable[str]:
        for morpheme in self._morphemes:
            if morpheme.katsuyou == '基本形':
                yield morpheme.surface

    @property
    def _intermediate_constant_words(self) -> List[str]:
        return self.__intermediate_constant_words

    def _get_pos(self, word: str) -> List[POS]:
        if word not in self._surface2morpheme:
            return []
        else:
            morphemes = self._surface2morpheme[word]
            return list({
                self._morphme_pos_to_POS.get(morpheme.pos, POS.OTHERS)
                for morpheme in morphemes
            })

    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> List[str]:
        if form == VerbForm.NORMAL:
            return [verb]

        elif form == VerbForm.ING:
            verbs: List[str] = []
            for morpheme in self._get_katsuyou_morphemes(verb, katsuyous=['連用タ接続']):
                if morpheme.surface[-1] == 'ん':
                    verbs.append(morpheme.surface + 'でいる')
                else:
                    verbs.append(morpheme.surface + 'ている')
            return verbs

        elif form == VerbForm.S:
            return [verb]

        elif form == VerbForm.ANTI:
            raise NotImplementedError()
        else:
            raise Exception()

    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> List[str]:
        if form == AdjForm.NORMAL:
            return [adj]

        elif form == AdjForm.NESS:
            return [adj + 'こと']

        elif form == AdjForm.ANTI:
            if not force:
                raise NotImplementedError()

            antonyms: List[str] = []
            # TODO: antonymsを入れる．wordnetでできるか？
            # "美しい" vs "醜い"
            if len(antonyms) == 0 and force:
                antonyms = self._change_adj_form(adj, AdjForm.NEG, force=True)
            return antonyms

        elif form == AdjForm.NEG:
            if not force:
                raise NotImplementedError()

            negnyms: List[str] = []
            # TODO: implement by wordnet
            # 日本語の場合，形容詞にはnegnymが無い？
            # e.g.) "不可能" vs "可能 -> "可能だ"は形容動詞語幹 + だ -> adj形容動詞を入れる必要がある．
            if len(negnyms) == 0 and force:
                negnyms = [_adj.surface + 'ないということ'
                           for _adj in  self._get_katsuyou_morphemes(adj, katsuyous=['連用テ接続'])]
            return negnyms

        else:
            raise ValueError()

    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> List[str]:
        if form == NounForm.NORMAL:
            return [noun]

        elif form == NounForm.SINGULAR:
            return [noun]

        elif form == NounForm.SINGULAR_WITH_PARTICLE:
            return [noun]

        elif form == NounForm.PLURAL:
            return [noun]

        elif form == NounForm.ANTI:
            if not force:
                raise NotImplementedError()

            antonyms: List[str] = []
            # TODO
            if len(antonyms) == 0 and force:
                return self._change_noun_form(noun, NounForm.NEG, force=True)
            return antonyms

        elif form == NounForm.NEG:
            if not force:
                raise NotImplementedError()

            negnyms: List[str] = []
            # TODO
            if len(negnyms) == 0 and force:
                raise NotImplementedError()
                # 「不可能」 -> OK, 「不台風」 -> NO, 「不電話」 -> NO
                # return [f'non-{noun}']
            return negnyms

        else:
            raise ValueError(f'Unknown form {form}')

    def _can_be_intransitive_verb(self, verb: str) -> bool:
        # return self._word_util.can_be_intransitive_verb(verb)
        return True

    def _can_be_transitive_verb(self, verb: str) -> bool:
        # return self._word_util.can_be_transitive_verb(verb)
        return True

    def _can_be_event_noun(self, noun: str) -> bool:
        return self._word_util.can_be_event_noun(noun)

    def _can_be_entity_noun(self, noun: str) -> bool:
        return self._word_util.can_be_entity_noun(noun)

    def get_synonyms(self, word: str) -> List[str]:
        return self._word_util.get_synonyms(word)

    def get_antonyms(self, word: str) -> List[str]:
        return self._word_util.get_antonyms(word)

    def get_negnyms(self, word) -> List[str]:
        raise NotImplementedError()

    def _get_katsuyou_morphemes(self,
                                word: str,
                                katsuyous: Optional[List[str]] = None) -> List[Morpheme]:
        return [morpheme for morpheme in self._base2katsuyous[word]
                if katsuyous is None or morpheme.katsuyou in katsuyous]
