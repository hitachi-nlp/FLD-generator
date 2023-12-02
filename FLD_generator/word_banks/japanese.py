from typing import Optional, Iterable, List, Dict, Any, Optional
from collections import defaultdict
from enum import Enum
from abc import abstractmethod, abstractproperty
from pprint import pprint

from ordered_set import OrderedSet
from FLD_generator.word_banks.base import POS
from FLD_generator.word_banks.base import WordBank
from FLD_generator.word_banks.parsers.japanese import parse
from FLD_generator.person_names import get_person_names
import line_profiling

from .parsers.japanese import Morpheme
from .word_utils import WordUtil


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
        NEG = 'neg'

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

    INTERMEDIATE_CONSTANT_PREFIXES = [
        '事物',
        '人物',
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
        morphemes = [morpheme for morpheme in morphemes
                     if morpheme.pos in ['名詞', '動詞', '形容詞']]
        self._all_morphemes = sorted(morphemes)

        self._morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        self._base_morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        self._katsuyou_morphemes: Dict[str, List[Morpheme]] = defaultdict(list)
        for morpheme in morphemes:
            self._morphemes[morpheme.surface].append(morpheme)
            if morpheme.surface == morpheme.base:
                self._base_morphemes[morpheme.base].append(morpheme)
            else:
                self._katsuyou_morphemes[morpheme.base].append(morpheme)

        self._word_util = WordUtil(
            'jpn',
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            vocab_restrictions=vocab_restrictions,
        )

        self._person_names: OrderedSet[str] = OrderedSet(get_person_names(country='US'))

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
                self._morphme_pos_to_POS.get(morpheme.pos, POS.OTHERS)
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
            antonyms += [
                word
                for word in self._change_adj_form(adj, self.AdjForm.NEG, force=False)
                if word not in antonyms]

            if len(antonyms) == 0 and force:
                antonyms += self._change_adj_form(adj, self.AdjForm.NEG, force=True)

            return antonyms

        elif form == self.AdjForm.NEG:
            """
            日本語の場合，形容詞にはnegnymが無いと思われる．
            きれい vs 醜い     -> これはantonymである．
            きれい vs 非きれい -> これがnegnymだが，言葉として存在しない．
            """
            raise ValueError('Japanese do not have negnyms.')

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

    def _get_antonyms(self, word: str) -> List[str]:
        return self._word_util.get_antonyms(word)

    def get_katsuyou_morphemes(self,
                               word: str,
                               katsuyous: Optional[List[str]] = None) -> List[Morpheme]:
        return [morpheme for morpheme in self._katsuyou_morphemes[word]
                if katsuyous is None or morpheme.katsuyou in katsuyous]


class KatsuyouRule:

    @abstractproperty
    def window_size(self) -> int:
        pass

    def apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        if len(morphemes) != self.window_size:
            raise ValueError()
        words = self._apply(morphemes)
        # if words is not None and len(words) != self.window_size:
        #     raise Exception('bug')
        return words

    @abstractmethod
    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        pass


class NarabaRule(KatsuyouRule):

    def __init__(self, word_bank: JapaneseWordBank):
        self._word_bank = word_bank

    @property
    def window_size(self) -> int:
        return 3

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        """
        surface='起こる' lid=None rid=None cost=None pos='動詞' pos1='自立' pos2=None pos3=None katsuyou_type='五段・ラ行' katsuyou='基本形' base='起こる' yomi='オコル' hatsuon='オコル'
        surface='なら' lid=None rid=None cost=None pos='助動詞' pos1=None pos2=None pos3=None katsuyou_type='特殊・ダ' katsuyou='仮定形' base='だ' yomi='ナラ' hatsuon='ナラ'
        surface='ば' lid=None rid=None cost=None pos='助詞' pos1='接続助詞' pos2=None pos3=None katsuyou_type=None katsuyou=None base='ば' yomi='バ' hatsuon='バ'
        """
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces == ['だ', 'なら', 'ば']:  # きれいだならば
            return ['ならば']
        elif morphemes[0].pos == '動詞' and surfaces[1:] == ['なら', 'ば']:  # 走るならば
            verb_katsuyous = self._word_bank.get_katsuyou_morphemes(morphemes[0].base, katsuyous=['仮定形'])
            if len(verb_katsuyous) == 0:
                return None
            else:
                return [verb_katsuyous[0].surface + 'ば']
        else:
            return None


class Katsuyou:

    def __init__(self, rules: List[KatsuyouRule]):
        self._rules = rules

    def apply(self, text: str) -> str:
        text_modified = text
        for rule in self._rules:
            is_appliable = True
            while is_appliable:
                morphemes_modified = parse(text_modified)
                words_modified_org = [morpheme.surface for morpheme in morphemes_modified]
                words_modified_dst: List[str] = []
                i_done = 0
                is_applied = False
                for i, window in enumerate(self._slide(morphemes_modified, rule.window_size)):
                    _katsuyou_words = rule.apply(window)
                    if _katsuyou_words is not None:
                        words_modified_dst += _katsuyou_words
                        i_done = i + rule.window_size - 1
                        is_applied = True
                        break
                    else:
                        words_modified_dst.append(window[0].surface)
                        i_done = i
                is_appliable = is_applied
                words_modified_dst += words_modified_org[i_done + 1:]
                text_modified = ''.join(words_modified_dst)

        return text_modified

    def _slide(self, seq: List[Any], window_size: int) -> Iterable[List[Any]]:
        for i in range(len(seq) - window_size + 1):
            yield seq[i: i + window_size]
