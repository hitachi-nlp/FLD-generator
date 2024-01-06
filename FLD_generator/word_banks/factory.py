from typing import Set, Optional, Dict, Union, List, Iterable
import logging

from FLD_generator.word_banks.base import WordBank, POS, UserWord
from .english import EnglishWordBank
from .japanese import JapaneseWordBank, load_morphemes

logger = logging.getLogger(__name__)


def build(
    lang: str,
    transitive_verbs_path: Optional[str] = None,
    intransitive_verbs_path: Optional[str] = None,
    vocab: Optional[List[UserWord]] = None,
) -> WordBank:
    logger.info('Building word bank for language=%s ...', lang)

    if lang == 'eng':

        if transitive_verbs_path is None:
            transitive_verbs_path = './res/word_banks/english/transitive_verbs.txt'
        transitive_verbs = set(line.strip('\n') for line in open(transitive_verbs_path))

        if intransitive_verbs_path is None:
            intransitive_verbs_path = './res/word_banks/english/intransitive_verbs.txt'
        intransitive_verbs = set(line.strip('\n') for line in open(intransitive_verbs_path))

        return EnglishWordBank(
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            vocab=vocab,
        )

    elif lang == 'jpn':

        if transitive_verbs_path is not None:
            raise NotImplementedError()
        transitive_verbs = None

        if intransitive_verbs_path is not None:
            raise NotImplementedError()
        intransitive_verbs = None

        jpn_dict_csvs_dir = './res/word_banks/japanese/mecab/mecab-ipadic/'
        jpn_morphemes = load_morphemes(jpn_dict_csvs_dir)
        return JapaneseWordBank(
            jpn_morphemes,
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            vocab=vocab,
        )

    else:
        raise ValueError(f'Unknown language "{lang}"')
