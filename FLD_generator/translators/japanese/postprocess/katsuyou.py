from typing import Optional, Iterable, List, Dict, Any, Optional, Set, Tuple
from abc import abstractmethod, abstractproperty

from ordered_set import OrderedSet
from FLD_generator.word_banks.japanese import JapaneseWordBank, Morpheme, parse


class KatsuyouRule:

    def __init__(self, word_bank: JapaneseWordBank):
        self._word_bank = word_bank

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
        if len(katsuyou_morphemes) == 0:
            return None
        else:
            return katsuyou_morphemes[0].surface


class NarabaKatsuyouRule(KatsuyouRule):

    @property
    def window_size(self) -> int:
        return 3

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if morphemes[0].pos == '動詞' and surfaces[1:] == ['なら', 'ば']:
            # 走るならば -> 走れば
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '仮定形')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ば']

        elif surfaces == ['だ', 'なら', 'ば']:
            # きれいだならば -> きれいならば
            return ['なら', 'ば']

        else:
            return None


class NaiKatsuyouRule(KatsuyouRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if morphemes[0].pos == '動詞' and surfaces[1] == 'ない':
            # 走るない -> 走らない
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '未然形')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ない']

        elif surfaces == ['だ', 'ない']:
            # きれいだならば -> きれいならば
            return ['で', 'ない']

        elif morphemes[0].pos == '形容詞' and surfaces[1] == 'ない':
            # 美しいない -> 美しくない
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '連用テ接続')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ない']

        else:
            return None


class NaiNaiKatsuyouRule(KatsuyouRule):

    @property
    def window_size(self) -> int:
        return 2

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if surfaces == ['ない', 'ない']:
            return ['なく', 'ない']
        else:
            return None


class KakuRandomOrderRule(KatsuyouRule):

    @property
    def window_size(self) -> int:
        return 4

    def _apply(self, morphemes: List[Morpheme]) -> Optional[List[str]]:
        surfaces = [morpheme.surface for morpheme in morphemes]
        if morphemes[0].pos == '動詞' and surfaces[1] == 'ない':
            # 走るない -> 走らない
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '未然形')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ない']

        elif surfaces == ['だ', 'ない']:
            # きれいだならば -> きれいならば
            return ['で', 'ない']

        elif morphemes[0].pos == '形容詞' and surfaces[1] == 'ない':
            # 美しいない -> 美しくない
            katsuyou_word = self._get_katsuyou_word(morphemes[0], '連用テ接続')
            if katsuyou_word is None:
                return None
            else:
                return [katsuyou_word, 'ない']

        else:
            return None




class KatsuyouTransformer:

    def __init__(self, rules: List[KatsuyouRule]):
        self._rules = rules

    def apply(self, text: str) -> str:
        text_modified = text
        for rule in self._rules:
            is_appliable = True
            done_windows: Set[Tuple[Tuple[str, Any], ...]] = set([])
            while is_appliable:
                morphemes_modified = parse(text_modified)
                words_modified_org = [morpheme.surface for morpheme in morphemes_modified]
                words_modified_dst: List[str] = []
                i_end = 0
                is_applied = False
                for i, window in enumerate(self._slide(morphemes_modified, rule.window_size)):
                    _katsuyou_words = rule.apply(window)
                    window_tuple = tuple(tuple(morpheme)for morpheme in window)
                    if _katsuyou_words is not None and window_tuple not in done_windows:
                        words_modified_dst += _katsuyou_words
                        i_end = i + rule.window_size - 1
                        is_applied = True
                        done_windows.add(window_tuple)
                        break
                    else:
                        words_modified_dst.append(window[0].surface)
                        i_end = i
                is_appliable = is_applied
                words_modified_dst += words_modified_org[i_end + 1:]
                text_modified = ''.join(words_modified_dst)

        return text_modified

    def _slide(self, seq: List[Any], window_size: int) -> Iterable[List[Any]]:
        for i in range(len(seq) - window_size + 1):
            yield seq[i: i + window_size]


def build_katsuyou_transformer(word_bank: JapaneseWordBank) -> KatsuyouTransformer:
    # XXX: the order of rules matters
    rules = [
        NarabaKatsuyouRule(word_bank),
        NaiKatsuyouRule(word_bank),
        NaiNaiKatsuyouRule(word_bank),
    ]
    return KatsuyouTransformer(rules)
