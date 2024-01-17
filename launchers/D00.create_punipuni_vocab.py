#!/usr/bin/env python
from typing import List, Optional
import logging
import json
from pathlib import Path
from pprint import pformat
import random

from logger_setup import setup as setup_logger
import click


logger = logging.getLogger(__name__)


@click.command()
@click.option('--output_dir', type=str, default='./res/word_banks/japanese/vocab/punipuni')
@click.option('--vary_even_words', is_flag=True, default=False)
@click.option('--fix_odd_words', is_flag=True, default=False)
@click.option('--min_repeats', type=int, default=2)
@click.option('--max_repeats', type=int, default=2)
@click.option('--no_level_postfix', is_flag=True, default=False)
@click.option('--level_lower', type=int, default=0)
@click.option('--level_upper', type=int, default=99)
@click.option('--vocab_size', type=int, default=100000,
              help='XXX: large size will lead to too much memory consumption'
                   'when we handle them by flashtext')
def main(output_dir: str,
         vary_even_words: bool,
         fix_odd_words: bool,
         min_repeats: int,
         max_repeats: int,
         no_level_postfix: bool,
         level_lower: int,
         level_upper: int,
         vocab_size: int):
    setup_logger(do_stderr=True, level=logging.INFO)
    fix_even_words = not vary_even_words

    even_words = [
        # 'す', 'そ',
        'ぴ', 'ぷ', 'ぽ',
        'ま', 'み', 'も',
    ]
    odd_words = [
        'い', 'え',

        # 'ぃ', 'ぇ',

        # 'く', 'け',
        'く',

        'ちゃ', 'ちゅ', 'ちょ',
        'な', 'に', 'ね', 'の',
        'にゃ', 'にゅ', 'にょ',

        'や', 'ゆ', 'よ',
        # 'ゃ', 'ゅ', 'ょ',

        # 'わ', 'を',
        'わ',
    ]

    entity_vocab: List[str] = []
    for n_repeat in range(min_repeats, max_repeats + 1):
        logger.info(f'Generating punipuni vocab with n_repeat={n_repeat} ...')
        seq_len = n_repeat * 2

        def go(heads: List[List[str]], i_pos: int) -> List[List[str]]:
            if i_pos == seq_len:
                return heads

            extended: List[List[str]] = []
            for head in heads:
                if i_pos % 2 == 0:
                    if fix_even_words and len(head) > 0:
                        next_words = [head[0]]
                    else:
                        next_words = even_words
                else:
                    if fix_odd_words and len(head) > 1:
                        next_words = [head[1]]
                    else:
                        next_words = odd_words

                for next_word in next_words:
                    extended.append(head + [next_word])

            return go(extended, i_pos + 1)

        punipunis = [''.join(seq) for seq in go([[]], 0)]

        if no_level_postfix:
            punipunis_with_lv_postfix = punipunis
        else:
            levels = list(range(level_lower, level_upper + 1))
            punipunis_with_lv_postfix = [f'{punipuni}Lv.{level}' for punipuni in punipunis for level in levels]
        entity_vocab.extend(punipunis_with_lv_postfix)

    logger.info('sampling %d words from %d words', vocab_size, len(entity_vocab))
    entity_vocab = random.sample(entity_vocab, vocab_size)
    event_vocab: List[str] = [entity + '事件' for entity in entity_vocab]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'vocab.punipuni.json', 'w') as f:
        json.dump({
            'NOUN.can_be_entity_noun': entity_vocab,
            'NOUN.can_be_event_noun': event_vocab,
        }, f, indent=4, ensure_ascii=False)

    stats = {
        'entity_vocab': len(entity_vocab),
        'event_vocab': len(event_vocab),
    }
    with open(output_dir / 'stats.txt', 'w') as f:
        f.write(pformat(stats))
    logger.info(f'stats:\n{pformat(stats)}')
    logger.info('written to %s', str(output_dir))


if __name__ == '__main__':
    main()
