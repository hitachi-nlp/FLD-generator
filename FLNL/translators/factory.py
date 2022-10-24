from typing import Optional, List
import json

from FLNL.utils import nested_merge

from FLNL.word_banks.base import WordBank
from FLNL.word_banks import build_wordnet_wordbank
from .clause_typed import ClauseTypedTranslator


def build(config_paths: List[str],
          word_bank: WordBank,
          reuse_object_nouns=False,
          limit_vocab_size_per_type: Optional[int] = None,
          volume_to_weight: str = 'linear',
          do_translate_to_nl=True):

    merged_config_json = {}
    for config_path in config_paths:
        merged_config_json = nested_merge(merged_config_json,
                                          json.load(open(config_path)))

    translator = ClauseTypedTranslator(
        merged_config_json,
        word_bank,
        reuse_object_nouns=reuse_object_nouns,
        limit_vocab_size_per_type=limit_vocab_size_per_type,
        volume_to_weight=volume_to_weight,
        do_translate_to_nl=do_translate_to_nl,
    )
    return translator