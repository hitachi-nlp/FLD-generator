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

    output_top_dir = Path('./outputs/10.create_formal_logic_corpus/20220802.minumum')

    argument_config = './configs/formal_logic/arguments/minumum.json'
    translation_config = './configs/formal_logic/sentence_translations/syllogistic_corpus-02.json'
    corpus_name = 'minumum'

    split_sizes = {
        'train': 1000,
        'valid': 100,
        'test': 100,
    }
    depth = 3
    num_distractors = 3
    world_assump = 'label_true_only'
    elim_dneg = True

    # engine = QsubEngine('ABCI', 'rt_AG.small')
    engine = SubprocessEngine()

    dry_run = False

    for split, size in split_sizes.items():

        settings = {
            'corpus_name': corpus_name,

            'argument_config': argument_config,
            'translation_config': translation_config,

            'split': split,
            'size': size,
            'depth': depth,
            'num_distractors': num_distractors,
            'world_assump': world_assump,
            'elim_dneg': elim_dneg,
        }

        output_dir = build_dir(
            settings,
            top_dir=str(output_top_dir / settings["corpus_name"]),
            short=True,
            dirname_exclude_params=[
                'argument_config',
                'translation_config',

                'corpus_name',
                'split',
            ],
            save_params=True
        )
        output_path = output_dir / f'{split}.jsonl'
        log_path = output_dir / 'log.txt'

        command = ' '.join([
            'python ./create_formal_logic_corpus.py',

            f'{output_path}',
            f'{settings["argument_config"]}',
            f'{settings["translation_config"]}',
            f'{settings["size"]}',

            f'--depth {settings["depth"]}',
            f'--num-distractors {settings["num_distractors"]}',
            f'--world-assump {settings["world_assump"]}',
            '--elim-dneg' if settings["elim_dneg"] else '',
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
            options={'l_opts': ['h_rt=3:00:00']},
            dry_run=dry_run,
            wait_until_finish=wait_until_finish,
        )


if __name__ == '__main__':
    main()
