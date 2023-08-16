from typing import Set, Optional, Dict, Union, List, Iterable

from .base import WordNetWordBank, POS
from .english import EnglishWordBank


def build(
    lang: str,
    transitive_verbs_path: Optional[str] = None,
    intransitive_verbs_path: Optional[str] = None,
    vocab_restrictions: Optional[Dict[Union[POS, str], Union[Iterable[str]]]] = None
) -> WordNetWordBank:

    if vocab_restrictions is not None:
        _vocab_restrictions: Optional[Dict[POS, Set[str]]] = {}
        for pos, words in vocab_restrictions.items():
            if not isinstance(pos, POS):
                _pos = POS(pos)
            else:
                _pos = pos
            words = set(words)

            _vocab_restrictions[_pos] = words
    else:
        _vocab_restrictions = None

    if lang == EnglishWordBank.language:
        if transitive_verbs_path is None:
            transitive_verbs_path = './res/word_banks/english/transitive_verbs.txt'
        transitive_verbs = set(line.strip('\n') for line in open(transitive_verbs_path))

        if intransitive_verbs_path is None:
            intransitive_verbs_path = './res/word_banks/english/intransitive_verbs.txt'
        intransitive_verbs = set(line.strip('\n') for line in open(intransitive_verbs_path))

        return EnglishWordBank(
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            vocab_restrictions=_vocab_restrictions,
        )

    elif lang == JapaneseWordBank.language:
        raise NotImplementedError()

    else:
        raise ValueError(f'Unknown language "{lang}"')
