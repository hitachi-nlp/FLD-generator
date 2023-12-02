from enum import Enum
from typing import List, Optional, Iterable, Any
from pathlib import Path
from functools import lru_cache

from fugashi import GenericTagger
from pydantic import BaseModel
import ipadic

_TAGGER = GenericTagger(ipadic.MECAB_ARGS)


def _maybe_field(text: str) -> Optional[str]:
    if text == '':
        return None
    elif text == '*':
        return None
    else:
        return text


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

    def __lt__(self, other: 'Morpheme'):
        return self.surface < other.surface

    def __repr__(self):
        return f'Morpheme({super().__repr__()})'


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
                    surface = _maybe_field(fields[0]),

                    lid = int(fields[1]) or None,
                    rid = int(fields[2]) or None,
                    cost = int(fields[3]) or None,

                    pos = _maybe_field(fields[4]),
                    pos1 = _maybe_field(fields[5]),
                    pos2 = _maybe_field(fields[6]),
                    pos3 = _maybe_field(fields[7]),

                    katsuyou_type = _maybe_field(fields[8]),
                    katsuyou = _maybe_field(fields[9]),

                    base = _maybe_field(fields[10]),
                    yomi = _maybe_field(fields[11]),
                    hatsuon = _maybe_field(fields[12]),
                )
            )

    return morphemes


def parse(text: str) -> List[Morpheme]:
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

                pos = _maybe_field(fields[0]),
                pos1 = _maybe_field(fields[1]),
                pos2 = _maybe_field(fields[2]),
                pos3 = _maybe_field(fields[3]),

                katsuyou_type = _maybe_field(fields[4]),
                katsuyou = _maybe_field(fields[5]),

                base = _maybe_field(fields[6]),
                yomi = _maybe_field(fields[7]),
                hatsuon = _maybe_field(fields[8]),


            )
        )
    return morphemes


@lru_cache(maxsize=1000000)
def get_lemma(word: str) -> str:
    return parse(word)[0].base
