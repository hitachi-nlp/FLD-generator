#!/usr/bin/env python
import math
import random
import json
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from pprint import pformat
import logging
from collections import defaultdict
import pandas as pd

import click
import dill
from logger_setup import setup as setup_logger

from FLD_generator.utils import fix_seed


logger = logging.getLogger(__name__)


@click.command()
@click.option('--output_dir', type=str, default='./res/word_banks/japanese/vocab/BCCWJ')
@click.option('--bccwj_short_unit_vocab', type=str,
              default='./res/word_banks/japanese/BCCWJ_word_frequency/BCCWJ_frequencylist_suw_ver1_0.tsv')
@click.option('--bccwj_short_unit_rank_limit', type=int, default=30000)
@click.option('--bccwj_long_unit_vocab', type=str,
              default='./res/word_banks/japanese/BCCWJ_word_frequency/BCCWJ_frequencylist_luw2_ver1_0.tsv')
@click.option('--bccwj_long_unit_rank_limit', type=int, default=200000)
@click.option('--sort_col', type=str, default='PB_frequency')
def main(output_dir: str,
         bccwj_short_unit_vocab: str,
         bccwj_short_unit_rank_limit: int,
         bccwj_long_unit_vocab: str,
         bccwj_long_unit_rank_limit: int,
         sort_col: str):
    """
    We make Japanese vocabulary from BCCWJ corpus.
    To choose modern words, we use high-frequency words.
    * references
        * [『現代日本語書き言葉均衡コーパス』語彙表 現代日本語書き言葉均衡コーパス（BCCWJ）](https://clrd.ninjal.ac.jp/bccwj/freq-list.html)
        * [フィールドの名前](https://clrd.ninjal.ac.jp/bccwj/data-files/frequency-list/BCCWJ_frequencylist_manual_ver1_0b.pdf)
    """
    setup_logger(do_stderr=True, level=logging.INFO)
    output_dir = Path(output_dir)

    verbs: Set[str] = set()
    adjs: Set[str] = set()
    can_be_entity_nouns: Set[str] = set()
    can_be_event_nouns: Set[str] = set()
    can_be_predicate_nouns: Set[str] = set()
    for path, rank_limit in zip([bccwj_short_unit_vocab, bccwj_long_unit_vocab],
                                [bccwj_short_unit_rank_limit, bccwj_long_unit_rank_limit]):
        if not Path(path).exists():
            raise FileNotFoundError(f'{path} does not exist. Please download it from https://clrd.ninjal.ac.jp/bccwj/freq-list.html')
        vocab_df = pd.read_csv(path, sep='\t')
        vocab_df = vocab_df.sort_values(sort_col, ascending=False)[:rank_limit or 9999999999]

        verb_df = vocab_df[vocab_df['pos'].map(lambda pos: pos.startswith('動詞'))]
        adj_df = vocab_df[vocab_df['pos'].map(lambda pos: pos.startswith('形容詞'))]

        # We make 'entity' and 'event' exclusive.
        # We also make event and predicate exclusive.
        # '形状詞可能' is same as 形容動詞語幹, such as "きれい(だ)"
        """
            '名詞-普通名詞-一般',       # entity: OK, event: NG, predicate: OK
            '名詞-普通名詞-サ変可能',   # entity: NG, event: OK, predicate: NG
            '名詞-普通名詞-形状詞可能', # entity: NG, event: NG, predicate: OK
            '名詞-固有名詞',            # entity: OK, event: NG, predicate: OK
        """
        can_be_entity_noun_pos = ['名詞-普通名詞-一般', '名詞-固有名詞']
        can_be_event_noun_pos = ['名詞-普通名詞-サ変可能']
        can_be_predicate_noun_pos = ['名詞-普通名詞-一般', '名詞-普通名詞-形状詞可能', '名詞-固有名詞']

        can_be_entity_noun_df = vocab_df[vocab_df['pos'].map(lambda pos: pos in can_be_entity_noun_pos)]
        can_be_event_noun_df = vocab_df[vocab_df['pos'].map(lambda pos: pos in can_be_event_noun_pos)]
        can_be_predicate_noun_df = vocab_df[vocab_df['pos'].map(lambda pos: pos in can_be_predicate_noun_pos)]

        verbs = verbs.union(set(verb_df['lemma'].values))
        adjs = adjs.union(set(adj_df['lemma'].values))
        can_be_entity_nouns = can_be_entity_nouns.union(set(can_be_entity_noun_df['lemma'].values))
        can_be_event_nouns = can_be_event_nouns.union(set(can_be_event_noun_df['lemma'].values))
        can_be_predicate_nouns = can_be_predicate_nouns.union(set(can_be_predicate_noun_df['lemma'].values))

    def dump_json(obj, path: Path):
        with path.open('w') as f:
            json.dump(obj, f, indent=4, ensure_ascii=False)

    _verbs = sorted(verbs)
    _adjs = sorted(adjs)
    _can_be_entity_nouns = sorted(can_be_entity_nouns)
    _can_be_event_nouns = sorted(can_be_event_nouns)
    _can_be_predicate_nouns = sorted(can_be_predicate_nouns)

    output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(
        {
            'NOUN.can_be_entity_noun': _can_be_entity_nouns,
            'NOUN.can_be_event_noun': _can_be_event_nouns,
            'NOUN.can_be_predicate_noun': _can_be_predicate_nouns,
            'VERB.can_be_intransitive_verb': _verbs,
            'VERB.can_be_transitive_verb': _verbs,
            'ADJ': _adjs,
        },
        output_dir / 'vocab.BCCWJ.all.json',
    )
    dump_json(
        {
            'NOUN.can_be_entity_noun': _can_be_entity_nouns,
            'NOUN.can_be_event_noun': _can_be_event_nouns,
            'NOUN.can_be_predicate_noun': _can_be_predicate_nouns,
            'VERB.can_be_intransitive_verb': _verbs,
            'VERB.can_be_transitive_verb': [],
            'ADJ': _adjs,
        },
        output_dir / 'vocab.BCCWJ.wo_transitive_verbs.json',
    )
    dump_json(
        {
            'NOUN.can_be_entity_noun': [],
            'NOUN.can_be_event_noun': [],
            'NOUN.can_be_predicate_noun': _can_be_predicate_nouns,
            'VERB.can_be_intransitive_verb': _verbs,
            'VERB.can_be_transitive_verb': [],
            'ADJ': _adjs,
        },
        output_dir / 'vocab.BCCWJ.wo_transitive_verbs.wo_event_entity_nouns.json',
    )
    dump_json(
        {
            'NOUN.can_be_entity_noun': [],
            'NOUN.can_be_event_noun': [],
            'NOUN.can_be_predicate_noun': [],
            'VERB.can_be_intransitive_verb': _verbs,
            'VERB.can_be_transitive_verb': [],
            'ADJ': _adjs,
        },
        output_dir / 'vocab.BCCWJ.wo_transitive_verbs.wo_all_nouns.json',
    )

    stats = {
        'verbs': len(verbs),
        'adjs': len(adjs),
        'can_be_entity_nouns': len(can_be_entity_nouns),
        'can_be_event_nouns': len(can_be_event_nouns),
        'can_be_predicate_nouns': len(can_be_predicate_nouns),
    }
    with open(output_dir / 'stats.txt', 'w') as f:
        f.write(pformat(stats))
    logger.info(f'stats:\n{pformat(stats)}')

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ./launchers/D00.create_BCCWJ_vocab.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


if __name__ == '__main__':
    main()
