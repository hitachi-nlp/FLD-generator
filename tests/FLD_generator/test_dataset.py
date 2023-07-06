import json

import random
from typing import List, Optional, Dict
import logging
from pprint import pformat
import glob
from collections import defaultdict

from FLD_generator.formula import Formula
from FLD_generator.argument import Argument
from FLD_generator.proof_tree_generators import build as build_generator
from FLD_generator.formula_distractors import build as build_distractor
from FLD_generator.translation_distractors import build as build_translation_distractor
from FLD_generator.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLD_generator.datasets import NLProofSDataset
from FLD_generator.word_banks import build_wordnet_wordbank
from FLD_generator.translators import (
    build as build_translator,
    TemplatedTranslator,
)
from FLD_generator.interpretation import formula_is_identical_to
from FLD_generator.utils import nested_merge, log_results
from logger_setup import setup as setup_logger

import line_profiling

logger = logging.getLogger(__name__)


@profile
def generate_dataset(dataset: NLProofSDataset,
                     num_dataset: int = 50) -> None:
    # agg_stats: Dict[str, int] = defaultdict(int)
    for i_sample, (nlproof_json, proof_tree, distractors, translation_distractors, stats) in enumerate(dataset.generate(num_dataset)):
        log_results(logger, i_sample=i_sample, nlproof_json=nlproof_json, proof_tree=proof_tree,
                    distractors=distractors, translation_distractors=translation_distractors,
                    stats=None)
        # for name, count in stats.items():
        #     if count is not None:
        #         agg_stats[name] += count
    # logger.info(pformat(dict(agg_stats)))


@profile
def test_generate_dataset():

    generator = build_generator(
        [
            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/others/AACorpus.pred_arg.json',

            # # -- we exclude the below for speed --
            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            # './configs/arguments/theorems/theorem.G_MP.pred_arg.json',

            # -- not tested. may not work --
            # './configs/arguments/theorems/universal_theorem.axiom.pred_arg.json',
            # './configs/arguments/theorems/universal_theorem.theorem.pred_arg.json',

            # not that important universal theorems
            # './configs/arguments/theorems/universal_theorem.axiom.and_or.pred_arg.json',
            # './configs/arguments/theorems/universal_theorem.axiom.implication_intro.pred_arg.json',
            # './configs/arguments/theorems/universal_theorem.axiom.negation.pred_arg.json',
            # './configs/arguments/theorems/universal_theorem.theorem.and_or.pred_arg.json',
        ],
        elim_dneg=True,
        complex_formula_arguments_weight=0.3,
        quantifier_axiom_arguments_weight=0.5,
        quantifier_axioms=[
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        quantification_degree='all_constants',
    )

    distractor = build_distractor(
        # 'unknown_interprands',
        # 'various_form',

        # 'fallback.unknown_interprands.negative_tree',
        # 'fallback.negative_tree.unknown_interprands',
        # 'fallback.negative_tree.various_form',
        # 'fallback.various_form.negative_tree',

        # 'mixture.negative_tree.simplified_formula.various_form',
        # 'mixture.negative_tree.negative_tree.simplified_formula.various_form',
        # 'mixture.negative_tree.negative_tree',

        # 'mixture.negative_tree_double',
        # 'mixture.negative_tree_triple',
        'mixture.negative_tree_quadruple',

        generator=generator,
        negative_tree_negated_hypothesis_ratio=1.0,
    )

    word_bank = None
    # word_bank = build_wordnet_wordbank('eng')

    translator = None
    # translator = build_translator(
    #     ['./configs/translations/thing.v1/'],
    #     word_bank,
    #     use_fixed_translation=True,
    #     reused_object_nouns_max_factor=1.0,
    #     limit_vocab_size_per_type=None,
    #     volume_to_weight='sqrt',
    #     do_translate_to_nl=True,
    # )

    translation_distractor = None
    # translation_distractor = build_translation_distractor(word_bank=word_bank)

    pipeline = ProofTreeGenerationPipeline(
        generator,
        distractor=distractor,
        translation_distractor=translation_distractor,
        fallback_from_formula_to_translation_distractor=True,
        translator=translator,
        add_subj_obj_swapped_distractor=True,
    )

    depth_range = (1, 3)
    branch_extensions_range = (2, 5)
    distractors_range = (15, 20)

    unknown_ratio = 0.33
    depth_1_reference_weight = None

    use_collapsed_translation_nodes_for_unknown_tree = False
    translation_distractors_range = (0, 5) if translation_distractor is not None else (0, 0)

    dataset = NLProofSDataset(
        pipeline,

        depth_range,
        branch_extensions_range,
        depth_1_reference_weight=depth_1_reference_weight,
        unknown_ratio=unknown_ratio,

        distractors_range=distractors_range,

        use_collapsed_translation_nodes_for_unknown_tree=use_collapsed_translation_nodes_for_unknown_tree,
        word_bank=word_bank,
        translation_distractors_range=translation_distractors_range,

        raise_if_translation_not_found=False
    )

    generate_dataset(dataset)


if __name__ == '__main__':
    random.seed(0)
    setup_logger(level=logging.INFO)

    # test_generate_dataset_AACorpus()
    test_generate_dataset()
