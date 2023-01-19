#!/usr/bin/env python
import logging
from pathlib import Path
import shutil

from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def main():
    setup_logger(level=logging.INFO)

    OUTPUT_DIR = './outputs/E00.prepare_dataset_release.py/20220119.release_for_NLP/'

    datasets = [
        ('sFLD-impl', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT.G_MP'),
        ('sFLD-crit', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-AA__frml-cmpl__dist-20__transl-nrrw__tree-1__dataset_size-30000'),
        ('sFLD-axiom', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT'),

        ('FLD.D5', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000'),
        ('FLD-impl', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP'),
        ('FLD', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000'),
        ('FLD-star', './outputs/10.create_FLNL_corpus/20221203.first_exp/dataset_name=20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000'),
    ]

    for dataset_name, top_dir in datasets:
        top_dir = Path(top_dir)
        output_dir = Path(OUTPUT_DIR) / dataset_name
        output_dir.mkdir(exist_ok=True, parents=True)

        for split in ['train', 'valid', 'test']:
            if split == 'valid':
                # placeholder until we create validation splits
                pseudo_split = 'test'
            else:
                pseudo_split = split
            split_paths = [path for path in top_dir.glob(f'**/*/{pseudo_split}.jsonl')
                           if str(path).find('job-') < 0]
            if len(split_paths) == 0:
                logger.warning('split "%s" for dataset "%s" not found under "%s"',
                               split,
                               dataset_name,
                               str(top_dir))
                continue
            elif len(split_paths) >= 2:
                raise ValueError()

            split_path = str(split_paths[0])
            logger.info('copying %s into %s', split_path, str(output_dir))
            shutil.copy(split_paths[0], str(output_dir / f'{split}.jsonl'))



if __name__ == '__main__':
    main()
