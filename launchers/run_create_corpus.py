#!/usr/bin/env python
import json
import random
import math
import logging
from typing import List, Union, Dict
from pathlib import Path
import copy
from collections import defaultdict
import statistics

import click
from script_engine import QsubEngine, SubprocessEngine
from script_engine.base import EngineBase
from logger_setup import setup as setup_logger, create_file_handler
from lab import build_dir, save_params
from joblib import Parallel, delayed
from experimental_settings import get_dataset_setting, maybe_option

logger = logging.getLogger(__name__)


@click.command()
def main():
    setup_logger(level=logging.INFO)
    logger.info('============================== [run_create_corpus.py] start! ============================')

    # output_top_dir = Path('./outputs/00.create_corpus/20230729.case_study_finalize')
    # output_top_dir = Path('./outputs/00.create_corpus/20230729.case_study_finalize.debug')

    # output_top_dir = Path('./outputs/00.create_corpus/20230801.case_study_finalize.fix')

    # output_top_dir = Path('./outputs/00.create_corpus/20230826.jpn')

    # output_top_dir = Path('./outputs/00.create_corpus/20230901.random_transitive_verbs')

    # output_top_dir = Path('./outputs/00.create_corpus/20230904.jpn')
    # output_top_dir = Path('./outputs/00.create_corpus/20230912.jpn')
    # output_top_dir = Path('./outputs/00.create_corpus/20230914.jpn')
    # output_top_dir = Path('./outputs/00.create_corpus/20230916.jpn')

    # output_top_dir = Path('./outputs/00.create_corpus/20231010.large_vocab.small')
    # output_top_dir = Path('./outputs/00.create_corpus/20231010.large_vocab')
    # output_top_dir = Path('./outputs/00.create_corpus/20231012.large_vocab')

    # output_top_dir = Path('./outputs/00.create_corpus/20231018.knowledge')
    # output_top_dir = Path('./outputs/00.create_corpus/20231021.knowledge')
    output_top_dir = Path('./outputs/00.create_corpus/20231028.knowledge')

    dataset_names = [
        # ---------------------------------- 20230729.case_study_finalize (ICML-official-release-v2) ------------------------------------
        # '20230729.case_study_finalize.D3',
        # '20230729.case_study_finalize.D8',

        # ---------------------------------- 20230826.jpn ------------------------------------
        # '20230826.jpn.D3',
        # '20230826.jpn.D8',

        # ---------------------------------- 202320230901.random_transitive_verbs.D3 ------------------------------------
        # '20230901.random_transitive_verbs.D3',
        # '20230901.random_transitive_verbs.D8',

        # ---------------------------------- 20230904.jpn ------------------------------------
        # '20230904.jpn.D1.wo_brnch.wo_dstrct',
        # '20230904.jpn.D1.wo_brnch',
        # '20230904.jpn.D1',
        # '20230904.jpn.D3',

        # ---------------------------------- 20230912.jpn ------------------------------------
        # '20230912.jpn.D3',

        # ---------------------------------- 20230914.jpn ------------------------------------
        # '20230914.jpn.D3',


        # ---------------------------------- 20230916.jpn ------------------------------------
        # '20230916.jpn.D1_wo_dist',
        # '20230916.jpn.D1',
        # '20230916.jpn.D3',
        # '20230916.jpn.D5',

        # ---------------------------------- 20231010.D3.large_vocab ------------------------------------
        # '20231010.D3.large_vocab',

        # ---------------------------------- 20231012.D3.large_vocab ------------------------------------
        # '20231012.D3.large_vocab',
        # '20231012.D3.large_vocab.smpl_stncs',
        # '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3',
        # '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3.trnsl_vrnts-3',

        # ---------------------------------- 20231018.knowledge ------------------------------------
        # '20231018.knowledge.D3',
        # '20231018.knowledge.D3.w_knowledge',
        # '20231018.knowledge.D3.w_knowledge.complex-0.3',

        # ---------------------------------- 20231021.knowledge ------------------------------------
        # '20231021.knowledge.D3',
        # '20231021.knowledge.D3.complex-0.3',
        # '20231021.knowledge.D3.complex-0.3.w_knowledge',

        # ---------------------------------- 20231028.knowledge ------------------------------------
        '20231028.knowledge.D3',
    ]
    # dataset_names = dataset_names[::-1]

    num_jobs_for_datasets = 3
    num_jobs_per_dataset = 60

    # num_jobs_for_datasets = 2
    # num_jobs_per_dataset = 80

    # -- large value can save ABCI points because it avoids that the data loading becomes the bottleneck.
    min_dataset_size_per_job = 150
    # min_dataset_size_per_job = 100
    # min_dataset_size_per_job = 50
    # min_dataset_size_per_job = 10

    # engine = SubprocessEngine()
    engine = QsubEngine('ABCI', 'rt_C.small')

    # ---------------------------- fixed settings --------------------------
    timeout_per_job = 7200  # for the case some jobs hangs
    num_workers_per_job = 5
    delete_logs_when_done = False
    dry_run = False

    if num_jobs_for_datasets * num_jobs_per_dataset > 180:
        raise ValueError('Too much jobs %s ~ ABCI job limit = 200',
                         num_jobs_for_datasets * num_jobs_per_dataset)

    jobs = []
    for dataset_name in dataset_names:
        jobs.append(
            delayed(make_dataset)(
                dataset_name,
                output_top_dir,
                engine,
                timeout_per_job,
                delete_logs_when_done,
                num_jobs_per_dataset,
                num_workers_per_job,
                min_dataset_size_per_job,
                dry_run,
            )
        )

    Parallel(n_jobs=num_jobs_for_datasets, backend='threading')(jobs)

    logger.info('============================== [00.run_create_corpus.py] done! ============================')


def _make_multiple_value_option(option: str, values: List[str]) -> str:
    return ' '.join([
        f'{option} {value}'
        for value in values
    ])


def make_dataset(dataset_name: str,
                 output_top_dir: Union[str, Path],
                 engine: EngineBase,
                 timeout_per_job: int,
                 delete_logs_when_done: bool,
                 num_jobs: int,
                 num_workers_per_job: int,
                 min_dataset_size_per_job: int,
                 dry_run: bool) -> None:
    logger.info('====================== make_dataset() for "%s" =========================',
                dataset_name)
    output_top_dir = Path(output_top_dir)

    # ----------------- fixed ------------------
    settings = {
        'dataset_name': dataset_name,
        'num_workers_per_job': num_workers_per_job,
    }
    settings.update(get_dataset_setting(dataset_name))

    output_dir = build_dir(
        settings,
        top_dir=str(output_top_dir / f'dataset_name={dataset_name}'),
        short=True,
        dirname_ignore_params=[
            'dataset_name',
            'proof_stances',
            'unknown_ratio',

            'argument_configs',

            'complex_formula_arguments_weight',
            'quantifier_axiom_arguments_weight',
            'quantify_implication_premise_conclusion_at_once',
            'quantify_all_at_once',

            'depth_range',
            'depth_distrib',
            'translation_variants_per_logic',
            'branch_extensions_range',

            'distractor',
            # 'distractor_factor',
            'distractors_range',
            'sample_distractor_prototype_formulas_from_all_possible_formulas',
            'disallow_hard_negative_distractors',
            # 'negative_tree_negated_hypothesis_ratio',
            'disallow_subj_obj_swapped_distractor',
            'use_collapsed_translation_nodes_for_unknown_tree',
            'fallback_from_formula_to_translation_distractor',
            'swap_ng_words_config',

            'translation_distractor',
            'translation_distractors_range',
            'use_fixed_translation',

            'split_sizes',
            'split_wise_settings',

            'translation_lang',
            'translation_configs',
            'limit_vocab_size_per_type',
            'translation_volume_to_weight',
            'trnsltn_adj_vrb_nn_rt',

            'knowledge_injection_range',
            'knowledge_no_shuffle',
            'atomic_filepath',
            'concept_net_100k_filepath',

            'num_workers_per_job',

            'quantifier_axioms',

            'world_assump',
        ],
        save_params=True
    )
    logger.addHandler(create_file_handler(output_dir / 'log.txt'))

    for split, size in settings['split_sizes'].items():
        size_with_margin = int(size * 1.1)   # for the case some jobs fail or hang

        split_output_dir = output_dir / split
        split_output_dir.mkdir(exist_ok=True, parents=True)

        if size_with_margin / num_jobs < min_dataset_size_per_job:
            _num_jobs = max(math.ceil(size_with_margin / min_dataset_size_per_job), 1)
        else:
            _num_jobs = num_jobs
        size_per_job = math.ceil(size_with_margin / _num_jobs)

        logger.info('============================== [launch_create_FLD_corpus.py] Generating dataset for %s split ============================', split)
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
            job_settings.update(settings.get('split_wise_settings', {}).get(split, {}))
            job_settings['split'] = split
            job_settings['seed'] = i_job

            save_params(job_settings, job_output_dir)

            command = ' '.join([
                'python ./create_corpus.py',

                f'{job_output_path}',
                str(int(size_per_job)),

                f'--depth-range \'{json.dumps(job_settings["depth_range"])}\'',
                maybe_option('--depth-distrib', job_settings.get("depth_distrib", None)),
                f'--branch-extensions-range \'{json.dumps(job_settings["branch_extensions_range"])}\'',

                _make_multiple_value_option('--argument-config', job_settings['argument_configs']),
                f'--complex-formula-arguments-weight {job_settings["complex_formula_arguments_weight"]}',
                f'--quantifier-axiom-arguments-weight {job_settings["quantifier_axiom_arguments_weight"]}',
                _make_multiple_value_option('--quantifier-axiom', job_settings['quantifier_axioms']),
                maybe_option('--quantification-degree', job_settings.get('quantification_degree', None)),

                maybe_option('--translation-lang', job_settings.get('translation_lang', None)),
                _make_multiple_value_option('--translation-config', job_settings['translation_configs']),
                '--use-fixed-translation' if job_settings.get("use_fixed_translation", False) else '',
                maybe_option('--reused-object-nouns-max-factor', job_settings.get("reused_object_nouns_max_factor", None)),
                f'--limit-vocab-size-per-type {job_settings["limit_vocab_size_per_type"]}' if job_settings.get("limit_vocab_size_per_type", None) is not None else '',
                maybe_option('--translation-volume-to-weight', job_settings.get("translation_volume_to_weight", None)),
                maybe_option('--translation-adj-verb-noun-ratio', job_settings.get("translation_adj_verb_noun_ratio", None)),


                f'--distractor "{job_settings["distractor"]}"',
                f'--distractors-range \'{json.dumps(job_settings["distractors_range"])}\'',
                # maybe_option('--negative-tree-negated-hypothesis-ratio', job_settings.get('negative_tree_negated_hypothesis_ratio', None)),
                '--sample-distractor-prototype-formulas-from-all-possible-formulas' if job_settings.get('sample_distractor_prototype_formulas_from_all_possible_formulas', False) else '',
                '--disallow-simplified-tree-formulas-as-distractor-prototype' if job_settings.get('disallow_simplified_tree_formulas_as_distractor_prototype', False) else '',
                '--disallow-subj-obj-swapped-distractor' if job_settings.get('disallow_subj_obj_swapped_distractor', False) else '',
                maybe_option('--swap-ng-words-config', job_settings.get("swap_ng_words_config", None)),
                maybe_option('--translation-distractor', job_settings.get("translation_distractor", None)),
                f'--translation-distractors-range \'{json.dumps(job_settings["translation_distractors_range"])}\'',
                '--fallback-from-formula-to-translation-distractor' if job_settings.get('fallback_from_formula_to_translation_distractor', False) else '',

                f'--knowledge-injection-range \'{json.dumps(job_settings["knowledge_injection_range"])}\'' if job_settings.get('knowledge_injection_range', None) is not None else '',
                '--knowledge-no-shuffle' if job_settings.get('knowledge_no_shuffle', False) else '',
                maybe_option('--atomic-filepath', job_settings.get("atomic_filepath", None)),
                maybe_option('--concept-net-100k-filepath', job_settings.get("concept_net_100k_filepath", None)),

                f'--proof-stances \'{json.dumps(job_settings["proof_stances"])}\'' if "proof_stances" in job_settings else '',
                f'--world-assump {job_settings["world_assump"]}' if "world_assump" in job_settings else '',
                maybe_option('--unknown-ratio', job_settings.get("unknown_ratio", None)),
                '--sample-all-stances-per-logic' if job_settings.get('sample_all_stances_per_logic', False) else '',
                maybe_option('--context-shuffles-per-instance', job_settings.get("context_shuffles_per_instance", None)),
                '--use-collapsed-translation-nodes-for-unknown-tree' if job_settings.get('use_collapsed_translation_nodes_for_unknown_tree', False) else '',

                maybe_option('--translation-variants-per-logic', job_settings.get("translation_variants_per_logic", None)),

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

            job_hours = math.floor(timeout_per_job / 3600)
            jobs.append(
                delayed(engine.run)(
                    command,
                    stdout=stdout,
                    stderr=stderr,
                    options={
                        'l_opts': [f'h_rt={job_hours}:00:00'],
                        'timeout_from_run': timeout_per_job,
                    },
                    dry_run=dry_run,
                    wait_until_finish=True,
                )
            )

        logger.info('waiting %d jobs to be finished...', len(jobs))
        Parallel(n_jobs=_num_jobs, backend='threading')(jobs)

        # -- aggregate results --
        logger.info('gathering results under %s', split_output_dir)
        cnt = 0
        is_done = False
        job_output_jsonls = sorted([
            path for path in split_output_dir.glob(f'**/*{split}.jsonl')
            if str(path).find('job-') >= 0
        ])
        lines: List[str] = []
        for jsonl in job_output_jsonls:
            if is_done:
                break
            for line in open(jsonl):
                if cnt >= size:
                    is_done = True
                    break
                lines.append(line)
                cnt += 1
        random.shuffle(lines)
        with open(split_output_dir / f'{split}.jsonl', 'w') as f_out:
            for line in lines:
                f_out.write(line)

        # -- aggregate statistics --
        logger.info('gathering stats under %s', split_output_dir)
        job_stats_jsonls = sorted([
            path for path in split_output_dir.glob(f'**/*{split}.jsonl.stats.json')
            if str(path).find('job-') >= 0
        ])
        agg_stats: Dict[str, Union[int, List[int]]] = {}
        for stats_path in job_stats_jsonls:
            stats = json.load(open(stats_path))
            for name, cnt in stats.items():
                if name.startswith('cum'):
                    if name in agg_stats:
                        agg_stats[name] += cnt
                    else:
                        agg_stats[name]  = cnt
                elif name.startswith('avg'):
                    if name in agg_stats:
                        agg_stats[name].append(cnt)
                    else:
                        agg_stats[name]  = [cnt]
                elif name.startswith('std'):
                    # TODO: implement
                    pass
        for name, cnt in sorted(agg_stats.items()):
            if name.startswith('avg'):
                agg_stats[name] = statistics.mean(cnt)
        json.dump(dict(agg_stats), open(str(split_output_dir / f'{split}.jsonl.stats.json'), 'w'),
                  ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))



if __name__ == '__main__':
    main()
