from typing import Optional, Iterable, List, Dict, Any, Optional, Set, Tuple, Union
from collections import defaultdict
from enum import Enum
from abc import abstractmethod, abstractproperty
from pprint import pprint
import logging
import json
from collections import defaultdict
from pathlib import Path

from ordered_set import OrderedSet
from FLD_generator.word_banks.base import POS, ATTR
from FLD_generator.word_banks.base import WordBank, UserWord
from FLD_generator.person_names import get_person_names
from FLD_generator.word_banks.word_utils import WordUtil
import line_profiling

from .parser import (
    Morpheme,
    NAIYOUGO_POS,
    morpheme_POS_to_WB_POS,
    WB_POS_to_morpheme_POS,
)


logger = logging.getLogger(__name__)


class JapaneseWordBank(WordBank):

    class VerbForm(Enum):
        """ https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html """
        NORMAL = 'normal'
        ING = 'ing'
        S = 's'

        KOTO = 'koto'

        ANTI = 'anti'

    class AdjForm(Enum):
        NORMAL = 'normal'
        NESS = 'ness'

        ANTI = 'anti'
        # NEG = 'neg'

    class PresentForm(Enum):
        NORMAL = 'normal'

    class PastForm(Enum):
        NORMAL = 'normal'

    class NounForm(Enum):
        NORMAL = 'normal'
        SINGULAR = 's'
        SINGULAR_WITH_PARTICLE = 'swa'
        PLURAL = 'p'   # not implemented

        ANTI = 'anti'
        NEG = 'neg'

    # INTERMEDIATE_CONSTANT_PREFIXES = [
    #     '事物',
    #     '人物',
    # ]

    def __init__(self,
                 morphemes: List[Morpheme],
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 extra_vocab: Optional[List[UserWord]] = None,
                 intermediate_constant_prefix: Optional[str] = None):
        super().__init__(extra_vocab=extra_vocab,
                         intermediate_constant_prefix=intermediate_constant_prefix)

        self._word_util = WordUtil(
            'jpn',
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            extra_vocab=extra_vocab,
        )

        self._person_names: OrderedSet[str] = OrderedSet([name for name in get_person_names(country='JP')
                                                          if not name.isascii()])

        morphemes = [morpheme for morpheme in morphemes
                     if morpheme.pos in NAIYOUGO_POS]

        self._morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        self._base_morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        self._katsuyou_morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        for morpheme in morphemes:
            surface = morpheme.surface
            base = morpheme.base

            self._morphemes[surface].append(morpheme)
            if surface == base:
                self._base_morphemes[base].append(morpheme)
            else:
                self._katsuyou_morphemes[base].append(morpheme)

        if extra_vocab is not None:
            for user_word in extra_vocab:
                base = user_word.lemma
                pos = user_word.pos
                mtc_morphemes = [morpheme for morpheme in self._morphemes.get(base, [])
                                 if morpheme.pos == WB_POS_to_morpheme_POS(pos)]
                if len(mtc_morphemes) == 0:
                    # logger.info('could not find the extra word "%s" in the canonical morpheme list. Will create a morpheme by ourselves.', lemma)
                    mtc_morphemes = [
                        Morpheme(surface=base,
                                 pos=WB_POS_to_morpheme_POS(pos),
                                 base=base)
                    ]

                for mtc_morpheme in mtc_morphemes:
                    surface = mtc_morpheme.surface

                    self._morphemes[surface].append(mtc_morpheme)
                    if surface == base:
                        # self._base_morphemes[base].append(mtc_morpheme)
                        # we override the canonical morphemes, so that only the user words are used.
                        self._base_morphemes[base] = [mtc_morpheme]
                    else:
                        # We prioritize but do not ovierride the canonical morphemes, as we may want to rely on canonical morphemes for katsuyou.
                        self._katsuyou_morphemes[base] = [mtc_morpheme] + self._katsuyou_morphemes[base]

    def _get_all_lemmas(self) -> Iterable[str]:
        for morphemes in self._base_morphemes.values():
            for morpheme in morphemes:
                yield morpheme.surface
        for name in self._person_names:
            yield name

    def _get_pos(self, word: str) -> List[POS]:
        if word in self._person_names:
            return [POS.NOUN]

        if word not in self._base_morphemes:
            return []
        else:
            morphemes = self._base_morphemes[word]
            return list({
                morpheme_POS_to_WB_POS(morpheme.pos)
                for morpheme in morphemes
            })

    def _change_verb_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.VerbForm.NORMAL, self.VerbForm.ING, self.VerbForm.S, self.VerbForm.KOTO]:

            if form == self.VerbForm.NORMAL:
                return [self._word_util.get_lemma(verb)]

            elif form == self.VerbForm.ING:
                verbs: List[str] = []
                for morpheme in self.get_katsuyou_morphemes(
                    verb,
                    katsuyous=[
                        '連用タ接続',
                        '連用形',
                        '未然形',  # very rare: "寇す" ->  寇し(未然形)
                    ]
                ):
                    if morpheme.surface[-1] == 'ん':
                        verbs.append(morpheme.surface + 'でいる')
                    else:
                        verbs.append(morpheme.surface + 'ている')
                    # break to use the first match katsyoukei because
                    # for some morpheme they have both '連用タ接続'(correct) and '連用形(incorrect)'
                    # but for some other morpheme they have only '連用形(correct)'
                    break

                if len(verbs) == 0 and force:
                    raise NotImplementedError()

                return verbs

            elif form == self.VerbForm.S:
                return [verb]

            elif form == self.VerbForm.KOTO:
                # 走ること
                return [verb + 'こと']

            raise Exception()

        elif form == self.VerbForm.ANTI:
            antonyms = self._get_antonyms(verb)

            if len(antonyms) == 0 and force:
                raise NotImplementedError()

            return antonyms

        else:
            raise ValueError()

    def _change_adj_form(self, adj: str, form: Enum, force=False) -> List[str]:

        if form == self.AdjForm.NORMAL:
            return [adj]

        elif form == self.AdjForm.NESS:
            return [adj + 'ということ']

        elif form == self.AdjForm.ANTI:
            raise NotImplementedError(
                'antonyms from the wordbank are low-quality, and thus we have to refine the logic in the wordbank.')

            antonyms = self._get_antonyms(adj)
            # antonyms += [
            #     word
            #     for word in self._change_adj_form(adj, self.AdjForm.NEG, force=False)
            #     if word not in antonyms
            # ]

            # if len(antonyms) == 0 and force:
            #     antonyms += self._change_adj_form(adj, self.AdjForm.NEG, force=True)

            return antonyms

        elif form == self.AdjForm.NEG:
            """
            日本語の場合，形容詞にはnegnymが無いと思われる．
            きれい vs 醜い     -> これはantonymである．
            きれい vs 非きれい -> これがnegnymだが，言葉として存在しない．
            """
            raise ValueError('Japanese adjective do not have negnyms.')

        else:
            raise ValueError()

    def _change_present_particle_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.PresentForm.NORMAL]:
            return [verb]
        else:
            raise ValueError()

    def _change_past_particle_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.PastForm.NORMAL]:
            return [verb]
        else:
            raise ValueError()

    def _change_noun_form(self, noun: str, form: Enum, force=False) -> List[str]:

        if form == self.NounForm.NORMAL:
            if noun in self._person_names:
                return [noun]

            return [noun]

        elif form == self.NounForm.SINGULAR:
            if noun in self._person_names:
                return [noun]

            return [noun]

        elif form == self.NounForm.SINGULAR_WITH_PARTICLE:
            if noun in self._person_names:
                return [noun]

            return [noun]

        elif form == self.NounForm.PLURAL:
            if noun in self._person_names:
                return []

            return [noun]

        elif form == self.NounForm.ANTI:
            if noun in self._person_names:
                return []

            raise NotImplementedError(
                'antonyms from the wordbank are low-quality, and thus we have to refine the logic in the wordbank.')

            antonyms = self._get_antonyms(noun)
            antonyms += [word for word in self._change_noun_form(noun, self.NounForm.NEG, force=False)
                         if word not in antonyms]

            if len(antonyms) == 0 and force:
                return self._change_noun_form(noun, self.NounForm.NEG, force=True)

            return antonyms

        elif form == self.NounForm.NEG:
            if noun in self._person_names:
                return []

            negnyms: List[str] = []

            negnym_candidates = [f'{neg_prefix}{noun}'
                                 for neg_prefix in ['無', '不', '未', '非']]
            for negnym_candidate in negnym_candidates:
                if negnym_candidate in self._base_morphemes:
                    negnyms.append(negnym_candidate)

            if len(negnyms) == 0 and force:
                negnyms = negnym_candidates

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
        if noun in self._person_names:
            return False
        return self._word_util.can_be_event_noun(noun)

    def _can_be_entity_noun(self, noun: str) -> bool:
        if noun in self._person_names:
            return True
        return self._word_util.can_be_entity_noun(noun)

    def _can_be_predicate_noun(self, noun: str) -> bool:
        return not self._can_be_entity_noun(noun) and not self._can_be_event_noun(noun)

    def _get_antonyms(self, word: str) -> List[str]:
        return self._word_util.get_antonyms(word)

    def get_katsuyou_morphemes(self,
                               word: str,
                               katsuyous: Optional[List[str]] = None) -> List[Morpheme]:
        return [morpheme for morpheme in self._katsuyou_morphemes[word]
                if katsuyous is None or morpheme.katsuyou in katsuyous]


def load_jp_extra_vocab(path: Union[str, List[str]],
                        ng_words: List[str] = None) -> List[UserWord]:
    ng_words = ng_words or []

    if isinstance(path, list):
        all_paths = path
    else:
        if Path(path).is_dir():
            all_paths = list(Path(path).glob('**/*.json'))
        else:
            all_paths = [Path(path)]
    vocab_jsons = []
    for _path in all_paths:
        logger.info(f'loading vocaburaly {_path}')
        vocab_jsons.append(json.load(open(str(_path))))

    word_pos_pairs: Set[Tuple[str, POS]] = set([])
    attrs: Dict[Tuple[str, POS], Dict[str, bool]] = defaultdict(lambda: {_attr.value: False for _attr in ATTR})
    for vocab_json in vocab_jsons:
        for key, words in vocab_json.items():
            if key.find('.') >= 0:
                pos_str, attr = key.split('.')
            else:
                pos_str = key
                attr = None
            pos = POS(pos_str)

            for word in words:
                word_pos_pairs.add((word, pos))
                if attr is not None:
                    attrs[(word, pos)][attr] = True

    # we need two-pass loading, as the words can appear multiple times for different attrs.
    vocab: List[UserWord] = []
    for word, pos in word_pos_pairs:
        if word in ng_words:
            continue
        _attrs = attrs[(word, pos)]
        vocab.append(UserWord(lemma=word, pos=pos, **_attrs))

    return vocab