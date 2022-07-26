#!/usr/bin/env python
import logging
from pathlib import Path

import click
from script_engine import QsubEngine, SubprocessEngine
from logger_setup import setup as setup_logger
from lab import build_dir

logger = logging.getLogger(__name__)


@click.command()
def main():
    setup_logger(level=logging.INFO)

    # output_top_dir = Path('./outputs/00.create_json_corpus/20220705.trial')
    # output_top_dir = Path('./outputs/00.create_json_corpus/20220706.format_changed')
    # output_top_dir = Path('./outputs/00.create_json_corpus/20220707.small')
    output_top_dir = Path('./outputs/00.create_json_corpus/debug')

    config = './configs/aacorpus/conf_syllogistic_corpus-02.json'
    corpus_name = 'org'

    split_sizes = {
        # original size
        # 'train': 9000,
        # 'test': 100,

        'train': 10,
        'valid': 10,
        'test': 10,
    }

    # engine = QsubEngine('ABCI', 'rt_AG.small')
    engine = SubprocessEngine()

    dry_run = False

    for split, size in split_sizes.items():

        settings = {
            'corpus_name': corpus_name,
            'split': split,
            'config': config,
            'size': size
        }

        output_dir = build_dir(
            settings,
            top_dir=str(output_top_dir / settings["corpus_name"] / settings["split"]),
            short=True,
            dirname_exclude_params=[
                'corpus_name',
                'split',
                'config',
                'size',
            ],
            save_params=True
        )

        log_path = output_dir / 'log.txt'
        command = ' '.join([
            'python ./create_json_corpus.py',
            f'{settings["corpus_name"]}',
            f'{settings["split"]}',
            f'--output-dir {output_dir}',
            f'--config {settings["config"]}',
            f'--size {settings["size"]}',
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
            options={'l_opts': ['h_rt=3:00:00']},
            dry_run=dry_run,
            wait_until_finish=wait_until_finish,
        )


if __name__ == '__main__':
    main()
