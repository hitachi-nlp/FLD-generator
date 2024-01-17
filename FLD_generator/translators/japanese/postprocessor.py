from typing import Optional, Iterable, List, Dict, Any, Optional, Set, Tuple
from abc import abstractmethod, abstractproperty, ABC
from collections import defaultdict
import random
import re

from ordered_set import OrderedSet
from FLD_generator.word_banks.japanese import JapaneseWordBank, Morpheme, MorphemeParser
from FLD_generator.word_banks.base import UserWord


class Postprocessor(ABC):

    def __init__(self, extra_vocab: Optional[List[UserWord]] = None):
        self._parser = MorphemeParser(extra_vocab=extra_vocab)
    
    @abstractmethod
    def apply(self, text: str) -> str:
        pass
    
    @abstractmethod
    def reset_assets(self) -> None:
        pass


class PostprocessorChain(Postprocessor):

    def __init__(self, postprocessors: List[Postprocessor], extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)
        self._postprocessors = postprocessors

    def apply(self, text: str) -> str:
        text_modified = text
        for postprocessor in self._postprocessors:
            text_modified = postprocessor.apply(text_modified)
        return text_modified

    def reset_assets(self) -> None:
        for postprocessor in self._postprocessors:
            postprocessor.reset_assets()


class WindowRule:

    def __init__(self, word_bank: JapaneseWordBank):
        self._word_bank = word_bank
        self._native_parser = MorphemeParser()

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

    def _get_katsuyou_word(self, morpheme: Morpheme, katsuyou: str) -> Optional[str]:
        katsuyou_morphemes = self._word_bank.get_katsuyou_morphemes(morpheme.base, katsuyous=[katsuyou])
        if len(katsuyou_morphemes) > 0:
            return katsuyou_morphemes[0].surface
        else:
            # long morpheme coming from user vocab, such as "剥がれ落ちる"
            shorter_morphemes = self._native_parser.parse(morpheme.surface)
            if len(shorter_morphemes) <= 1:
                return None
            else:
                last_morpheme = shorter_morphemes[-1]
                last_katsuyou_morphemes = self._word_bank.get_katsuyou_morphemes(last_morpheme.base, katsuyous=[katsuyou])
                if len(last_katsuyou_morphemes) == 0:
                    return None
                else:
                    last_katsuyou_morpheme = last_katsuyou_morphemes[0]
                    return ''.join([morpheme.surface for morpheme in shorter_morphemes[:-1]] + [last_katsuyou_morpheme.surface])

    @abstractmethod
    def reset_assets(self) -> None:
        pass


class WindowRulesPostprocessor(Postprocessor):

    def __init__(self,
                 rules: List[WindowRule],
                 extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)
        self._rules = rules

    def apply(self, text: str) -> str:
        text_modified = text
        for rule in self._rules:
            is_appliable = True
            done_positions: Set[int] = set([])
            while is_appliable:
                morphemes_modified = self._parser.parse(text_modified)
                words_modified_org = [morpheme.surface for morpheme in morphemes_modified]
                words_modified_dst: List[str] = []
                i_end = 0
                is_applied = False
                if len(morphemes_modified) >= rule.window_size:
                    for i, window in enumerate(self._slide(morphemes_modified, rule.window_size)):
                        _modified_words = rule.apply(window)
                        if _modified_words is not None and i not in done_positions:
                            words_modified_dst += _modified_words
                            i_end = i + rule.window_size - 1
                            is_applied = True
                            done_positions.add(i)
                            break
                        else:
                            words_modified_dst.append(window[0].surface)
                            i_end = i
                else:
                    is_applied = False
                    i_end = -1
                is_appliable = is_applied
                words_modified_dst += words_modified_org[i_end + 1:]
                text_modified = ''.join(words_modified_dst)

        return text_modified

    def _slide(self, seq: List[Any], window_size: int) -> Iterable[List[Any]]:
        for i in range(len(seq) - window_size + 1):
            yield seq[i: i + window_size]

    def reset_assets(self) -> None:
        for rule in self._rules:
            rule.reset_assets()


class NarabaKatsuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 3

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if morphemes[0].pos == '動詞' and surfaces[1:] == ['なら', 'ば']:
            # 走るならば -> 走れば
            # 走るなら -> 走るなら (変化無し)
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '仮定形')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ば']

        elif surfaces[:2] == ['だ', 'なら']:
            # きれいだならば -> きれいならば
            # きれいだなら -> きれいなら
            return ['なら', surfaces[2]]

        else:
            return None

    def reset_assets(self) -> None:
        pass


class DaKaKatuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        # 彼はきれいだか楽しい -> 彼はきれいであるか楽しい
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces == ['だ', 'か']:
            return ['である', 'か']
        else:
            return None

    def reset_assets(self) -> None:
        pass


class DaKotoMonoKatuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 3

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        # 彼はきれいだか楽しい -> 彼はきれいであるか楽しい
        koto_mono = ['こと', '事', 'もの', '物']
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces[0] == 'だ' and surfaces[1] in koto_mono:
            return ['な', surfaces[1], surfaces[2]]
        if surfaces[0] == 'だ' and surfaces[1] == '」' and surfaces[2] in koto_mono:
            return ['な', '」', surfaces[2]]
        else:
            return None

    def reset_assets(self) -> None:
        pass


class ShiKatuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if morphemes[0].pos == '動詞' and surfaces[1] == 'し':
            # 走るし青い -> 走って青い (微妙)
            return None
        elif morphemes[0].pos == '形容詞' and surfaces[1] == 'し':
            # 彼は赤いし青い -> 彼は赤くて青い
            if random.random() < 0.5:
                katsuyou_word = self._get_katsuyou_word(morphemes[0], '連用テ接続')
                if katsuyou_word is None:
                    return None
                else:
                    return [katsuyou_word, 'て']
            else:
                return None

        elif surfaces == ['だ', 'し']:
            if random.random() < 0.5:
                # きれいだし -> きれいで
                return ['で']
            else:
                return None
        elif surfaces[0] == 'だし':
            # parsing with user words sometimes fails, such as 「ぽにょぽにょだし...」 into 「ぽにょぽにょ/だし/...」
            if random.random() < 0.5:
                return ['で'] + surfaces[1:]
            else:
                return None

        elif surfaces == ['ない', 'し']:
            if random.random() < 0.5:
                # 走らないし -> 走らなくて
                return ['なく', 'て']
            else:
                return None
        elif surfaces[0] == ['ないし']:
            # parsing with user words sometimes fails, such as 「ググるないし...」 into 「グルる/ないし/...」
            if random.random() < 0.5:
                return ['なくて'] + surfaces[1:]
            else:
                return None

        else:
            return None

    def reset_assets(self) -> None:
        pass


class NaiKatsuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]

        if morphemes[0].pos == '動詞' and surfaces[1] in ['ない', 'ないし']:
            # 走るない -> 走らない
            # 会議する -> 会議しない

            if morphemes[0].base.endswith('する'):
                # as 'する' has more than two 未然形, we explicitly specify it
                katsuyou_word = re.sub('する$', '', morphemes[0].base) + 'し'
            else:
                katsuyou_word = self._get_katsuyou_word(morphemes[0], '未然形')

            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, surfaces[1]]

        elif surfaces[0] == 'だ' and surfaces[1] in ['ない', 'ないし']:
            # きれいだない -> きれいでない
            # きれいだないし赤い -> きれいでないし赤い
            return ['で', surfaces[1]]

        elif morphemes[0].pos == '形容詞' and surfaces[1] in ['ない', 'ないし']:
            if surfaces[0] == 'く':  # sometimes 'く'(ない) is parsed as 形容詞
                return None

            # 美しいない -> 美しくない
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '連用テ接続')
            if katsuyou_word is None:
                if surfaces[0].endswith('い'):
                    # should be something like "夫婦らしい"
                    return [surfaces[0][:-1] + 'く', surfaces[1]]
                else:
                    return None
            else:
                return [katsuyou_word, surfaces[1]]

        else:
            return None

    def reset_assets(self) -> None:
        pass


class NaiNaiKatsuyouRule(WindowRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces[0] == 'ない' and surfaces[1] in ['ない', 'ないし']:
            return ['なく', surfaces[1]]
        else:
            return None

    def reset_assets(self) -> None:
        pass


class KakuRandomOrderRule(WindowRule):

    def __init__(self,
                 word_bank: JapaneseWordBank,
                 kaku_list: List[str]):
        self._word_bank = word_bank
        self._kaku_list = kaku_list

    @property
    def window_size(self) -> int:
        return 4

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        # XXX: この実装だとダメ．「赤い人間が猫を追う」 => 「赤い猫を人間が追う」 <<phrase::da_dearu>>になってしまう．
        # おそらく，構文解析が必要となる．
        # surfaces = [morpheme.surface for morpheme in morphemes]
        # if surfaces[1] in ['は', 'が'] and surfaces[3] in self._kaku_list:
        #     return [surfaces[2], surfaces[3], surfaces[1], surfaces[0]]
        # else:
        #     return None
        raise NotImplementedError()

    def reset_assets(self) -> None:
        pass


class UniqueKOSOADOPostprocessor(Postprocessor):

    _KOSOADO = ['この', 'その', 'あの']

    def __init__(self,
                 extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)
        self._obj_to_kosoado: Dict[str, str] = {}

    def apply(self, text: str) -> str:
        morphemes = self._parser.parse(text)
        obj_to_kosoados: Dict[str, Set[str]] = defaultdict(set)
        for i, morepheme in enumerate(morphemes):
            if morepheme.surface in self._KOSOADO and i + 1 < len(morphemes):
                obj = morphemes[i + 1]
                obj_to_kosoados[obj.surface].add(morepheme.surface)

        text_modified = text
        for obj, kosoados in obj_to_kosoados.items():
            if obj in self._obj_to_kosoado:
                unique_kosoado = self._obj_to_kosoado[obj]
            else:
                unique_kosoado = random.choice(list(kosoados))
            self._obj_to_kosoado[obj] = unique_kosoado

            for possible_kosoado in kosoados:
                text_modified = text_modified.replace(possible_kosoado + obj, unique_kosoado + obj)

        return text_modified

    def reset_assets(self) -> None:
        self._obj_to_kosoado: Dict[str, str] = {}


def build_postprocessor(word_bank: JapaneseWordBank) -> WindowRulesPostprocessor:
    extra_vocab = word_bank.extra_vocab
    return PostprocessorChain([
        WindowRulesPostprocessor(
            [
                # XXX: the order of rules matters
                NarabaKatsuyouRule(word_bank),
                # add extra_vocab as argument
                DaKaKatuyouRule(word_bank),
                DaKotoMonoKatuyouRule(word_bank),
                NaiKatsuyouRule(word_bank),
                NaiNaiKatsuyouRule(word_bank),
                # KakuRandomOrderRule(word_bank),
                ShiKatuyouRule(word_bank),
            ],
            extra_vocab=extra_vocab,
        ),
        UniqueKOSOADOPostprocessor(extra_vocab=extra_vocab),
    ])
