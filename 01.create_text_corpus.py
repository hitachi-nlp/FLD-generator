#!/usr/bin/env python
import logging
from pathlib import Path
import json

import click
from script_engine import QsubEngine, SubprocessEngine
from logger_setup import setup as setup_logger
from lab import build_dir

logger = logging.getLogger(__name__)


@click.command()
def main():
    setup_logger(level=logging.INFO)

    # input_top_dir = Path('./outputs/00.create_json_corpus/20220705.trial/')
    # output_top_dir = Path('./outputs/01.create_text_corpus/20220705.trial/')
    # text_mixin_type = 'MOCK'

    input_top_dir = Path('./outputs/00.create_json_corpus/20220706.format_changed/')
    output_top_dir = Path('./outputs/01.create_text_corpus/20220706.format_changed/')
    text_mixin_type = 'MOCK'

    # engine = QsubEngine('ABCI', 'rt_AG.small')
    engine = SubprocessEngine()

    dry_run = False

    for input_lab_path in input_top_dir.glob('**/*/lab.params.json'):
        settings = json.load(open(input_lab_path))
        settings['text_mixin_type'] = text_mixin_type

        input_top_dir = input_lab_path.parent
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
            'python ./create_text_corpus.py',
            f'{input_top_dir}',
            f'{output_dir}',
            f'--text-mixin-type {settings["text_mixin_type"]}',

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
