#!/usr/bin/env python
import logging
import re
from pathlib import Path
import json
from script_engine import QsubEngine, SubprocessEngine

from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def compute_distrib(input_dir: Path, output_dir: Path) -> None:
    engine = SubprocessEngine()
    for input_path in input_dir.glob('**/*.jsonl'):
        if str(input_path).find('job-') >= 0:
            continue
        lab_prams_path = input_path.parent.parent / 'lab.params.json'
        dataset_name = json.load(open(lab_prams_path))['dataset_name']
        split = re.sub(r'\.jsonl$', '', input_path.name)
        output_path = output_dir / f'dataset_name={dataset_name}.{split}.results.txt'
        engine.run(
            f'python ./show_labelwise_results.py {str(input_path)} {str(output_path)}',
            wait_until_finish=True,
        )


def main():
    setup_logger(level=logging.INFO)

    # input_dir = Path('./outputs/00.create_corpus/20230711.refactor_distractors')
    # output_dir = Path('./outputs/G01.show_labelwise_results.py/20230711.refactor_distractors')

    input_dir = Path('./outputs/00.create_corpus/20230718.case_study')
    output_dir = Path('./outputs/G01.show_labelwise_results.py/20230718.case_study')

    compute_distrib(input_dir, output_dir)


if __name__ == '__main__':
    main()
