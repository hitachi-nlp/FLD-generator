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

from FLNL.translators import ClauseTypedTranslator
from FLNL.word_banks import EnglishWordBank
from FLNL.distractors import SameFormUnkownInterprandsDistractor, FormalLogicDistractor
from FLNL.argument import Argument
from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.proof_tree_generators import ProofTreeGenerator
from FLNL.datasets import NLProofSDataset
from FLNL.proof import ProofTree
from FLNL.utils import nested_merge
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
                 proof_stances: List[str],
                 world_assump: str,
                 depth: int,
                 branch_extension_steps: int):
    arguments = load_arguments(argument_config)
    generator = ProofTreeGenerator(
        arguments,
        elim_dneg=not keep_dneg,
        complicated_arguments_weight=complication,
        quantified_arguments_weight=quantification,
    )

    distractor = SameFormUnkownInterprandsDistractor(distractor_factor)

    merged_config_json = {}
    for config_path in translation_config:
        merged_config_json = nested_merge(merged_config_json,
                                          json.load(open(config_path)))
    translator = ClauseTypedTranslator(
        merged_config_json,
        EnglishWordBank(),
        do_translate_to_nl=True,
    )

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    return NLProofSDataset(pipeline, proof_stances, world_assump, depth, branch_extension_steps)


def generate_instances(size: int, *args):
    # logger = logging.getLogger(__name__)
    logger.debug('[pass or not checking for finding the cause of hangups] 00')  # HONOKA: we pass here

    dataset = load_dataset(*args)  # HONOKA: we pass here
    logger.debug('[pass or not checking for finding the cause of hangups] 01')

    data = []
    _final_stats = None
    for nlproof_json, proof_tree, distractors, stats in tqdm(dataset.generate(size)):  # HONOKA: we can't pass here
        data.append((nlproof_json, proof_tree, distractors))
        _final_stats = stats
        log(logger, nlproof_json, proof_tree, distractors)
    logger.debug('[pass or not checking for finding the cause of hangups] 02')
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
              default=['./configs/FLNL/translations/clause_typed.thing.json'])
@click.option('--depth', type=int, default=5)
@click.option('--max-leaf-extensions', type=int, default=5)
@click.option('--complication', type=float, default=0.0)
@click.option('--quantification', type=float, default=0.0)
@click.option('--keep-dneg', is_flag=True, default=False)
@click.option('--distractor-factor', type=float, default=1.0)
@click.option('--proof-stances', type=str, default=json.dumps(['PROOF', 'DISPROOF', 'UNKNOWN']))
@click.option('--world-assump', default='CWA')
@click.option('--num-workers', type=int, default=1)
@click.option('--batch-size-per-worker', type=int, default=300)
@click.option('--seed', type=int, default=0)
def main(output_path,
         argument_config,
         translation_config,
         size,
         depth,
         branch_extension_steps,
         complication,
         quantification,
         keep_dneg,
         distractor_factor,
         proof_stances,
         world_assump,
         num_workers,
         batch_size_per_worker,
         seed):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(seed)
    proof_stances = json.loads(proof_stances)

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

    gathered_stats = defaultdict(int)
    with open(output_path, 'w') as f_out:

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
                        proof_stances,
                        world_assump,
                        depth,
                        branch_extension_steps,
                    )
                )

            logger.debug('[pass or not checking for finding the cause of hangups] 0')  # HONOKA: we pass here
            instances_list = Parallel(n_jobs=num_workers, backend='multiprocessing')(jobs)
            logger.debug('[pass or not checking for finding the cause of hangups] 1')  # HONOKA: we can't pass here

            cnt = 0
            is_done = False
            num_used_jobs = 0
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

                num_used_jobs += 1

            for name, count in stats.items():
                if not name.startswith('cum.'):
                    gathered_stats[name] = gathered_stats[name] / num_used_jobs

            logger.debug('[pass or not checking for finding the cause of hangups] 2')  # HONOKA: we can't pass here

            logger.info('=========================== gathered stats (batch=%d) ============================',
                        i_batch)
            logger.info('\n' + pformat(gathered_stats))

    with open(str(output_path) + '.stats.json', 'w') as f_out:
        json.dump(dict(gathered_stats), f_out,
                  ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))



if __name__ == '__main__':
    main()
