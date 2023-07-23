#!/usr/bin/env python
import json
import math
import logging
from typing import List, Union
from pathlib import Path
import copy

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

    # output_top_dir = Path('./outputs/00.create_corpus/20221203.first_exp')
    # output_top_dir = Path('./outputs/00.create_corpus/20221217.back_to_the_past')

    # output_top_dir = Path('./outputs/00.create_corpus/20230529.use_fixed_translation_for_LLM')
    # output_top_dir = Path('./outputs/00.create_corpus/20230601.fix_translation')
    # output_top_dir = Path('./outputs/00.create_corpus/20230615.formula_checkers')
    # output_top_dir = Path('./outputs/00.create_corpus/20230616.formula_checkers')
    # output_top_dir = Path('./outputs/00.create_corpus/20230621.formula_checkers')

    # output_top_dir = Path('./outputs/00.create_corpus/20230626.many_bugs_fixed')
    # output_top_dir = Path('./outputs/00.create_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure')
    # output_top_dir = Path('./outputs/00.create_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure.v1')
    # output_top_dir = Path('./outputs/00.create_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure.v2')

    # output_top_dir = Path('./outputs/00.create_corpus/20230628.make_harder')
    # output_top_dir = Path('./outputs/00.create_corpus/20230629.degug')

    # output_top_dir = Path('./outputs/00.create_corpus/20230701.finalize')

    # output_top_dir = Path('./outputs/00.create_corpus/20230703.refactor_test')
    # output_top_dir = Path('./outputs/00.create_corpus/20230703.refactor_test.2')
    # output_top_dir = Path('./outputs/00.create_corpus/20230703.refactor_test.3.large')
    # output_top_dir = Path('./outputs/00.create_corpus/20230704.speedup.1')
    # output_top_dir = Path('./outputs/00.create_corpus/20230704.speedup.2')
    # output_top_dir = Path('./outputs/00.create_corpus/20230704.refactor_test')

    # output_top_dir = Path('./outputs/00.create_corpus/20230705.dist-tree')
    # output_top_dir = Path('./outputs/00.create_corpus/20230705.dist-tree.1_parallel')
    # output_top_dir = Path('./outputs/00.create_corpus/20230705.log')
    # output_top_dir = Path('./outputs/00.create_corpus/20230705.min_size_per_worker=20')
    # output_top_dir = Path('./outputs/00.create_corpus/20230705.min_size_per_worker=20')

    # output_top_dir = Path('./outputs/00.create_corpus/20230706.finalize')
    # output_top_dir = Path('./outputs/00.create_corpus/20230706.finalize.wo_cache')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.wo_cache')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large.all')

    # output_top_dir = Path('./outputs/00.create_corpus/20230707.wo_cache.wo_timeout')  # OK
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.wo_cache.w_timeout')   # OK
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.wo_timeout')   # NG
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout')    # NG

    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.raise_test')  # OK
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.first_use_no_cache')  # not good
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.second_use_no_cache')   # OK
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.yield_return')
    # output_top_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.yield_from')

    # output_top_dir = Path('./outputs/00.create_corpus/20230707.finalize')
    # output_top_dir = Path('./outputs/00.create_corpus/20230710.update_translation')
    # output_top_dir = Path('./outputs/00.create_corpus/20230710.update_translation.bf51eb2')
    # output_top_dir = Path('./outputs/00.create_corpus/20230710.update_translation.7485fef')

    # output_top_dir = Path('./outputs/00.create_corpus/20230711.refactor_distractors')
    # output_top_dir = Path('./outputs/00.create_corpus/20230711.finalize')
    # output_top_dir = Path('./outputs/00.create_corpus/20230711.ICML-official-release-v2')

    # output_top_dir = Path('./outputs/00.create_corpus/20230718.case_study')
    # output_top_dir = Path('./outputs/00.create_corpus/20230718.case_study.strip_double_brace')
    # output_top_dir = Path('./outputs/00.create_corpus/20230718.debug')

    # output_top_dir = Path('./outputs/00.create_corpus/20230718.symmetric_translation')
    # output_top_dir = Path('./outputs/00.create_corpus/20230718.symmetric_translation.debug.1')
    # output_top_dir = Path('./outputs/00.create_corpus/20230718.symmetric_translation.debug.weight-0.01')
    # output_top_dir = Path('./outputs/00.create_corpus/20230718.symmetric_translation.debug.weight_type_avg')
    output_top_dir = Path('./outputs/00.create_corpus/20230718.symmetric_translation.debug.weight_type_avg.0.05')

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
        # '20221107__arg-cmpl__dpth-03__dist-10__transl-wide__size-100000',
        # '20221107__arg-cmpl__dpth-10__dist-10__transl-wide__size-100000',


        # '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--0__transl-wide__unk-0.33__size-100000',
        # '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--10__transl-wide__unk-0.33__size-100000',
        # '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--0__transl-wide__unk-0.65__size-100000',
        # '20221112__arg-cmpl__dpth-3__dist-5__transl_dist--0__transl-wide__unk-0.33__size-100000',


        # '20221115__arg-RT__frml-smpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000',
        # '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000',
        # '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--10__transl-nrrw__size-100000',
        # '20221115__arg-RT__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000',  # ~ RuleTaker
        # '20221115__arg-all__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000',
        # '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-nrrw__size-100000',
        # '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-wide__size-100000',


        # '20221117__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--20__transl-wide__size-100000',
        # '20221117__arg-RT__frml-cmpl__tree-tiny__dist-0__transl_dist--20__transl-wide__size-100000',

        # '20221120.negative_tree__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-100000',

        # '20221123.and__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000',

        # '20221124.and__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000',

        # '20221125.full__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000',
        # '20221126.transl__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-30000',

        # '20221130.transl__arg-AA__frml-smpl__tree-1__dist-5__transl_dist--5__transl-wide__size-30000',



        # '20221203.first_exp__arg-RT__frml-smpl__dist-0__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-RT__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-AA__frml-cmpl__dist-20__transl-nrrw__tree-1__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000',

        # ---------------------------------- 20221215 additional experiments ------------------------------------
        # '20221203.first_exp__arg-RT__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000',

        # ---------------------------------- 20221216 additional experiments ------------------------------------
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000',

        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP',
        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-8__dataset_size-30000.G_MP',

        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT.G_MP',
        # '20221203.first_exp__arg-FLD__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT',

        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.G_MP',

        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000.G_MP',
        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000.G_MP',

        # ---------------------------------- 20221217.back_to_the_past ------------------------------------
        # '20221217.back_to_the_past__arg-FLD__frml-cmpl__dist-10__transl-wide__tree-10__dataset_size-100000',

        # ---------------------------------- 20230529.use_fixed_translation_for_LLM ------------------------------------
        # '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT.G_MP',
        # '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000',
        # '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000',

        # ---------------------------------- 20230615.formula_checkers ------------------------------------
        # '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000',
        # '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems',

        # ---------------------------------- 20230616.formula_checkers ------------------------------------
        # '20230616.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems',

        # ---------------------------------- 20230621.formula_checkers ------------------------------------
        # '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems',
        # '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems.wo_translation_dist',

        # ---------------------------------- 20230626.many_bugs_fixed ------------------------------------
        # '20230626.many_bugs_fixed.20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP',
        # '20230626.many_bugs_fixed.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.plus_quantifiers',

        # ---------------------------------- 20230628.make_harder ------------------------------------
        # '20230626.many_bugs_fixed.D3.hard',
        # '20230626.many_bugs_fixed.D3.hard.dist-trees',
        # '20230626.many_bugs_fixed.D3.hard.unk-0.1',
        # '20230626.many_bugs_fixed.D3.hard.brnch-high',
        # '20230626.many_bugs_fixed.D3.hard.dist-neg-1.0',
        # '20230626.many_bugs_fixed.D3.hard.dist-neg-0.5',
        # '20230626.many_bugs_fixed.D3.hard.dist-neg-0.0',
        # '20230626.many_bugs_fixed.D3.hard.dist-trees-only',

        # '20230626.many_bugs_fixed.D8.hard',
        # '20230626.many_bugs_fixed.D8.hard.dist-trees',

        # ---------------------------------- 20230701.finalize ------------------------------------
        # '20230701.D3.default',
        # '20230701.D3.wo_transl_dist',
        # '20230701.D3.brnch-small',
        # '20230701.D3.dist-small',
        # '20230701.D3.default.refactor_test',
        # '20230701.D3.default.dist-tree-triple',
        # '20230701.D3.default.dist-tree-quadruple',

        # '20230701.D8.default',

        # ---------------------------------- 20230706..finalize ------------------------------------
        # '20230706.finalize.D3.dist-double',
        # '20230706.finalize.D3.dist-quadruple',
        # # '20230706.finalize.D8.dist-double',
        # '20230706.finalize.D8.dist-quadruple',

        # ---------------------------------- 20230707.finalize ------------------------------------
        # '20230707.finalize.D3.dist-double',
        # '20230707.finalize.D3.dist-triple',
        # '20230707.finalize.D3.dist-quadruple',

        # '20230707.finalize.D8.dist-double',
        # '20230707.finalize.D8.dist-triple',
        # '20230707.finalize.D8.dist-quadruple',

        # ---------------------------------- 20230711.finalize ------------------------------------
        # '20230711.dist-fallback',
        # '20230711.finalize.D3',
        # '20230711.finalize.D8',

        # ---------------------------------- 20230718.case_study ------------------------------------
        # '20230718.case_study.D3.dist-mixture',
        # '20230718.case_study.D3.num_dist-wide',
        '20230718.case_study.D3.dist-mixture.num_dist-wide',
        # '20230718.case_study.D8.dist-mixture.num_dist-wide',

    ]
    # dataset_names = dataset_names[::-1]

    num_jobs_for_datasets = 2
    num_jobs_per_dataset = 80

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
    timeout_per_job = 4800  # for the case some jobs hangs
    num_workers_per_job = 5
    delete_logs_when_done = True
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
        dirname_exclude_params=[
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

            'translation_configs',
            'limit_vocab_size_per_type',
            'translation_volume_to_weight',

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
            job_settings['split'] = split
            job_settings['seed'] = i_job

            save_params(job_settings, job_output_dir)

            command = ' '.join([
                'python ./create_corpus.py',

                f'{job_output_path}',
                str(int(size_per_job)),

                f'--depth-range \'{json.dumps(job_settings["depth_range"])}\'',
                maybe_option('--depth-distrib', settings.get("depth_distrib", None)),
                f'--branch-extensions-range \'{json.dumps(job_settings["branch_extensions_range"])}\'',

                _make_multiple_value_option('--argument-config', job_settings['argument_configs']),
                f'--complex-formula-arguments-weight {job_settings["complex_formula_arguments_weight"]}',
                f'--quantifier-axiom-arguments-weight {job_settings["quantifier_axiom_arguments_weight"]}',
                _make_multiple_value_option('--quantifier-axiom', job_settings['quantifier_axioms']),
                maybe_option('--quantification-degree', job_settings.get('quantification_degree', None)),

                _make_multiple_value_option('--translation-config', job_settings['translation_configs']),
                '--use-fixed-translation' if settings.get("use_fixed_translation", False) else '',
                maybe_option('--reused-object-nouns-max-factor', settings.get("reused_object_nouns_max_factor", None)),
                f'--limit-vocab-size-per-type {job_settings["limit_vocab_size_per_type"]}' if job_settings.get("limit_vocab_size_per_type", None) is not None else '',
                maybe_option('--translation-volume-to-weight', settings.get("translation_volume_to_weight", None)),


                f'--distractor "{job_settings["distractor"]}"',
                f'--distractors-range \'{json.dumps(job_settings["distractors_range"])}\'',
                # maybe_option('--negative-tree-negated-hypothesis-ratio', job_settings.get('negative_tree_negated_hypothesis_ratio', None)),
                '--sample-distractor-prototype-formulas-from-all-possible-formulas' if job_settings.get('sample_distractor_prototype_formulas_from_all_possible_formulas', False) else '',
                '--disallow-simplified-tree-formulas-as-distractor-prototype' if job_settings.get('disallow_simplified_tree_formulas_as_distractor_prototype', False) else '',
                '--disallow-subj-obj-swapped-distractor' if job_settings.get('disallow_subj_obj_swapped_distractor', False) else '',
                maybe_option('--swap-ng-words-config', settings.get("swap_ng_words_config", None)),
                maybe_option('--translation-distractor', settings.get("translation_distractor", None)),
                f'--translation-distractors-range \'{json.dumps(job_settings["translation_distractors_range"])}\'',
                '--fallback-from-formula-to-translation-distractor' if job_settings.get('fallback_from_formula_to_translation_distractor', False) else '',

                f'--proof-stances \'{json.dumps(job_settings["proof_stances"])}\'' if "proof_stances" in job_settings else '',
                f'--world-assump {job_settings["world_assump"]}' if "world_assump" in job_settings else '',
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
                # logger.info('gathering results from %s', str(jsonl))
                if is_done:
                    break
                for line in open(jsonl):
                    if cnt >= size:
                        is_done = True
                        break
                    f_out.write(line)
                    cnt += 1




if __name__ == '__main__':
    main()
