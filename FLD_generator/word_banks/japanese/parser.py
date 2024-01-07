from enum import Enum
from typing import List, Optional, Iterable, Any, Dict
from pathlib import Path
from functools import lru_cache
import logging
import re

from fugashi import GenericTagger
from pydantic import BaseModel
import ipadic

from FLD_generator.word_banks.base import WordBank, POS, ATTR, UserWord

logger = logging.getLogger(__name__)
_TAGGER = GenericTagger(ipadic.MECAB_ARGS)


def _maybe_field(elems: List[str], i: int) -> Optional[str]:
    if i >= len(elems):
        return None

    text = elems[i]
    if text == '':
        return None
    elif text == '*':
        return None
    else:
        return text


NAIYOUGO_POS = ['名詞', '動詞', '形容詞']


def morpheme_POS_to_WB_POS(pos: str) -> POS:
    if pos == '名詞':
        return POS.NOUN
    elif pos == '動詞':
        return POS.VERB
    elif pos == '形容詞':
        return POS.ADJ
    elif pos == '副詞':
        return POS.ADV
    else:
        return POS.OTHERS


def WB_POS_to_morpheme_POS(pos: POS) -> str:
    if pos == POS.NOUN:
        return '名詞'
    elif pos == POS.VERB:
        return '動詞'
    elif pos == POS.ADJ:
        return '形容詞'
    elif pos == POS.ADV:
        return '副詞'
    else:
        return 'その他'


class Morpheme(BaseModel):
    surface: Optional[str] = None

    lid: Optional[int] = None
    rid: Optional[int] = None
    cost: Optional[int] = None

    pos: Optional[str] = None
    pos1: Optional[str] = None
    pos2: Optional[str] = None
    pos3: Optional[str] = None

    katsuyou_type: Optional[str] = None
    katsuyou: Optional[str] = None

    base: Optional[str] = None
    yomi: Optional[str] = None
    hatsuon: Optional[str] = None

    misc: Dict = {}

    def __lt__(self, other: 'Morpheme'):
        return self.surface < other.surface

    def __repr__(self):
        return f'{super().__repr__()}'


class MorphemeParser:

    def __init__(self, extra_vocab: Optional[List[UserWord]] = None):
        self.extra_vocab = {word.lemma: word for word in extra_vocab} if extra_vocab else {}
        self._sep = '📙'

        if len(self.extra_vocab) > 0:
            self._user_word_regexp = re.compile(
                '|'.join(
                    sorted((word.lemma for word in self.extra_vocab.values()),
                           key=lambda x: - len(x))
                )
            )
        else:
            self._user_word_regexp = None

    def parse(self, text: str) -> List[Morpheme]:
        text_org = text
        if self._user_word_regexp is not None:
            text = self._user_word_regexp.sub(lambda x: f'{self._sep}{x.group(0)}{self._sep}', text)
            # if text != text_org:
            #     logger.debug('We parse the text with user word markers, as folllows:'
            #                  '\noriginal     : %s'
            #                  '\nwith markers : %s',
            #                  text_org, text)

        morphemes = _parse(text)
        morphemes_with_user_words: List[Morpheme] = []
        inner_user_word_morphemes: List[Morpheme] = []
        is_inner_user_word = False
        for morpheme in morphemes:
            if not is_inner_user_word and morpheme.surface == self._sep:
                is_inner_user_word = True
                continue

            if is_inner_user_word and morpheme.surface == self._sep:
                user_word_lemma = ''.join(_morpheme.surface for _morpheme in inner_user_word_morphemes)
                if user_word_lemma not in self.extra_vocab:
                    logger.warning('User word "%s" is not found in the user vocab.'
                                   ' This could be caused by a bug, or that the original sentence includes the special separator "%s".',
                                   user_word_lemma,
                                   self._sep)
                    morphemes_with_user_words.extend(inner_user_word_morphemes)
                    inner_user_word_morphemes = []
                    is_inner_user_word = False
                    continue

                user_word = self.extra_vocab[user_word_lemma]
                if len(inner_user_word_morphemes) == 1 and inner_user_word_morphemes[0].pos == user_word.pos:
                    # might be ok as it is, which is more informative as it includes results from the morphological analysis
                    # typically, verbs such as "走る", "歩く" pass here
                    user_morpheme = inner_user_word_morphemes[0]
                else:
                    user_morpheme = Morpheme(
                        surface=user_word.lemma,
                        pos=WB_POS_to_morpheme_POS(user_word.pos),
                        base=user_word.lemma,
                    )
                user_morpheme.misc['vocab_type'] = 'user'
                morphemes_with_user_words.append(user_morpheme)
                inner_user_word_morphemes = []
                is_inner_user_word = False
                continue

            if is_inner_user_word:
                inner_user_word_morphemes.append(morpheme)
            else:
                morphemes_with_user_words.append(morpheme)


        return morphemes_with_user_words

    @lru_cache(maxsize=1000000)
    def get_lemma(self, word: str) -> str:
        return self.parse(word)[0].base


def load_morphemes(dir_or_csv: str) -> List[Morpheme]:
    path = Path(dir_or_csv)
    if path.is_dir():
        csv_iter: Iterable[Path] = path.glob('**/*.csv')
    else:
        csv_iter = [path]

    morphemes: List[Morpheme] = []
    for csv_path in csv_iter:
        for line in open(str(csv_path), encoding='euc_jp'):
            # A line is like as follows:
            # 表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
            # 引き込む,762,762,7122,動詞,自立,*,*,五段・マ行,基本形,引き込む,ヒキコム,ヒキコム"""

            fields = line.rstrip('\n').split(',')
            morphemes.append(
                Morpheme(
                    surface = _maybe_field(fields, 0),

                    lid = int(fields[1]) or None,
                    rid = int(fields[2]) or None,
                    cost = int(fields[3]) or None,

                    pos = _maybe_field(fields, 4),
                    pos1 = _maybe_field(fields, 5),
                    pos2 = _maybe_field(fields, 6),
                    pos3 = _maybe_field(fields, 7),

                    katsuyou_type = _maybe_field(fields, 8),
                    katsuyou = _maybe_field(fields, 9),

                    base = _maybe_field(fields, 10),
                    yomi = _maybe_field(fields, 11),
                    hatsuon = _maybe_field(fields, 12),
                )
            )

    return morphemes


def _parse(text: str) -> List[Morpheme]:
    result = _TAGGER.parse(text)

    morphemes: List[Morpheme] = []
    for line in result.split('\n'):
        if line.rstrip('\n') == 'EOS':
            break

        surface, fields_str = line.split('\t')
        fields = fields_str.split(',')
        morphemes.append(
            Morpheme(
                surface=surface,

                lid=None,
                rid=None,
                cost=None,

                pos = _maybe_field(fields, 0),
                pos1 = _maybe_field(fields, 1),
                pos2 = _maybe_field(fields, 2),
                pos3 = _maybe_field(fields, 3),

                katsuyou_type = _maybe_field(fields, 4),
                katsuyou = _maybe_field(fields, 5),

                base = _maybe_field(fields, 6),
                yomi = _maybe_field(fields, 7),
                hatsuon = _maybe_field(fields, 8),


            )
        )
    return morphemes
