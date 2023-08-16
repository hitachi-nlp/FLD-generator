from enum import Enum
from typing import List, Optional, Iterable
from pathlib import Path

from pydantic import BaseModel


def maybe_field(text: str) -> Optional[str]:
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


def load_morphemes(dir_or_csv: str) -> List[Morpheme]:
    path = Path(dir_or_csv)
    if path.is_dir():
        csv_iter: Iterable[Path] = path.glob('**/*.csv')
    else:
        csv_iter = [path]

    morphemes: List[Morpheme] = []
    for csv_path in csv_iter:
        for line in open(str(csv_path)):
            # A line is like as follows:
            # 表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
            # 引き込む,762,762,7122,動詞,自立,*,*,五段・マ行,基本形,引き込む,ヒキコム,ヒキコム"""

            fields = line.rstrip('\n').split(',')
            morphemes.append(
                Morpheme(
                    surface = maybe_field(fields[0]),

                    lid = int(fields[1]) or None,
                    rid = int(fields[2]) or None,
                    cost = int(fields[3]) or None,

                    pos = maybe_field(fields[4]),
                    pos1 = maybe_field(fields[5]),
                    pos2 = maybe_field(fields[6]),
                    pos3 = maybe_field(fields[7]),

                    katsuyou_type = maybe_field(fields[8]),
                    katsuyou = maybe_field(fields[9]),

                    base = maybe_field(fields[10]),
                    yomi = maybe_field(fields[11]),
                    hatsuon = maybe_field(fields[12]),
                )
            )

    return morphemes
