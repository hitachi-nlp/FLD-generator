#!/usr/bin/env python
import logging
from typing import List
from pathlib import Path

import click
from script_engine import QsubEngine, SubprocessEngine
from logger_setup import setup as setup_logger
from lab import build_dir

logger = logging.getLogger(__name__)


def _make_multiple_value_option(option: str, values: List[str]) -> str:
    return ' '.join([
        f'{option} {value}'
        for value in values
    ])


@click.command()
def main():
    setup_logger(level=logging.INFO)

    # corpus_name = '20220827.trial'
    output_top_dir = Path('./outputs/10.create_formal_logic_corpus/20220827.trial')

    argument_configs = [
        './configs/formal_logic/arguments/LP.axiom.pred_only.json',
        './configs/formal_logic/arguments/LP.theorem.pred_only.json',

        './configs/formal_logic/arguments/LP.axiom.pred_arg.json',
        './configs/formal_logic/arguments/LP.theorem.pred_arg.json',
    ]
    translation_configs = [
        './configs/formal_logic/translations/clause_typed.thing.json'
    ]

    split_sizes = {
        'train': 100,
        'valid': 10,
        'test': 10,
    }
    depth = 3
    complication = 0.3
    quantification = 0.2
    distractor_factor = 3
    world_assump = 'label_true_only'

    # engine = QsubEngine('ABCI', 'rt_AG.small')
    engine = SubprocessEngine()

    dry_run = False

    for split, size in split_sizes.items():

        settings = {
            # 'corpus_name': corpus_name,
            'split': split,

            'size': size,

            'argument_configs': argument_configs,
            'translation_configs': translation_configs,

            'depth': depth,
            'complication': complication,
            'quantification': quantification,
            'distractor_factor': distractor_factor,
            'world_assump': world_assump,
        }

        output_dir = build_dir(
            settings,
            # top_dir=str(output_top_dir / settings["corpus_name"]),
            top_dir=str(output_top_dir),
            short=True,
            dirname_exclude_params=[
                'corpus_name',
                'split',

                'argument_configs',
                'translation_configs',
                'size',
            ],
            save_params=True
        )
        output_path = output_dir / f'{split}.jsonl'
        log_path = output_dir / f'log.{split}txt'

        command = ' '.join([
            'python ./create_formal_logic_corpus.py',

            f'{output_path}',
            f'{settings["size"]}',

            _make_multiple_value_option('--ac', settings['argument_configs']),
            _make_multiple_value_option('--tc', settings['translation_configs']),

            f'--depth {settings["depth"]}',
            f'--complication {settings["complication"]}',
            f'--quantification {settings["quantification"]}',
            f'--distractor-factor {settings["distractor_factor"]}',
            f'--world-assump {settings["world_assump"]}',
            f'1>{str(log_path)} 2>&1',
        ])

        if isinstance(engine, SubprocessEngine):
            stdout = None
            stderr = None
            wait_until_finish = True
        else:
            command += f' 1>{str(log_path)} 2>&1'
            stdout = output_dir / 'stdout.txt'
            stderr = output_dir / 'stderr.txt'
            wait_until_finish = False
        engine.run(
            command,
            stdout=stdout,
            stderr=stderr,
            options={'l_opts': ['h_rt=12:00:00']},
            dry_run=dry_run,
            wait_until_finish=wait_until_finish,
        )
    logger.info('10.create_formal_logic_corpus.py done!')


if __name__ == '__main__':
    main()
