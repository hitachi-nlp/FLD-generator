#!/usr/bin/env python
import logging
import re
from pathlib import Path
import shutil
import json
from script_engine import QsubEngine, SubprocessEngine

from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def compute_distrib(input_dir: Path, output_dir: Path) -> None:
    engine = SubprocessEngine()
    for input_path in input_dir.glob('**/*.jsonl'):
        # if str(input_path).find('job-') >= 0 or not str(input_path).find('train') >= 0:
        if str(input_path).find('job-') >= 0:
            continue
        lab_prams_path = input_path.parent.parent / 'lab.params.json'
        dataset_name = json.load(open(lab_prams_path))['dataset_name']
        split = re.sub(r'\.jsonl$', '', input_path.name)
        output_path = output_dir / f'dataset_name={dataset_name}.{split}.distrib.txt'
        engine.run(
            f'python ./compute_distrib.py {str(input_path)} {str(output_path)}',
            wait_until_finish=True,
        )


def main():
    setup_logger(level=logging.INFO)

    # input_dir = Path('./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed/')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230626.many_bugs_fixed/')

    # input_dir = Path('./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230626.many_bugs_fixed.suppress_tree_generation_failure/')

    # input_dir = Path('./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure.v1')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230626.many_bugs_fixed.suppress_tree_generation_failure.v1')

    # input_dir = Path('./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure.v2')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230626.many_bugs_fixed.suppress_tree_generation_failure.v2')

    # input_dir = Path('./outputs/00.create_corpus/20230701.finalize')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230701.finalize')

    # input_dir = Path('./outputs/00.create_corpus/20230703.refactor_test')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230703.refactor_test')

    # input_dir = Path('./outputs/00.create_corpus/20230703.refactor_test.2')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230703.refactor_test.2')

    # input_dir = Path('./outputs/00.create_corpus/20230703.refactor_test.3.large')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230703.refactor_test.3.large')

    # input_dir = Path('./outputs/00.create_corpus/20230704.speedup.1')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230704.speedup.1')

    # input_dir = Path('./outputs/00.create_corpus/20230704.speedup.2')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230704.speedup.2')

    # input_dir = Path('./outputs/00.create_corpus/20230705.dist-tree')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230705.dist-tree')

    # input_dir = Path('./outputs/00.create_corpus/20230706.finalize')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230706.finalize')

    # OK!
    # input_dir = Path('./outputs/00.create_corpus/20230707.476ad61')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.476ad61')

    # NG!
    # input_dir = Path('./outputs/00.create_corpus/20230707.33d4ddb')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.33d4ddb')

    # input_dir = Path('./outputs/00.create_corpus/20230707.d02e0eb')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.d02e0eb')

    # input_dir = Path('./outputs/00.create_corpus/20230707.ccc02a8')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.ccc02a8')

    # input_dir = Path('./outputs/00.create_corpus/20230707.33bf5a7')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.33bf5a7')

    # input_dir = Path('./outputs/00.create_corpus/20230707.f6e8db7')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.f6e8db7')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.wo_cache')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.wo_cache')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.w_cache')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.w_cache.w_timeout')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.w_cache.w_timeout.latest')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large')

    # input_dir = Path('./outputs/00.create_corpus/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large.all')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.honoka-dev.w_cache.w_timeout.latest.extend_branches_timeout_large.all')



    # input_dir = Path('./outputs/00.create_corpus/20230707.wo_cache.wo_timeout')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.wo_cache.wo_timeout')

    # input_dir = Path('./outputs/00.create_corpus/20230707.wo_cache.w_timeout')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.wo_cache.w_timeout')

    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.wo_timeout')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.wo_timeout')

    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.w_timeout')



    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.raise_test')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.w_timeout.raise_test')

    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.first_use_no_cache')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.w_timeout.first_use_no_cache')

    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.second_use_no_cache')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.w_timeout.second_use_no_cache')

    # input_dir = Path('./outputs/00.create_corpus/20230707.w_cache.w_timeout.yield_from')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.w_cache.w_timeout.yield_from')

    # input_dir = Path('./outputs/00.create_corpus/20230707.finalize')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230707.finalize')

    # input_dir = Path('./outputs/00.create_corpus/20230711.refactor_distractors')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230711.refactor_distractors')

    # input_dir = Path('./outputs/00.create_corpus/20230711.refactor_distractors')
    # output_dir = Path('./outputs/G00.compute_distrib.py/20230711.refactor_distractors')

    input_dir = Path('./outputs/00.create_corpus/2023-07-27.compare_models')
    output_dir = Path('./outputs/G00.compute_distrib.py/2023-07-27.compare_models')

    compute_distrib(input_dir, output_dir)


if __name__ == '__main__':
    main()
