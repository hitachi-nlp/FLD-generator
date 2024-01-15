from pathlib import Path
from typing import List, Optional, Union
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


def _get_config_paths(name_or_path: Union[str, List[str]], lang: str) -> List[str]:
    if isinstance(name_or_path, list):
        return name_or_path

    if Path(name_or_path).is_dir():
        return [str(p) for p in Path(name_or_path).glob('**/*.json')]
    elif Path(name_or_path).is_file():
        return [name_or_path]
    else:
        if lang == 'eng':
            if name_or_path == 'thing':
                return _get_config_paths('./configs/translations/eng/thing_person.v0/', lang)
            else:
                raise ValueError()
        elif lang == 'jpn':
            if name_or_path == 'thing':
                return _get_config_paths('./configs/translations/jpn/thing.v1/', lang)
            elif name_or_path == 'punipuni':
                paths = [path
                         for path in _get_config_paths('./configs/translations/jpn/thing.v1/', lang)
                         if not path.endswith('phrase.json')]
                paths.append('./configs/translations/jpn/punipuni/phrases.json')
                return paths
            else:
                raise ValueError()
        else:
            raise ValueError()



def build(lang: str,
          config_name_or_path: List[str],
          word_bank: WordBank,
          adj_verb_noun_ratio: Optional[str] = None,
          insert_word_delimiters=False,
          **kwargs) -> TemplatedTranslator:

    config_paths = _get_config_paths(config_name_or_path, lang)

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
            **kwargs,
        )
    else:
        raise ValueError(f'Unsupported language {lang}')
    return translator


# def build_knowledge(*args, **kwargs) -> Translator:
#     return MockIfThenKnowledgeTranslator()
