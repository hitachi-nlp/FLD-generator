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
                 translation_volume_to_weight: str,
                 complication: float,
                 quantification: float,
                 quantifier_axioms: Optional[List[str]],
                 quantify_implication_premise_conclusion_at_once: Optional[bool],
                 quantify_all_at_once: Optional[bool],
                 keep_dneg: bool,
                 distractor: str,
                 num_distractors: List[int],
                 sample_distractor_formulas_from_tree: bool,
                 use_simplified_tree_formulas_as_distractor_prototype: bool,
                 sample_hard_negative_distractors: bool,
                 dont_try_negative_hypothesis: bool,
                 add_subj_obj_swapped_distractor: bool,
                 translation_distractor: str,
                 fallback_from_formula_to_translation_distractor: bool,
                 num_translation_distractors: List[int],
                 proof_stances: List[str],
                 world_assump: str,
                 unknown_ratio: float,
                 use_collapsed_translation_nodes_for_unknown_tree: bool,
                 swap_ng_words: Optional[List[str]],
                 depths: List[int],
                 depth_distribution: str,
                 force_fix_illegal_intermediate_constants: bool,
                 branch_extension_steps: List[int]):
    generator = build_generator(
        argument_config,
        elim_dneg=not keep_dneg,
        complication=complication,
        quantification=quantification,
        quantifier_axioms=quantifier_axioms,
        quantify_implication_premise_conclusion_at_once=quantify_implication_premise_conclusion_at_once,
        quantify_all_at_once=quantify_all_at_once,
    )

    logger.info(_build_bounded_msg(f'{"[start] building wordnet":<30}', 3))
    word_bank = build_wordnet_wordbank('eng')
    logger.info(_build_bounded_msg(f'{"[finish] building wordnet":<30}', 3))

    if any(size > 0 for size in num_distractors):
        logger.info(_build_bounded_msg(f'{"[start] building distractor":<30}', 3))
        _distractor = build_distractor(distractor,
                                       generator=generator,
                                       sample_prototype_formulas_from_tree=sample_distractor_formulas_from_tree,
                                       use_simplified_formulas_as_prototype=use_simplified_tree_formulas_as_distractor_prototype,
                                       sample_hard_negatives=sample_hard_negative_distractors,
                                       negated_hypothesis_ratio=0.0 if dont_try_negative_hypothesis else 0.5)
        logger.info(_build_bounded_msg(f'{"[finish] building distractor":<30}', 3))
    else:
        _distractor = None

    if any(size > 0 for size in num_translation_distractors) or fallback_from_formula_to_translation_distractor:
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
                                  volume_to_weight=translation_volume_to_weight)
    logger.info(_build_bounded_msg(f'{"[finish] building translator":<30}', 3))

    pipeline = ProofTreeGenerationPipeline(
        generator,
        distractor=_distractor,
        translation_distractor=_translation_distractor,
        fallback_from_formula_to_translation_distractor=fallback_from_formula_to_translation_distractor,
        translator=translator,
        add_subj_obj_swapped_distractor=add_subj_obj_swapped_distractor,
    )

    if depth_distribution == 'flat':
        depth_weights = None
        depth_1_reference_weight = None
    elif depth_distribution == 'ruletaker.ours.20221202':
        if set(depths) != set([1, 2, 3]):
            raise ValueError(f'depths {depths} is not consistent with ruletaker.ours.20221202.')
        # see "depth分布" of experiments.md
        depth_weights = [0.40, 0.15, 0.12]
        depth_1_reference_weight = 0.23 / (0.23 + 0.17)
    else:
        raise ValueError(f'Unknown depth distribution {depth_distribution}')

    return NLProofSDataset(pipeline,
                           proof_stances,
                           world_assump,
                           depths,
                           branch_extension_steps,
                           depth_weights=depth_weights,
                           depth_1_reference_weight=depth_1_reference_weight,
                           force_fix_illegal_intermediate_constants=force_fix_illegal_intermediate_constants,
                           num_distractors=num_distractors,
                           num_translation_distractors=num_translation_distractors,
                           unknown_ratio=unknown_ratio,
                           use_collapsed_translation_nodes_for_unknown_tree=use_collapsed_translation_nodes_for_unknown_tree,
                           swap_ng_words=swap_ng_words,
                           word_bank = word_bank if use_collapsed_translation_nodes_for_unknown_tree else None)


def generate_instances(size: int, *args):
    dataset = load_dataset(*args)
    data = []
    agg_stats = defaultdict(int)
    for nlproof_json, proof_tree, distractors, translation_distractors, stats in tqdm(dataset.generate(size)):
        data.append((nlproof_json, proof_tree, distractors, translation_distractors))

        log_results(logger, nlproof_json=nlproof_json, proof_tree=proof_tree,
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
              multiple=True, default=[])
@click.option('--translation-config', '--tc',
              multiple=True,
              default=['./configs/translations/thing.json'])
@click.option('--use-fixed-translation', type=bool, is_flag=True)
@click.option('--reused-object-nouns-max-factor', type=float, default=0.0)
@click.option('--limit-vocab-size-per-type', type=int, default=None)
@click.option('--translation-volume-to-weight', type=str, default='linear')
@click.option('--depths', type=str, default=json.dumps([5]))
@click.option('--depth-distribution', type=click.Choice(['flat', 'ruletaker.ours.20221202']))
@click.option('--force-fix-illegal-intermediate-constants', is_flag=True)
@click.option('--branch-extension-steps', type=str, default=json.dumps([5]))
@click.option('--complication', type=float, default=0.0)
@click.option('--quantification', type=float, default=0.0)
@click.option('--quantifier-axiom', multiple=True, default=None)
@click.option('--translation-config', '--tc', multiple=True,
              default=['./configs/translations/thing.json'])
@click.option('--quantify-implication-premise-conclusion-at_once', is_flag=True)
@click.option('--quantify-all-at-once', is_flag=True)
@click.option('--keep-dneg', is_flag=True, default=False)
@click.option('--distractor', default='unknown_interprands')
@click.option('--num-distractors', type=str, default=json.dumps([5]))
@click.option('--sample-distractor-formulas-from-tree', type=bool, is_flag=True)
@click.option('--use-simplified-tree-formulas-as-distractor-prototype', type=bool, is_flag=True)
@click.option('--dont-try-negative-hypothesis', type=bool, is_flag=True)
@click.option('--sample-hard-negative-distractors', type=bool, is_flag=True)
@click.option('--add-subj-obj-swapped-distractor', type=bool, is_flag=True)
@click.option('--translation-distractor', default='word_swap')
@click.option('--fallback-from-formula-to-translation-distractor', is_flag=True, default=False)
@click.option('--num-translation-distractors', type=str, default=json.dumps([5]))
@click.option('--proof-stances', type=str, default=json.dumps(['PROVED', 'DISPROVED', 'UNKNOWN']))
@click.option('--world-assump', default='CWA')
@click.option('--unknown-ratio', type=float, default = 1 / 3.)
@click.option('--use-collapsed-translation-nodes-for-unknown-tree', is_flag=True, default=False)
@click.option('--swap-ng-words-config', default='./configs/translation_distractors/swap_ng_words.json')
@click.option('--num-workers', type=int, default=1)
@click.option('--min-size-per-worker', type=int, default=1000)   # single thread: data load = 2min, generation = 300 instances / 8min    vs    multithread: data load = 20min, generation = 5 x 300 instances / 8min
@click.option('--batch-size-per-worker', type=int, default=10000)
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
         depth_distribution,
         force_fix_illegal_intermediate_constants,
         branch_extension_steps,
         complication,
         quantification,
         quantifier_axiom,
         quantify_implication_premise_conclusion_at_once,
         quantify_all_at_once,
         keep_dneg,
         distractor,
         num_distractors,
         sample_distractor_formulas_from_tree,
         use_simplified_tree_formulas_as_distractor_prototype,
         sample_hard_negative_distractors,
         dont_try_negative_hypothesis,
         add_subj_obj_swapped_distractor,
         translation_distractor,
         fallback_from_formula_to_translation_distractor,
         num_translation_distractors,
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
    depths = json.loads(depths)
    branch_extension_steps = json.loads(branch_extension_steps)
    num_distractors = json.loads(num_distractors)
    num_translation_distractors = json.loads(num_translation_distractors)
    proof_stances = json.loads(proof_stances)
    swap_ng_words = json.load(open(swap_ng_words_config))

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
                        translation_volume_to_weight,
                        complication,
                        quantification,
                        quantifier_axiom,
                        quantify_implication_premise_conclusion_at_once,
                        quantify_all_at_once,
                        keep_dneg,
                        distractor,
                        num_distractors,
                        sample_distractor_formulas_from_tree,
                        use_simplified_tree_formulas_as_distractor_prototype,
                        sample_hard_negative_distractors,
                        dont_try_negative_hypothesis,
                        add_subj_obj_swapped_distractor,
                        translation_distractor,
                        fallback_from_formula_to_translation_distractor,
                        num_translation_distractors,
                        proof_stances,
                        world_assump,
                        unknown_ratio,
                        use_collapsed_translation_nodes_for_unknown_tree,
                        swap_ng_words,
                        depths,
                        depth_distribution,
                        force_fix_illegal_intermediate_constants,
                        branch_extension_steps,
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


if __name__ == '__main__':
    main()
