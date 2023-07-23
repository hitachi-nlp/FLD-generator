#!/usr/bin/env python
import math
import random
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from pprint import pformat
import logging
from collections import defaultdict

import click
from tqdm import tqdm
import dill

from FLD_generator.translators import build as build_translator
from FLD_generator.word_banks import build_wordnet_wordbank
from FLD_generator.formula_distractors import FormulaDistractor
from FLD_generator.argument import Argument
from FLD_generator.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLD_generator.proof_tree_generators import build as build_generator
from FLD_generator.datasets import NLProofSDataset
from FLD_generator.proof import ProofTree
from FLD_generator.utils import nested_merge
from FLD_generator.formula_distractors import build as build_distractor
from FLD_generator.translation_distractors import build as build_translation_distractor
from FLD_generator.utils import _build_bounded_msg, log_results
from joblib import Parallel, delayed

from logger_setup import setup as setup_logger


logger = logging.getLogger(__name__)


def load_dataset(argument_config: List[str],
                 translation_config: List[str],
                 use_fixed_translation: bool,
                 reused_object_nouns_max_factor: float,
                 limit_vocab_size_per_type: Optional[int],
                 # translation_volume_to_weight: str,
                 translation_default_weight_type: str,
                 complex_formula_arguments_weight: float,
                 quantifier_axiom_arguments_weight: float,
                 quantifier_axioms: Optional[List[str]],
                 quantification_degree: str,
                 keep_dneg: bool,
                 distractor: str,
                 distractors_range: Tuple[int, int],
                 sample_distractor_prototype_formulas_from_all_possible_formulas: bool,
                 disallow_simplified_tree_formulas_as_distractor_prototype: bool,
                 disallow_hard_negative_distractors: bool,
                 # negative_tree_negated_hypothesis_ratio: float,
                 disallow_subj_obj_swapped_distractor: bool,
                 translation_distractor: str,
                 fallback_from_formula_to_translation_distractor: bool,
                 translation_distractors_range: Tuple[int, int],
                 proof_stances: List[str],
                 world_assump: str,
                 unknown_ratio: float,
                 use_collapsed_translation_nodes_for_unknown_tree: bool,
                 swap_ng_words: Optional[List[str]],
                 depth_range: Tuple[int, int],
                 depth_distrib: str,
                 force_fix_illegal_intermediate_constants: bool,
                 branch_extensions_range: Tuple[int, int]):
    generator = build_generator(
        argument_config,
        elim_dneg=not keep_dneg,
        complex_formula_arguments_weight=complex_formula_arguments_weight,
        quantifier_axiom_arguments_weight=quantifier_axiom_arguments_weight,
        quantifier_axioms=quantifier_axioms,
        quantification_degree=quantification_degree,
    )

    logger.info(_build_bounded_msg(f'{"[start] building wordnet":<30}', 3))
    word_bank = build_wordnet_wordbank('eng')
    logger.info(_build_bounded_msg(f'{"[finish] building wordnet":<30}', 3))

    if distractors_range[1] > 0:
        logger.info(_build_bounded_msg(f'{"[start] building distractor":<30}', 3))
        _distractor = build_distractor(
            distractor,
            generator=generator,
            sample_prototype_formulas_from_all_possible_formulas=sample_distractor_prototype_formulas_from_all_possible_formulas,
            disallow_simplified_formulas_as_prototype=disallow_simplified_tree_formulas_as_distractor_prototype,
            sample_hard_negatives=not disallow_hard_negative_distractors,
            # negative_tree_negated_hypothesis_ratio=negative_tree_negated_hypothesis_ratio,
        )
        logger.info(_build_bounded_msg(f'{"[finish] building distractor":<30}', 3))
    else:
        _distractor = None

    if translation_distractors_range[1] > 0:
        logger.info(_build_bounded_msg(f'{"[start] building translation distractor":<30}', 3))
        _translation_distractor = build_translation_distractor(
            translation_distractor,
            word_bank=word_bank,
            swap_ng_words=swap_ng_words,
        )
        logger.info(_build_bounded_msg(f'{"[finish] building translation distractor":<30}', 3))
    else:
        _translation_distractor = None

    logger.info(_build_bounded_msg(f'{"[start] building translator":<30}', 3))
    translator = build_translator(translation_config,
                                  word_bank,
                                  use_fixed_translation=use_fixed_translation,
                                  reused_object_nouns_max_factor=reused_object_nouns_max_factor,
                                  limit_vocab_size_per_type=limit_vocab_size_per_type,
                                  # volume_to_weight=translation_volume_to_weight,
                                  default_weight_type=translation_default_weight_type)
    logger.info(_build_bounded_msg(f'{"[finish] building translator":<30}', 3))

    pipeline = ProofTreeGenerationPipeline(
        generator,
        distractor=_distractor,
        translation_distractor=_translation_distractor,
        fallback_from_formula_to_translation_distractor=fallback_from_formula_to_translation_distractor,
        translator=translator,
        add_subj_obj_swapped_distractor=not disallow_subj_obj_swapped_distractor,
    )

    if depth_distrib == 'flat':
        depth_weights = None
        depth_1_reference_weight = None
    elif depth_distrib == 'flat.no_reference':
        depth_weights = None
        depth_1_reference_weight = 0.0
    elif depth_distrib == 'ruletaker.ours.20221202':
        if set(depth_range) != (1, 3):
            raise ValueError(f'depths {depth_range} is not consistent with ruletaker.ours.20221202.')
        # see "depth分布" of experiments.md
        depth_weights = [0.40, 0.15, 0.12]
        depth_1_reference_weight = 0.23 / (0.23 + 0.17)
    else:
        raise ValueError(f'Unknown depth distrib {depth_distrib}')

    return NLProofSDataset(pipeline,
                           depth_range,
                           branch_extensions_range,
                           proof_stances=proof_stances,
                           world_assump=world_assump,
                           depth_weights=depth_weights,
                           depth_1_reference_weight=depth_1_reference_weight,
                           force_fix_illegal_intermediate_constants=force_fix_illegal_intermediate_constants,
                           distractors_range=distractors_range,
                           translation_distractors_range=translation_distractors_range,
                           unknown_ratio=unknown_ratio,
                           use_collapsed_translation_nodes_for_unknown_tree=use_collapsed_translation_nodes_for_unknown_tree,
                           swap_ng_words=swap_ng_words,
                           word_bank = word_bank if use_collapsed_translation_nodes_for_unknown_tree else None)


def generate_instances(size: int, *args):
    dataset = load_dataset(*args)
    data = []
    agg_stats = defaultdict(int)
    for i_sample, (nlproof_json, proof_tree, distractors, translation_distractors, stats) in tqdm(enumerate(dataset.generate(size))):
        data.append((nlproof_json, proof_tree, distractors, translation_distractors))

        log_results(logger, i_sample=i_sample, nlproof_json=nlproof_json, proof_tree=proof_tree,
                    distractors=distractors, translation_distractors=translation_distractors,
                    stats=None)

        if stats is not None:
            for name, count in stats.items():
                if count is not None:
                    agg_stats[name] += count

    return data, agg_stats


@click.command()
@click.argument('output-path')
@click.argument('size', type=int)
@click.option('--argument-config', '--ac',
              multiple=True,
              default=['./configs/arguments/axioms'],
              help='argument (deduction rule) configuration files')
@click.option('--complex-formula-arguments-weight', type=float, default=0.0)
@click.option('--quantifier-axiom-arguments-weight', type=float, default=0.0)
@click.option('--quantifier-axiom', multiple=True, default=None)
@click.option('--quantification-degree', type=str, default='all_constants')
#
@click.option('--depth-range', type=str, default=json.dumps([1, 5]))
@click.option('--depth-distrib', type=click.Choice(['flat', 'flat.no_reference', 'ruletaker.ours.20221202']))
@click.option('--branch-extensions-range', type=str, default=json.dumps([5, 5]))
#
@click.option('--force-fix-illegal-intermediate-constants', is_flag=True)
@click.option('--keep-dneg', is_flag=True, default=False)
#
@click.option('--translation-config', '--tc',
              multiple=True,
              default=['./configs/translations/thing.v1'],
              help='natural language translation config files')
@click.option('--use-fixed-translation', type=bool, is_flag=True)
@click.option('--reused-object-nouns-max-factor', type=float, default=1.0)
@click.option('--limit-vocab-size-per-type', type=int, default=None)
# @click.option('--translation-volume-to-weight', type=str, default='sqrt')
@click.option('--translation-default-weight-type', type=str, default='W__SQRT(VOLUME)__1.0')
#
@click.option('--distractor', default='mixture.negative_tree.negative_tree')
@click.option('--distractors-range', type=str, default=json.dumps([5, 5]))
@click.option('--disallow-hard-negative-distractors', type=bool, is_flag=True)
# @click.option('--negative-tree-negated-hypothesis-ratio', type=float, default=0.5)
@click.option('--sample-distractor-prototype-formulas-from-all-possible-formulas', type=bool, is_flag=True)
@click.option('--disallow-simplified-tree-formulas-as-distractor-prototype', type=bool, is_flag=True)
@click.option('--disallow-subj-obj-swapped-distractor', type=bool, is_flag=True)
@click.option('--translation-distractor', default='word_swap')
@click.option('--translation-distractors-range', type=str, default=json.dumps([0, 0]))
@click.option('--fallback-from-formula-to-translation-distractor', is_flag=True, default=False)
@click.option('--proof-stances', type=str, default=json.dumps(['PROVED', 'DISPROVED', 'UNKNOWN']))
@click.option('--world-assump', default='OWA')
@click.option('--unknown-ratio', type=float, default = 1 / 3.)
@click.option('--use-collapsed-translation-nodes-for-unknown-tree', is_flag=True, default=False)
@click.option('--swap-ng-words-config', default=None)
@click.option('--num-workers', type=int, default=1)
@click.option('--min-size-per-worker', type=int,
              default=10,
              # multithread  : data load = 4min, generation = 140 instances / 14min = 10 instances / min
              )
@click.option('--batch-size-per-worker', type=int, default=10000)
@click.option('--seed', type=int, default=0)
def main(output_path,
         argument_config,
         translation_config,
         use_fixed_translation,
         reused_object_nouns_max_factor,
         limit_vocab_size_per_type,
         # translation_volume_to_weight,
         translation_default_weight_type,
         size,
         depth_range,
         depth_distrib,
         force_fix_illegal_intermediate_constants,
         branch_extensions_range,
         complex_formula_arguments_weight,
         quantifier_axiom_arguments_weight,
         quantifier_axiom,
         quantification_degree,
         keep_dneg,
         distractor,
         distractors_range,
         sample_distractor_prototype_formulas_from_all_possible_formulas,
         disallow_simplified_tree_formulas_as_distractor_prototype,
         disallow_hard_negative_distractors,
         # negative_tree_negated_hypothesis_ratio,
         disallow_subj_obj_swapped_distractor,
         translation_distractor,
         fallback_from_formula_to_translation_distractor,
         translation_distractors_range,
         proof_stances,
         world_assump,
         unknown_ratio,
         use_collapsed_translation_nodes_for_unknown_tree,
         swap_ng_words_config,
         num_workers,
         min_size_per_worker,
         batch_size_per_worker,
         seed):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(seed)
    depth_range = tuple(json.loads(depth_range))
    branch_extensions_range = json.loads(branch_extensions_range)
    distractors_range = json.loads(distractors_range)
    translation_distractors_range = json.loads(translation_distractors_range)
    proof_stances = json.loads(proof_stances)
    swap_ng_words = json.load(open(swap_ng_words_config)) if swap_ng_words_config is not None else None

    if len(argument_config) == 0:
        raise ValueError()

    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    size_per_worker = math.ceil(size / num_workers)
    if size_per_worker < min_size_per_worker:
        num_workers = max(int(size / min_size_per_worker), 1)
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
                        # translation_volume_to_weight,
                        translation_default_weight_type,
                        complex_formula_arguments_weight,
                        quantifier_axiom_arguments_weight,
                        quantifier_axiom,
                        quantification_degree,
                        keep_dneg,
                        distractor,
                        distractors_range,
                        sample_distractor_prototype_formulas_from_all_possible_formulas,
                        disallow_simplified_tree_formulas_as_distractor_prototype,
                        disallow_hard_negative_distractors,
                        # negative_tree_negated_hypothesis_ratio,
                        disallow_subj_obj_swapped_distractor,
                        translation_distractor,
                        fallback_from_formula_to_translation_distractor,
                        translation_distractors_range,
                        proof_stances,
                        world_assump,
                        unknown_ratio,
                        use_collapsed_translation_nodes_for_unknown_tree,
                        swap_ng_words,
                        depth_range,
                        depth_distrib,
                        force_fix_illegal_intermediate_constants,
                        branch_extensions_range,
                    )
                )

            logger.info('creating corpus with %d jobs', num_workers)
            instances_list = Parallel(n_jobs=num_workers, backend='multiprocessing')(jobs)

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

            logger.info('=========================== gathered stats (batch=%d) ============================',
                        i_batch)
            logger.info('\n' + pformat(gathered_stats))

    with open(str(output_path) + '.stats.json', 'w') as f_out:
        json.dump(dict(gathered_stats), f_out,
                  ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! create_FLD_corpus.py DONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


if __name__ == '__main__':
    main()
