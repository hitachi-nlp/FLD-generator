#!/usr/bin/env python
import math
import random
import json
from typing import List, Dict
from pathlib import Path
from pprint import pformat
import logging
from collections import defaultdict

import click
from tqdm import tqdm
import dill

from formal_logic.translators import ClauseTypedTranslator
from formal_logic.word_banks import EnglishWordBank
from formal_logic.distractors import SameFormUnkownInterprandsDistractor, FormalLogicDistractor
from formal_logic.argument import Argument
from formal_logic.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from formal_logic.proof_tree_generators import ProofTreeGenerator
from formal_logic.datasets import NLProofSDataset
from formal_logic.proof import ProofTree
from joblib import Parallel, delayed

from logger_setup import setup as setup_logger


logger = logging.getLogger(__name__)


def load_arguments(config_paths: List[str]) -> List[Argument]:
    arguments = []
    for config_path in config_paths:
        arguments.extend([Argument.from_json(json_obj)
                          for json_obj in json.load(open(config_path))
                          if not json_obj['id'].startswith('__')])
    return arguments


def load_dataset(argument_config: str,
                 translation_config: str,
                 complication: float,
                 quantification: float,
                 keep_dneg: bool,
                 distractor_factor: float,
                 world_assump: str,
                 depth: int,
                 max_leaf_extensions: int):
    arguments = load_arguments(argument_config)
    generator = ProofTreeGenerator(
        arguments,
        elim_dneg=not keep_dneg,
        complicated_arguments_weight=complication,
        quantified_arguments_weight=quantification,
    )

    distractor = SameFormUnkownInterprandsDistractor(distractor_factor)

    translator = ClauseTypedTranslator(
        {key: value
         for config_path in translation_config
         for key, value in json.load(open(config_path)).items()},
        EnglishWordBank(),
        do_translate_to_nl=True,
    )

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    return NLProofSDataset(pipeline, world_assump, depth, max_leaf_extensions)


def generate_instances(size: int, *args):
    # logger = logging.getLogger(__name__)
    logger.info('[pass or not checking for finding the cause of hangups] 00')  # HONOKA: we pass here

    dataset = load_dataset(*args)  # HONOKA: we pass here
    logger.info('[pass or not checking for finding the cause of hangups] 01')

    data = []
    _final_stats = None
    for nlproof_json, proof_tree, distractors, stats in tqdm(dataset.generate(size)):  # HONOKA: we can't pass here
        data.append((nlproof_json, proof_tree, distractors))
        _final_stats = stats
        log(logger, nlproof_json, proof_tree, distractors)
    logger.info('[pass or not checking for finding the cause of hangups] 02')
    return data, _final_stats


def log(logger, nlproof_json: Dict, proof_tree: ProofTree, distractors: List[str]):
    logger.info('\n')
    logger.info('--------------- tree --------------')

    logger.info('\n')
    logger.info('\n' + proof_tree.format_str)

    logger.info('\n')
    logger.info('--------------- distractors --------------')
    logger.info('\n' + pformat(distractors))

    logger.info('\n')
    logger.info('--------------- NLProofs json --------------')
    logger.info('\n' + pformat(nlproof_json))

    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')


@click.command()
@click.argument('output-path')
@click.argument('size', type=int)
@click.option('--argument-config', '--ac',
              multiple=True, default=[])
@click.option('--translation-config', '--tc',
              multiple=True,
              default=['./configs/formal_logic/translations/clause_typed.thing.json'])
@click.option('--depth', type=int, default=5)
@click.option('--max-leaf-extensions', type=int, default=5)
@click.option('--complication', type=float, default=0.0)
@click.option('--quantification', type=float, default=0.0)
@click.option('--keep-dneg', is_flag=True, default=False)
@click.option('--distractor-factor', type=float, default=1.0)
@click.option('--world-assump', default='CWA')
@click.option('--num-workers', type=int, default=1)
@click.option('--batch-size-per-worker', type=int, default=300)
@click.option('--seed', type=int, default=0)
def main(output_path,
         argument_config,
         translation_config,
         size,
         depth,
         max_leaf_extensions,
         complication,
         quantification,
         keep_dneg,
         distractor_factor,
         world_assump,
         num_workers,
         batch_size_per_worker,
         seed):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(seed)

    if len(argument_config) == 0:
        raise ValueError()

    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    size_per_worker = math.ceil(size / num_workers)
    _batch_size_per_worker = min(batch_size_per_worker, size_per_worker)
    num_batches = math.ceil(size_per_worker / _batch_size_per_worker)

    logger.info('num_workers: %d', num_workers)
    logger.info('size_per_worker: %d', size_per_worker)
    logger.info('batch_size_per_worker: %d', _batch_size_per_worker)
    logger.info('num_batches: %d', num_batches)

    with open(output_path, 'w') as f_out:

        gathered_stats = defaultdict(int)
        for i_batch in range(num_batches):
            jobs = []
            for _ in range(num_workers):
                jobs.append(
                    delayed(generate_instances)(
                        _batch_size_per_worker,
                        argument_config,
                        translation_config,
                        complication,
                        quantification,
                        keep_dneg,
                        distractor_factor,
                        world_assump,
                        depth,
                        max_leaf_extensions,
                    )
                )

            logger.info('[pass or not checking for finding the cause of hangups] 0')  # HONOKA: we pass here
            instances_list = Parallel(n_jobs=num_workers, backend='multiprocessing')(jobs)
            logger.info('[pass or not checking for finding the cause of hangups] 1')  # HONOKA: we can't pass here

            cnt = 0
            is_done = False
            for instances, stats in instances_list:
                if is_done:
                    break

                for nlproof_json, proof_tree, distractors in instances:
                    if cnt >= size:
                        is_done = True
                        break
                    f_out.write(json.dumps(nlproof_json) + '\n')
                    cnt += 1
                for name, count in stats.items():
                    gathered_stats[name] += count
            logger.info('[pass or not checking for finding the cause of hangups] 2')  # HONOKA: we can't pass here

            logger.info('=========================== gathered stats (batch=%d) ============================',
                        i_batch)
            logger.info('\n' + pformat(gathered_stats))



if __name__ == '__main__':
    main()
