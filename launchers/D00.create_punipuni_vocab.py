#!/usr/bin/env python
from typing import List
import logging
import json
from pathlib import Path
from pprint import pformat

from logger_setup import setup as setup_logger
import click


logger = logging.getLogger(__name__)


@click.command()
@click.option('--output_dir', type=str, default='./res/word_banks/japanese/punipuni_vocab')
def main(output_dir: str):
    setup_logger(do_stderr=True, level=logging.INFO)

    pu_words = [
        # 'す', 'そ',
        'ぱ', 'ぴ', 'ぷ', 'ぽ',
        'ま', 'み', 'も',
    ]
    yo_words = [
        'な', 'に', 'にょ', 'ね',
        'や', 'ゆ', 'よ',
        'わ',
    ]
    min_repeats = 2
    max_repeats = 3

    entity_vocab: List[str] = []
    for n_repeat in range(min_repeats, max_repeats + 1):
        seq_len = n_repeat * 2

        def go(heads: List[str], i_pos: int) -> List[str]:
            if i_pos == seq_len:
                return heads

            next_words = pu_words if i_pos % 2 == 0 else yo_words

            extended: List[str] = []
            for head in heads:
                for next_word in next_words:
                    extended.append(head + next_word)

            return go(extended, i_pos + 1)

        entity_vocab.extend(go([''], 0))

    event_vocab: List[str] = [entity + '事件' for entity in entity_vocab]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / 'punipuni.json', 'w') as f:
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

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ./launchers/D00.create_punipuni_vocab.py !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


if __name__ == '__main__':
    main()
