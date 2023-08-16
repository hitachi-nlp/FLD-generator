from typing import List

from fugashi import GenericTagger
import ipadic

from .morpheme import Morpheme, maybe_field

_TAGGER = GenericTagger(ipadic.MECAB_ARGS)

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

                pos = maybe_field(fields[0]),
                pos1 = maybe_field(fields[1]),
                pos2 = maybe_field(fields[2]),
                pos3 = maybe_field(fields[3]),

                katsuyou_type = maybe_field(fields[4]),
                katsuyou = maybe_field(fields[5]),

                base = maybe_field(fields[6]),
                yomi = maybe_field(fields[7]),
                hatsuon = maybe_field(fields[8]),


            )
        )
    return morphemes
