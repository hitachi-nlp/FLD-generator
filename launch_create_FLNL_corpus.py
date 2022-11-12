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
from experimental_settings import get_dataset_setting, maybe_option

logger = logging.getLogger(__name__)


def _make_multiple_value_option(option: str, values: List[str]) -> str:
    return ' '.join([
        f'{option} {value}'
        for value in values
    ])


@click.command()
def main():
    setup_logger(level=logging.INFO)
    logger.info('============================== [launch_create_FLNL_corpus.py] start! ============================')

    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221007.add-axioms-theorems')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/debug')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221011.beat_ruletaker')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/debug')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221012.beat_ruletaker')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221026.enhance')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221027.enhance.fix')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221028.enhance.fix_translation')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221028.dist-var')
    # output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221101.various_datasets')
    output_top_dir = Path('./outputs/10.create_FLNL_corpus/20221107.more_distractive')

    dataset_names = [
        # '20221007.atmf-PA.arg-compl.dpth-3.add-axioms-theorems',
        # '20221007.atmf-PA.arg-compl.dpth-5.add-axioms-theorems',
        # '20221007.atmf-PA.arg-compl.dpth-10.add-axioms-theorems',
        # '20221007.atmf-PA.arg-compl.dpth-1-3.add-axioms-theorems',

        # '20221007.atmf-PA.arg-compl.dpth-3.add-axioms-theorems.limit_vocab',
        # '20221007.atmf-PA.arg-compl.dpth-5.add-axioms-theorems.limit_vocab',
        # # '20221007.atmf-PA.arg-compl.dpth-10.add-axioms-theorems.limit_vocab',
        # '20221007.atmf-PA.arg-compl.dpth-1-3.add-axioms-theorems.limit_vocab',

        # '20221011__dpth-S__bx-S__dist-neg__dist_size-S__size-S',
        # '20221011__dpth-M__bx-M__dist-neg__dist_size-S__size-S',
        # '20221011__dpth-S__bx-S__dist-neg__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-neg__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-neg__dist_size-M__size-M',

        # '20221011__dpth-S__bx-S__dist-unk__dist_size-S__size-S',
        # '20221011__dpth-M__bx-M__dist-unk__dist_size-S__size-S',
        # '20221011__dpth-S__bx-S__dist-unk__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-unk__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-unk__dist_size-M__size-M',

        # '20221011__dpth-S__bx-S__dist-mix__dist_size-S__size-S',
        # '20221011__dpth-M__bx-M__dist-mix__dist_size-S__size-S',
        # '20221011__dpth-S__bx-S__dist-mix__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-S',
        # '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-M',

        # '20221015__dpth-S__bx-S__dist-mix__dist_size-M__size-S.reuse_object_nouns',
        # '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-S.reuse_object_nouns',

        # '20221026__dpth-M__bx-M__dist-unk__dist_size-M__reuse-0.0__transl_weight-linear__size-S',
        # '20221026__dpth-M__bx-M__dist-unk__dist_size-M__reuse-0.0__transl_weight-sqrt__size-S',

        # '20221028__dpth-M__bx-M__dist-var__dist_size-S__reuse-0.0__transl_weight-linear__size-S',
        # '20221028__dpth-M__bx-M__dist-var__dist_size-M__reuse-0.0__transl_weight-linear__size-S',

        # '20221101__arg-basic__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-True__voc_limit-100__dataset_size-100000',
        # '20221101__arg-cmpl__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-True__voc_limit-100__dataset_size-100000',
        # '20221101__arg-cmpl__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-False__voc_limit-None__dataset_size-100000',
        # '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-0__reuse-0.0__fixed_transl-False__voc_limit-None__dataset_size-100000',
        # '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-10__reuse-1.0__fixed_transl-False__voc_limit-None__dataset_size-100000',
        # '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-10__reuse-1.0__fixed_transl-False__voc_limit-None__dataset_size-300000',

        # '20221107__arg-base__dpth-03__dist-00__transl-nrrw__size-100000',
        # '20221107__arg-cmpl__dpth-03__dist-00__transl-nrrw__size-100000',
        # '20221107__arg-cmpl__dpth-03__dist-00__transl-wide__size-100000',
        '20221107__arg-cmpl__dpth-03__dist-10__transl-wide__size-100000',
        '20221107__arg-cmpl__dpth-10__dist-10__transl-wide__size-100000',

        '20221112__arg-cmpl__dpth-3__dist-10__cllps--False__transl-wide__unk-0.33__size-100000',
        '20221112__arg-cmpl__dpth-3__dist-10__cllps--True__transl-wide__unk-0.33__size-100000',
        '20221112__arg-cmpl__dpth-3__dist-10__cllps--False__transl-wide__unk-0.60__size-100000',
    ]

    # engine = SubprocessEngine()
    engine = QsubEngine('ABCI', 'rt_C.small')

    # num_jobs = 1
    num_jobs = 180

    # num_workers_per_job = 1
    num_workers_per_job = 5

    timeout_per_job = 1800  # for the case some jobs hangs
    delete_logs_when_done = True
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
                'unknown_ratio',

                'argument_configs',

                'complication',
                'quantification',

                'depths',
                'branch_extension_steps',

                'distractor',
                # 'distractor_factor',
                'num_distractors',
                'sample_distractor_formulas_from_tree',
                'sample_hard_negative_distractors',
                'add_subj_obj_swapped_distractor',
                'use_collapsed_translation_nodes_for_unknown_tree'

                'translation_distractor',
                'num_translation_distractors',

                'split_sizes',

                'translation_configs',
                'limit_vocab_size_per_type',
                'translation_volume_to_weight',

                'num_workers_per_job',

                'world_assump',
            ],
            save_params=True
        )
        logger.addHandler(create_file_handler(output_dir / 'log.txt'))

        min_size_per_job = 100    # too small value might be slow.
        for split, size in settings['split_sizes'].items():
            size_with_margin = int(size * 1.1)   # for the case some jobs fail or hang

            split_output_dir = output_dir / split
            split_output_dir.mkdir(exist_ok=True, parents=True)

            if size_with_margin / num_jobs < min_size_per_job:
                _num_jobs = max(math.ceil(size_with_margin / min_size_per_job), 1)
            else:
                _num_jobs = num_jobs
            size_per_job = math.ceil(size_with_margin / _num_jobs)

            logger.info('============================== [launch_create_FLNL_corpus.py] Generating dataset for %s split ============================', split)
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
                    '--use-fixed-translation' if settings.get("use_fixed_translation", False) else '',
                    maybe_option('--reused-object-nouns-max-factor', settings.get("reused_object_nouns_max_factor", None)),
                    f'--limit-vocab-size-per-type {job_settings["limit_vocab_size_per_type"]}' if job_settings.get("limit_vocab_size_per_type", None) is not None else '',
                    maybe_option('--translation-volume-to-weight', settings.get("translation_volume_to_weight", None)),

                    f'--depths \'{json.dumps(job_settings["depths"])}\'',
                    f'--branch-extension-steps \'{json.dumps(job_settings["branch_extension_steps"])}\'',
                    f'--complication {job_settings["complication"]}',
                    f'--quantification {job_settings["quantification"]}',

                    f'--distractor {job_settings["distractor"]}',
                    f'--num-distractors \'{json.dumps(job_settings["num_distractors"])}\'',
                    '--sample-distractor-formulas-from-tree' if job_settings.get('sample_distractor_formulas_from_tree', False) else '',
                    '--sample-hard-negative-distractors' if job_settings.get('sample_hard_negative_distractors', False) else '',
                    '--add-subj-obj-swapped-distractor' if job_settings.get('add_subj_obj_swapped_distractor', False) else '',

                    f'--translation_distractor {job_settings["translation_distractor"]}',
                    f'--num-translation_distractors \'{json.dumps(job_settings["num_translation_distractors"])}\'',

                    f'--proof-stances \'{json.dumps(job_settings["proof_stances"])}\'',
                    f'--world-assump {job_settings["world_assump"]}',
                    maybe_option('--unknown-ratio', settings.get("unknown_ratio", None)),
                    '--use-collapsed-translation-nodes-for-unknown-tree' if job_settings.get('use_collapsed_translation_nodes_for_unknown_tree', False) else '',
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

                if delete_logs_when_done and i_job >= 5:
                    # remove large log files.
                    command += f'; rm {str(job_log_path)}; rm {str(job_output_dir)}/*.stats.json'

                jobs.append(
                    delayed(engine.run)(
                        command,
                        stdout=stdout,
                        stderr=stderr,
                        options={
                            'l_opts': ['h_rt=5:00:00'],
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
            job_output_jsonls = sorted([
                path for path in split_output_dir.glob(f'**/*{split}.jsonl')
                if str(path).find('job-') >= 0
            ])
            with open(split_output_dir / f'{split}.jsonl', 'w') as f_out:
                for jsonl in job_output_jsonls:
                    logger.info('gathering results from %s', str(jsonl))
                    if is_done:
                        break
                    for line in open(jsonl):
                        if cnt >= size:
                            is_done = True
                            break
                        f_out.write(line)
                        cnt += 1

    logger.info('============================== [launch_create_FLNL_corpus.py] done! ============================')


if __name__ == '__main__':
    main()
