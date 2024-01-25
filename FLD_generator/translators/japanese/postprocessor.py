from typing import Optional, Iterable, List, Dict, Any, Optional, Set, Tuple, Union
from abc import abstractmethod, abstractproperty, ABC
from collections import defaultdict
import random
import re
from pprint import pprint

from ordered_set import OrderedSet
from FLD_generator.word_banks.japanese import JapaneseWordBank, Morpheme, MorphemeParser
from FLD_generator.word_banks.base import UserWord


_KOTO_MONO_NOUNS = ['こと', '事', 'もの', '物', '者', 'モンスター']
_STATE_PREDS = [
    '正しい',
    '真実',
    '事実',
    '本当',
    '確か',
    '誤り',
    '間違い',
    '偽',
    '事実',
    '嘘',
    '誤っ',
    '間違っ',
]

_OCCUR_VERBS = ['起こる', '起きる', '発生', '生じる']


def _slide(seq: List[Any], window_size: int) -> Iterable[List[Any]]:
    for i in range(len(seq) - window_size + 1):
        yield seq[i: i + window_size]


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
                    for i, window in enumerate(_slide(morphemes_modified, rule.window_size)):
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
        # きれいだもの -> きれいなもの
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces[0] == 'だ' and surfaces[1] in _KOTO_MONO_NOUNS:
            return ['な', surfaces[1], surfaces[2]]
        if surfaces[0] == 'だ' and surfaces[1] == '」' and surfaces[2] in _KOTO_MONO_NOUNS:
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
        elif surfaces[0] == 'ある' and surfaces[1] in ['ない', 'ないし']:
            # きれいであるない -> きれいでない
            return [surfaces[1]]

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


class ZeroAnaphoraPostprocessor(Postprocessor):

    def __init__(self, extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)

    def apply(self, text: str) -> str:
        morphemes = self._parser.parse(text)
        morphemes_processed = []
        do_skip = False
        for window in _slide(morphemes, 2):
            if window[0].surface == 'それ' and window[1].surface in ['は', 'が']:
                if random.random() < 0.5:
                    do_skip = True
                    continue
            if do_skip:
                do_skip = False
                continue
            morphemes_processed.append(window[0])
        morphemes_processed.append(morphemes[-1])

        return ''.join(m.surface for m in morphemes_processed)

    def reset_assets(self) -> None:
        pass


class UniqueKOSOADOPostprocessor(Postprocessor):

    _KOSOADO = ['この', 'その', 'あの']

    def __init__(self, extra_vocab: Optional[List[UserWord]] = None):
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


class HaGaUsagePostprocessor(Postprocessor):
    """ convert last が to は in a block of 「...」

    See "「は」「が」の使い分け" in FLD-docs/japanese/NLP_2024/README.md for details.
    """

    _SHARED_SUBJECT_MAX_INTERVAL = 5

    _ha_morpheme = Morpheme(surface='は', lid=None, rid=None, cost=None, pos='助詞', pos1='係助詞', pos2=None,
                            pos3=None, katsuyou_type=None, katsuyou=None, base='は', yomi='ハ', hatsuon='ワ', misc={})
    _ga_morpheme = Morpheme(surface='が', lid=None, rid=None, cost=None, pos='助詞', pos1='格助詞', pos2='一般',
                            pos3=None, katsuyou_type=None, katsuyou=None, base='が', yomi='ガ', hatsuon='ガ', misc={})

    # XXX: ALWAYS follow ShiKatuyouRule
    _parallel_morphemes = [
        # ---- and like morphemes ----
        Morpheme(surface='し', lid=None, rid=None, cost=None, pos='動詞', pos1='自立', pos2=None, pos3=None,
                 katsuyou_type='サ変・スル', katsuyou='連用形', base='する', yomi='シ', hatsuon='シ', misc={}),
        Morpheme(surface='し', lid=None, rid=None, cost=None, pos='助詞', pos1='接続助詞', pos2=None,
                 pos3=None, katsuyou_type=None, katsuyou=None, base='し', yomi='シ', hatsuon='シ', misc={}),

        # 走るししかも is sometimes parses as 「走る/しし/かも」
        Morpheme(surface='しし', lid=None, rid=None, cost=None, pos='名詞', pos1='一般', pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='しし', yomi='シシ', hatsuon='シシ', misc={}),

        Morpheme(surface='て', lid=None, rid=None, cost=None, pos='助詞', pos1='接続助詞', pos2=None,
                 pos3=None, katsuyou_type=None, katsuyou=None, base='て', yomi='テ', hatsuon='テ', misc={}),

        Morpheme(surface='で', lid=None, rid=None, cost=None, pos='助詞', pos1='格助詞', pos2='一般', pos3=None,
                 katsuyou_type=None, katsuyou=None, base='で', yomi='デ', hatsuon='デ', misc={}),
        Morpheme(surface='で', lid=None, rid=None, cost=None, pos='助動詞', pos1=None, pos2=None, pos3=None,
                 katsuyou_type='特殊・ダ', katsuyou='連用形', base='だ', yomi='デ', hatsuon='デ', misc={}),

        # sometime, 「赤くないし青くない」 is wrongly parsed into 「赤く/ないし/青く/ない」
        Morpheme(surface='ないし', lid=None, rid=None, cost=None, pos='接続詞', pos1=None, pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='ないし', yomi='ナイシ', hatsuon='ナイシ', misc={}),


        # ---- or like morphemes ----
        Morpheme(surface='か', lid=None, rid=None, cost=None, pos='助詞', pos1='副助詞／並立助詞／終助詞', pos2=None,
                 pos3=None, katsuyou_type=None, katsuyou=None, base='か', yomi='カ', hatsuon='カ', misc={}),
        # somethines, 「赤いかまたは青い」 is wrongly parsed into 「赤い/かまた/は/青い」
        Morpheme(surface='かまた', lid=None, rid=None, cost=None, pos='名詞', pos1='固有名詞', pos2='人名', pos3='姓',
                 katsuyou_type=None, katsuyou=None, base='かまた', yomi='カマタ', hatsuon='カマタ', misc={}),


        # ---- and but like morphemes ----
        Morpheme(surface='が', lid=None, rid=None, cost=None, pos='助詞', pos1='格助詞', pos2='一般', pos3=None,
                 katsuyou_type=None, katsuyou=None, base='が', yomi='ガ', hatsuon='ガ', misc={}),
        Morpheme(surface='が', lid=None, rid=None, cost=None, pos='助詞', pos1='接続助詞', pos2=None,
                 pos3=None, katsuyou_type=None, katsuyou=None, base='が', yomi='ガ', hatsuon='ガ', misc={}),

        Morpheme(surface='けど', lid=None, rid=None, cost=None, pos='接続詞', pos1=None, pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='けど', yomi='ケド', hatsuon='ケド', misc={}),
        Morpheme(surface='けど', lid=None, rid=None, cost=None, pos='助詞', pos1='接続助詞', pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='けど', yomi='ケド', hatsuon='ケド', misc={}),

        Morpheme(surface='けれど', lid=None, rid=None, cost=None, pos='接続詞', pos1=None, pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='けれど', yomi='ケレド', hatsuon='ケレド', misc={}),
        Morpheme(surface='けれど', lid=None, rid=None, cost=None, pos='助詞', pos1='接続助詞', pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='けれど', yomi='ケレド', hatsuon='ケレド', misc={}),

        Morpheme(surface='一方', lid=None, rid=None, cost=None, pos='接続詞', pos1=None, pos2=None, pos3=None,
                 katsuyou_type=None, katsuyou=None, base='一方', yomi='イッポウ', hatsuon='イッポー', misc={}),
    ]

    # ---- implication like morphemes ----
    _implication_morphemes = [
        # surface='と' lid=None rid=None cost=None pos='助詞' pos1='接続助詞' pos2=None pos3=None katsuyou_type=None katsuyou=None base='と' yomi='ト' hatsuon='ト' misc={}
        # surface='ば' lid=None rid=None cost=None pos='助詞' pos1='接続助詞' pos2=None pos3=None katsuyou_type=None katsuyou=None base='ば' yomi='バ' hatsuon='バ' misc={}

    ]

    def __init__(self,
                 extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)

    def apply(self, text: str) -> str:
        morphemes = self._parser.parse(text)
        morphemes_processed = morphemes.copy()

        haga_positions_block_stack: List[List[int]] = []
        parallel_positions_block_stack: List[List[int]] = []
        for i_pos, morpheme in enumerate(morphemes):

            if morpheme.surface == '「' or i_pos == 0:
                is_degenerate = morpheme.surface == '「' and i_pos == 0
                for _ in range(2 if is_degenerate else 1):
                    haga_positions_block_stack.append([])
                    parallel_positions_block_stack.append([])
                continue

            if morpheme.surface == '」' or i_pos == len(morphemes) - 1:
                is_degenerate = morpheme.surface == '」' and i_pos == len(morphemes) - 1
                for _ in range(2 if is_degenerate else 1):
                    done_haga_positions = haga_positions_block_stack.pop()
                    if len(done_haga_positions) >= 2:
                        for pos in done_haga_positions[:-1]:
                            morphemes_processed[pos] = self._ga_morpheme
                        for pos in done_haga_positions[-1:]:   # i.e., -1
                            morphemes_processed[pos] = self._ha_morpheme

                        # share は・が before and after an and morpheme
                        done_parallel_positions = parallel_positions_block_stack.pop()
                        for parallel_pos in done_parallel_positions:
                            for left_pos, right_pos in [done_haga_positions[i: i + 2] for i in range(0, len(done_haga_positions) - 1)]:
                                if left_pos < parallel_pos < right_pos:  # Xは..し，Yが.. というように，「またぐ」構造になっている．
                                    # 並列構造になっているかどうかを判定するヒューリスティック
                                    if morphemes[right_pos - 1].surface == 'それ'\
                                            or right_pos - left_pos <= self._SHARED_SUBJECT_MAX_INTERVAL:
                                        morphemes_processed[left_pos] = morphemes_processed[right_pos]
                continue

            def match(maybe_morpheme: Optional[Morpheme], attr: str, gold: Union[str, List[str]]) -> bool:
                if maybe_morpheme is None:
                    return False
                if not hasattr(maybe_morpheme, attr):
                    return False
                else:
                    if isinstance(gold, str):
                        return getattr(maybe_morpheme, attr) == gold
                    elif isinstance(gold, list):
                        return getattr(maybe_morpheme, attr) in gold
                    else:
                        raise ValueError()

            prev_morpheme = morphemes[i_pos - 1] if i_pos - 1 >= 0 else None
            prev_prev_morpheme = morphemes[i_pos - 2] if i_pos - 2 >= 0 else None
            next_morepheme = morphemes[i_pos + 1] if i_pos + 1 < len(morphemes) else None

            is_subject_ha = morpheme == self._ha_morpheme\
                and (match(prev_morpheme, 'pos', '名詞') or match(prev_morpheme, 'surface', '」'))
            should_kept_ha = morpheme == self._ha_morpheme\
                and (
                    (match(prev_morpheme, 'surface', _KOTO_MONO_NOUNS) and match(next_morepheme, 'surface', _STATE_PREDS))
                    or (match(prev_morpheme, 'surface', _KOTO_MONO_NOUNS) and match(prev_prev_morpheme, 'surface', 'という'))
                    or match(prev_morpheme, 'surface', ['また', 'かまた', 'もしく', 'あるい'])
                )

            is_subject_ga = morpheme == self._ga_morpheme\
                and (
                    # 何"が"しかのもの
                    (match(prev_morpheme, 'pos', '名詞') and not match(prev_morpheme, 'surface', ['何', 'なに', '何ら']))
                    or match(prev_morpheme, 'surface', '」')
                )
            should_kept_ga = morpheme == self._ga_morpheme\
                and (
                    (match(prev_morpheme, 'surface', _KOTO_MONO_NOUNS) and match(next_morepheme, 'surface', _STATE_PREDS))
                    or match(next_morepheme, 'surface', _OCCUR_VERBS)
                )

            is_parallel_conjunction = morpheme in self._parallel_morphemes\
                and not is_subject_ga and not is_subject_ha\
                and not (morpheme.surface == 'し' and match(next_morepheme, 'surface', 'たら'))

            if is_subject_ha and not should_kept_ha:
                haga_positions_block_stack[-1].append(i_pos)
            if is_subject_ga and not should_kept_ga:
                haga_positions_block_stack[-1].append(i_pos)
            if is_parallel_conjunction:
                parallel_positions_block_stack[-1].append(i_pos)

        return ''.join(m.surface for m in morphemes_processed)

    def reset_assets(self) -> None:
        pass


def build_postprocessor(word_bank: JapaneseWordBank,
                        postprocessors: Optional[List[Postprocessor]] = None) -> Postprocessor:
    extra_vocab = word_bank.extra_vocab
    postprocessors = postprocessors or [
        # XXX: THE ORDER OF RULES MATTERS!!
        WindowRulesPostprocessor(
            [
                NarabaKatsuyouRule(word_bank),
                DaKaKatuyouRule(word_bank),
                DaKotoMonoKatuyouRule(word_bank),
                NaiKatsuyouRule(word_bank),
                NaiNaiKatsuyouRule(word_bank),
                ShiKatuyouRule(word_bank),
            ],
            extra_vocab=extra_vocab,
        ),
        UniqueKOSOADOPostprocessor(extra_vocab=extra_vocab),
        HaGaUsagePostprocessor(extra_vocab=extra_vocab),
        ZeroAnaphoraPostprocessor(extra_vocab=extra_vocab),
    ]
    return PostprocessorChain(postprocessors)
