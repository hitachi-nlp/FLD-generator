from pathlib import Path
from typing import List, Optional
import logging
import json

from tqdm import tqdm
from FLD_generator.utils import nested_merge
from FLD_generator.word_banks.base import WordBank, POS, UserWord

from .base import Translator
from .templated import TemplatedTranslator
from .english import EnglishTranslator
from .japanese import JapaneseTranslator
# from .knowledge import MockIfThenKnowledgeTranslator

logger = logging.getLogger(__name__)


def build(lang: str,
          config_paths: List[str],
          word_bank: WordBank,
          adj_verb_noun_ratio: Optional[str] = None,
          insert_word_delimiters=False,
          extra_vocab: Optional[List[UserWord]] = None,
          **kwargs) -> TemplatedTranslator:

    merged_config_json = {}
    for config_path in config_paths:
        _config_path = Path(config_path)
        if _config_path.is_dir():
            all_paths = sorted(_config_path.glob('**/*.json'))
        else:
            all_paths = [_config_path]
        for _path in all_paths:
            logger.info('loading "%s"', str(_path))
            merged_config_json = nested_merge(merged_config_json,
                                              json.load(open(str(_path))))

    adj_verb_noun_ratio = adj_verb_noun_ratio or '1-1-1'
    _adj_verb_noun_ratio = [float(ratio) for ratio in adj_verb_noun_ratio.split('-')]
    if lang == 'eng':
        translator: TemplatedTranslator = EnglishTranslator(
            merged_config_json,
            word_bank,
            adj_verb_noun_ratio=_adj_verb_noun_ratio,
            **kwargs,
        )
    elif lang == 'jpn':
        translator = JapaneseTranslator(
            merged_config_json,
            word_bank,
            adj_verb_noun_ratio=_adj_verb_noun_ratio,
            insert_word_delimiters=insert_word_delimiters,
            extra_vocab=extra_vocab,
            **kwargs,
        )
    else:
        raise ValueError(f'Unsupported language {lang}')
    return translator


# def build_knowledge(*args, **kwargs) -> Translator:
#     return MockIfThenKnowledgeTranslator()
