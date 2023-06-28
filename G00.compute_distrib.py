#!/usr/bin/env python
import logging
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
        split = input_path.name.rstrip('.jsonl')
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

    input_dir = Path('./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed.suppress_tree_generation_failure.v1')
    output_dir = Path('./outputs/G00.compute_distrib.py/20230626.many_bugs_fixed.suppress_tree_generation_failure.v1')

    compute_distrib(input_dir, output_dir)


if __name__ == '__main__':
    main()
