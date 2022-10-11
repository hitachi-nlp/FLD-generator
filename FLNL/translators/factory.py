from typing import Optional, List
import json

from FLNL.utils import nested_merge

from FLNL.word_banks.base import WordBank
from FLNL.word_banks import build_wordnet_wordbank
from .clause_typed import ClauseTypedTranslator


def build(config_paths: List[str],
          word_bank: WordBank,
          limit_vocab_size_per_type: Optional[int] = None,
          do_translate_to_nl=True):

    merged_config_json = {}
    for config_path in config_paths:
        merged_config_json = nested_merge(merged_config_json,
                                          json.load(open(config_path)))

    translator = ClauseTypedTranslator(
        merged_config_json,
        word_bank,
        limit_vocab_size_per_type=limit_vocab_size_per_type,
        do_translate_to_nl=do_translate_to_nl,
    )
    return translator
