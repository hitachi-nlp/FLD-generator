from typing import Set, Optional, Dict, Union, List

from .base import WordNetWordBank, POS
from .english import EnglishWordBank
from .japanese import JapaneseWordBank


def build(
    lang: str,
    vocab_restrictions: Optional[Dict[Union[POS, str], Union[Set[str], List[str]]]] = None
) -> WordNetWordBank:

    if lang == EnglishWordBank.language:
        klass = EnglishWordBank
    elif lang == JapaneseWordBank.language:
        klass = JapaneseWordBank
    else:
        raise ValueError(f'Unknown language "{lang}"')

    if vocab_restrictions is not None:
        _vocab_restrictions = {}
        for pos, words in vocab_restrictions.items():
            if not isinstance(pos, POS):
                _pos = POS(pos)
            else:
                _pos = pos
            words = set(words)

            _vocab_restrictions[_pos] = words
    else:
        _vocab_restrictions = vocab_restrictions

    return klass(vocab_restrictions=_vocab_restrictions)
