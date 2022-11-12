#!/usr/bin/env python
import math
import random
import json
from typing import List, Dict, Optional
from pathlib import Path
from pprint import pformat
import logging
from collections import defaultdict

import click
from tqdm import tqdm
import dill

from FLNL.translators import build as build_translator
from FLNL.word_banks import build_wordnet_wordbank
from FLNL.formula_distractors import SameFormUnkownInterprandsDistractor, FormulaDistractor
from FLNL.argument import Argument
from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.proof_tree_generators import build as build_generator
from FLNL.datasets import NLProofSDataset
from FLNL.proof import ProofTree
from FLNL.utils import nested_merge
from FLNL.formula_distractors import AVAILABLE_DISTRACTORS, build as build_distractor
from FLNL.translation_distractors import build as build_translation_distractor, AVAILABLE_DISTRACTORS as AVAILABLE_TRANSLATION_DISTRACTORS
from joblib import Parallel, delayed

from logger_setup import setup as setup_logger


logger = logging.getLogger(__name__)


def load_dataset(argument_config: List[str],
                 translation_config: List[str],
                 use_fixed_translation: bool,
                 reused_object_nouns_max_factor: float,
                 limit_vocab_size_per_type: Optional[int],
                 translation_volume_to_weight: str,
                 complication: float,
                 quantification: float,
                 keep_dneg: bool,
                 distractor: str,
                 num_distractors: List[int],
                 sample_distractor_formulas_from_tree: bool,
                 sample_hard_negative_distractors: bool,
                 add_subj_obj_swapped_distractor: bool,
                 translation_distractor: str,
                 num_translation_distractors: List[int],
                 proof_stances: List[str],
                 world_assump: str,
                 unknown_ratio: float,
                 use_collapsed_translation_nodes_for_unknown_tree: bool,
                 depths: List[int],
                 branch_extension_steps: List[int]):
    generator = build_generator(
        argument_config,
        elim_dneg=not keep_dneg,
        complication=complication,
        quantification=quantification,
    )

    word_bank = build_wordnet_wordbank('eng')

    _distractor = build_distractor(distractor,
                                   generator=generator,
                                   sample_prototype_formulas_from_tree=sample_distractor_formulas_from_tree,
                                   sample_hard_negatives=sample_hard_negative_distractors)

    _translation_distractor = build_translation_distractor(
        translation_distractor,
        word_bank=word_bank,
    )

    translator = build_translator(translation_config,
                                  word_bank,
                                  use_fixed_translation=use_fixed_translation,
                                  reused_object_nouns_max_factor=reused_object_nouns_max_factor,
                                  limit_vocab_size_per_type=limit_vocab_size_per_type,
                                  volume_to_weight=translation_volume_to_weight)

    pipeline = ProofTreeGenerationPipeline(
        generator,
        distractor=_distractor,
        translation_distractor=_translation_distractor,
        translator=translator,
        add_subj_obj_swapped_distractor=add_subj_obj_swapped_distractor,
    )

    return NLProofSDataset(pipeline,
                           proof_stances,
                           world_assump,
                           depths,
                           branch_extension_steps,
                           num_distractors=num_distractors,
                           num_translation_distractors=num_translation_distractors,
                           unknown_ratio=unknown_ratio,
                           use_collapsed_translation_nodes_for_unknown_tree=use_collapsed_translation_nodes_for_unknown_tree,
                           word_bank = word_bank if use_collapsed_translation_nodes_for_unknown_tree else None)


def generate_instances(size: int, *args):
    # logger = logging.getLogger(__name__)
    logger.debug('[pass or not checking for finding the cause of hangups] 00')  # HONOKA: we pass here

    dataset = load_dataset(*args)  # HONOKA: we pass here
    logger.debug('[pass or not checking for finding the cause of hangups] 01')

    data = []
    _final_stats = None
    for nlproof_json, proof_tree, distractors, translation_distractors, stats in tqdm(dataset.generate(size)):  # HONOKA: we can't pass here
        data.append((nlproof_json, proof_tree, distractors, translation_distractors))
        _final_stats = stats
        log(logger, nlproof_json, proof_tree, distractors, translation_distractors)
    logger.debug('[pass or not checking for finding the cause of hangups] 02')
    return data, _final_stats


def log(logger, nlproof_json: Dict, proof_tree: ProofTree, distractors: List[str], translation_distractors: List[str]):
    logger.info('\n')
    logger.info('--------------- tree --------------')

    logger.info('\n')
    logger.info('\n' + proof_tree.format_str)

    logger.info('\n')
    logger.info('--------------- distractors --------------')
    logger.info('\n' + pformat(distractors))


    logger.info('\n')
    logger.info('--------------- translation distractors --------------')
    logger.info('\n' + pformat(translation_distractors))

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
              default=['./configs/FLNL/translations/thing.json'])
@click.option('--use-fixed-translation', type=bool, is_flag=True)
@click.option('--reused-object-nouns-max-factor', type=float, default=0.0)
@click.option('--limit-vocab-size-per-type', type=int, default=None)
@click.option('--translation-volume-to-weight', type=str, default='linear')
@click.option('--depths', type=str, default=json.dumps([5]))
@click.option('--branch-extension-steps', type=str, default=json.dumps([5]))
@click.option('--complication', type=float, default=0.0)
@click.option('--quantification', type=float, default=0.0)
@click.option('--keep-dneg', is_flag=True, default=False)
@click.option('--distractor', type=click.Choice(AVAILABLE_DISTRACTORS), default='unknown_interprands')
@click.option('--num-distractors', type=str, default=json.dumps([5]))
@click.option('--sample-distractor-formulas-from-tree', type=bool, is_flag=True)
@click.option('--sample-hard-negative-distractors', type=bool, is_flag=True)
@click.option('--add-subj-obj-swapped-distractor', type=bool, is_flag=True)
@click.option('--translation-distractor', type=click.Choice(AVAILABLE_TRANSLATION_DISTRACTORS), default='word_swap')
@click.option('--num-translation-distractors', type=str, default=json.dumps([5]))
@click.option('--proof-stances', type=str, default=json.dumps(['PROOF', 'DISPROOF', 'UNKNOWN']))
@click.option('--world-assump', default='CWA')
@click.option('--unknown-ratio', type=float, default = 1 / 3.)
@click.option('--use-collapsed-translation-nodes-for-unknown-tree', default='CWA')
@click.option('--num-workers', type=int, default=1)
@click.option('--batch-size-per-worker', type=int, default=300)
@click.option('--seed', type=int, default=0)
def main(output_path,
         argument_config,
         translation_config,
         use_fixed_translation,
         reused_object_nouns_max_factor,
         limit_vocab_size_per_type,
         translation_volume_to_weight,
         size,
         depths,
         branch_extension_steps,
         complication,
         quantification,
         keep_dneg,
         distractor,
         num_distractors,
         sample_distractor_formulas_from_tree,
         sample_hard_negative_distractors,
         add_subj_obj_swapped_distractor,
         translation_distractor,
         num_translation_distractors,
         proof_stances,
         world_assump,
         unknown_ratio,
         use_collapsed_translation_nodes_for_unknown_tree,
         num_workers,
         batch_size_per_worker,
         seed):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(seed)
    depths = json.loads(depths)
    branch_extension_steps = json.loads(branch_extension_steps)
    num_distractors = json.loads(num_distractors)
    num_translation_distractors = json.loads(num_translation_distractors)
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
                        use_fixed_translation,
                        reused_object_nouns_max_factor,
                        limit_vocab_size_per_type,
                        translation_volume_to_weight,
                        complication,
                        quantification,
                        keep_dneg,
                        distractor,
                        num_distractors,
                        sample_distractor_formulas_from_tree,
                        sample_hard_negative_distractors,
                        add_subj_obj_swapped_distractor,
                        translation_distractor,
                        num_translation_distractors,
                        proof_stances,
                        world_assump,
                        unknown_ratio,
                        use_collapsed_translation_nodes_for_unknown_tree,
                        depths,
                        branch_extension_steps,
                    )
                )

            logger.debug('[pass or not checking for finding the cause of hangups] 0')  # HONOKA: we pass here
            instances_list = Parallel(n_jobs=num_workers, backend='multiprocessing')(jobs)
            logger.debug('[pass or not checking for finding the cause of hangups] 1')  # HONOKA: we can't pass here

            cnt = 0
            is_done = False
            num_jobs: Dict[str, int] = defaultdict(int)
            for instances, stats in instances_list:
                if is_done:
                    break

                for nlproof_json, proof_tree, _, _ in instances:
                    if cnt >= size:
                        is_done = True
                        break
                    f_out.write(json.dumps(nlproof_json) + '\n')
                    cnt += 1

                for name, count in stats.items():
                    if count is not None:
                        gathered_stats[name] += count
                        num_jobs[name] += 1

            for name, count in gathered_stats.items():
                if not name.startswith('cum.'):
                    gathered_stats[name] = gathered_stats[name] / num_jobs[name]

            logger.debug('[pass or not checking for finding the cause of hangups] 2')  # HONOKA: we can't pass here

            logger.info('=========================== gathered stats (batch=%d) ============================',
                        i_batch)
            logger.info('\n' + pformat(gathered_stats))

    with open(str(output_path) + '.stats.json', 'w') as f_out:
        json.dump(dict(gathered_stats), f_out,
                  ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))


if __name__ == '__main__':
    main()
