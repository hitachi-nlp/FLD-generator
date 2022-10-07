#!/usr/bin/env python
import json
import math
import logging
from typing import List
from pathlib import Path
import copy

import click
from script_engine import QsubEngine, SubprocessEngine
from logger_setup import setup as setup_logger, create_file_handler
from lab import build_dir, save_params
from joblib import Parallel, delayed
from experimental_settings import get_dataset_setting

logger = logging.getLogger(__name__)


def _make_multiple_value_option(option: str, values: List[str]) -> str:
    return ' '.join([
        f'{option} {value}'
        for value in values
    ])


@click.command()
def main():
    setup_logger(level=logging.INFO)
    logger.info('============================== [10.create_FLNL_corpus.py] start! ============================')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220827.trial')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/debug')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220828.size--100')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220828.size--100000')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220830.various_datasets.trial')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220831.various_datasets.trial')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220901.various_datasets.trial')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220902.disproof-off')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220909.various_levels')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220910.various_levels.wo_disproof')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220910.various_levels.w_disproof')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220910.various_levels.w_disproof.wo_marker')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220916.unknown.trial')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220916.UNKNOWN')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220917.UNKNOWN')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220919.UNKNOWN.fix_translation')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220929.assump')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220929.assump.void')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221001.assump.void.large')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221002.assump_brace')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221002.assump_brace.large')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20220928.neg_tree_distractor')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221002.neg_tree_distractor.more')

    output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221007.add-axioms-theorems')

    dataset_names = [
        # '20220901.atmf-P.arg-basic.dpth-1',
        # '20220901.atmf-PA.arg-basic.dpth-1',
        # '20220901.atmf-PA.arg-compl.dpth-1',
        # '20220901.atmf-PA.arg-compl.dpth-3',
        # '20220901.atmf-PA.arg-compl.dpth-5',

        # '20220916.atmf-P.arg-basic.dpth-1.UNKNOWN',
        # '20220916.atmf-PA.arg-basic.dpth-1.UNKNOWN',
        # '20220916.atmf-PA.arg-compl.dpth-1.UNKNOWN',
        # '20220916.atmf-PA.arg-compl.dpth-3.UNKNOWN',
        # '20220916.atmf-PA.arg-compl.dpth-5.UNKNOWN',

        # '20220929.atmf-PA.arg-compl.dpth-3.20220929.assump.debug',
        # '20220929.atmf-PA.arg-compl.dpth-3.20221001.assump.void',
        # '20220929.atmf-PA.arg-compl.dpth-5.20221001.assump.void',

        # '20220928.atmf-P.arg-basic.dpth-1.neg_tree_distractor',
        # '20220928.atmf-PA.arg-basic.dpth-1.neg_tree_distractor',
        # '20220928.atmf-PA.arg-compl.dpth-1.neg_tree_distractor',
        # '20220928.atmf-PA.arg-compl.dpth-3.neg_tree_distractor',
        # '20220928.atmf-PA.arg-compl.dpth-5.neg_tree_distractor',

        # '20221002.atmf-PA.arg-compl.dpth-3.neg_tree_distractor.more',
        # '20221002.atmf-PA.arg-compl.dpth-5.neg_tree_distractor.more',

        '20221007.atmf-PA.arg-compl.dpth-3.add-axioms-theorems',
        '20221007.atmf-PA.arg-compl.dpth-5.add-axioms-theorems',
        '20221007.atmf-PA.arg-compl.dpth-10.add-axioms-theorems',
    ]

    split_sizes = {
        # 'train': 100,
        # 'valid': 100,
        # 'test': 100,

        'train': 100000,
        'valid': 1000,
        'test': 1000,
    }

    # engine = SubprocessEngine()
    engine = QsubEngine('ABCI', 'rt_C.small')

    # num_jobs = 1
    num_jobs = 100

    # num_workers_per_job = 1
    num_workers_per_job = 5

    timeout_per_job = 600  # for the case some jobs hangs
    dry_run = False

    # ----------------- fixed ------------------
    for dataset_name in dataset_names:
        settings = {
            'dataset_name': dataset_name,
            'num_workers_per_job': num_workers_per_job,
        }
        settings.update(get_dataset_setting(dataset_name))

        output_dir = build_dir(
            settings,
            top_dir=str(output_top_dir / f'dataset_name={dataset_name}'),
            short=True,
            dirname_exclude_params=[
                'dataset_name',
                'proof_stances',

                'argument_configs',

                'complication',
                'quantification',

                'depth',
                'branch_extension_steps',
                'distractor',
                'distractor_factor',

                'translation_configs',

                'num_workers_per_job',

                'world_assump',
            ],
            save_params=True
        )
        logger.addHandler(create_file_handler(output_dir / 'log.txt'))

        min_size_per_job = 100    # too small value might be slow.
        for split, size in split_sizes.items():
            size_with_margin = int(size * 1.1)   # for the case some jobs fail or hang

            split_output_dir = output_dir / split
            split_output_dir.mkdir(exist_ok=True, parents=True)

            if size_with_margin / num_jobs < min_size_per_job:
                _num_jobs = max(math.ceil(size_with_margin / min_size_per_job), 1)
            else:
                _num_jobs = num_jobs
            size_per_job = math.ceil(size_with_margin / _num_jobs)

            logger.info('============================== [10.create_FLNL_corpus.py] Generating dataset for %s split ============================', split)
            logger.info('size: %d', size)
            logger.info('size_with_margin: %d', size_with_margin)
            logger.info('num_jobs: %d', _num_jobs)
            logger.info('size_per_job: %d', size_per_job)

            jobs = []
            for i_job in range(_num_jobs):
                job_output_dir = split_output_dir / f'job-{str(i_job).zfill(6)}'
                job_output_dir.mkdir(exist_ok=True, parents=True)

                job_output_path = job_output_dir / f'{split}.jsonl'
                job_log_path = job_output_dir / 'log.txt'

                job_settings = copy.deepcopy(settings)
                job_settings['split'] = split
                job_settings['seed'] = i_job

                save_params(job_settings, job_output_dir)

                command = ' '.join([
                    'python ./create_FLNL_corpus.py',

                    f'{job_output_path}',
                    str(int(size_per_job)),

                    _make_multiple_value_option('--ac', job_settings['argument_configs']),
                    _make_multiple_value_option('--tc', job_settings['translation_configs']),

                    f'--depth {job_settings["depth"]}',
                    f'--branch-extension-steps {job_settings["branch_extension_steps"]}',
                    f'--complication {job_settings["complication"]}',
                    f'--quantification {job_settings["quantification"]}',
                    f'--distractor {job_settings["distractor"]}',
                    f'--distractor-factor {job_settings["distractor_factor"]}',
                    f'--proof-stances \'{json.dumps(job_settings["proof_stances"])}\'',
                    f'--world-assump {job_settings["world_assump"]}',
                    f'--num-workers {job_settings["num_workers_per_job"]}',
                    f'--seed {job_settings["seed"]}',
                ])

                if isinstance(engine, SubprocessEngine):
                    command += f' 2>&1 | tee {str(job_log_path)}'
                    stdout = None
                    stderr = None
                else:
                    command += f' 1>{str(job_log_path)} 2>&1'
                    stdout = job_output_dir / 'stdout.txt'
                    stderr = job_output_dir / 'stderr.txt'

                jobs.append(
                    delayed(engine.run)(
                        command,
                        stdout=stdout,
                        stderr=stderr,
                        options={
                            'l_opts': ['h_rt=12:00:00'],
                            'timeout_from_run': timeout_per_job,
                        },
                        dry_run=dry_run,
                        wait_until_finish=True,
                    )
                )

            logger.info('waiting %d jobs to be finished...', len(jobs))
            Parallel(n_jobs=_num_jobs, backend='threading')(jobs)

            logger.info('gathering results under %s', split_output_dir)
            cnt = 0
            is_done = False
            with open(split_output_dir / f'{split}.jsonl', 'w') as f_out:
                for jsonl in sorted(split_output_dir.glob(f'**/*{split}.jsonl')):
                    if is_done:
                        break
                    for line in open(jsonl):
                        if cnt >= size:
                            is_done = True
                            break
                        f_out.write(line)
                        cnt += 1

    logger.info('============================== [10.create_FLNL_corpus.py] done! ============================')


if __name__ == '__main__':
    main()
