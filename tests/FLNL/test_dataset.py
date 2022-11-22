import json

import random
from typing import List, Optional
import logging
from pprint import pformat

from FLNL.formula import Formula
from FLNL.argument import Argument
from FLNL.proof_tree_generators import build as build_generator, ProofTreeGenerator
from FLNL.formula_distractors import build as build_distractor
from FLNL.translation_distractors import build as build_translation_distractor
from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.datasets import NLProofSDataset
from FLNL.word_banks import build_wordnet_wordbank
from FLNL.translators import (
    build as build_translator,
    TemplatedTranslator,
)
from FLNL.interpretation import formula_is_identical_to
from FLNL.utils import nested_merge
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


RAISE_IF_TRANSLATION_NOT_FOUND = True


def generate_dataset(dataset: NLProofSDataset,
                     num_dataset: int = 10000) -> None:
    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')
    for nlproof_json, proof_tree, distractors, translation_distractors, stats in dataset.generate(num_dataset):

        logger.info('\n')
        logger.info('--------------- tree --------------')

        logger.info('\n')
        logger.info('\n' + proof_tree.format_str)

        logger.info('\n')
        logger.info('--------------- formula distractors --------------')
        logger.info('\n' + pformat(distractors))

        logger.info('\n')
        logger.info('--------------- translation distractors --------------')
        logger.info('\n' + pformat(translation_distractors))

        logger.info('\n')
        logger.info('--------------- NLProofs json --------------')
        logger.info('\n' + pformat(nlproof_json))

        logger.info('\n')
        logger.info('--------------- stats --------------')
        for key in ['avg.word_count_all']:
            if key in stats:
                logger.info('%s: %s', key, stats[key])
        # logger.info(dict(stats))
        # logger.info('\n' + pformat(stats))

        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')

        # f_out.write(json.dumps(nlproof_json) + '\n')


def test_generate_dataset():
    def _to_range(begin: int, end: int) -> List[int]:
        return list(range(begin, end + 1))

    word_bank = build_wordnet_wordbank('eng')

    translator = build_translator(
        [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        word_bank,
        use_fixed_translation=False,
        reused_object_nouns_max_factor=1.0,
        limit_vocab_size_per_type=None,
        volume_to_weight='sqrt',
        do_translate_to_nl=True,
    )
   
    generator = build_generator(
        [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # -- we exclude the below for speed --
            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',


            # -- not tested. may not work --
            # './configs/FLNL/arguments/universal_theorem.axiom.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.theorem.pred_arg.json',

            # not that important universal theorems
            # './configs/FLNL/arguments/universal_theorem.axiom.and_or.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.axiom.implication_intro.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.axiom.negation.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.theorem.and_or.pred_arg.json',
        ],
        elim_dneg=True,
        complication=0.3,
        quantification=0.2,
    )

    distractor = build_distractor(
        # 'unknown_interprands',
        # 'various_form',
        # 'negative_tree',

        # 'fallback.unknown_interprands.negative_tree',
        # 'fallback.negative_tree.unknown_interprands',
        'fallback.negative_tree.various_form',
        # 'fallback.various_form.negative_tree',

        # 'mixture.unknown_interprands.negative_tree',
        # 'mixture.various_form.negative_tree',
        # 'mixture.negative_tree.unknown_interprands',

        generator=generator,
        sample_prototype_formulas_from_tree=True,
        sample_hard_negatives=True,
        try_negated_hypothesis_first=True,
    )

    # translation_distractor = build_translation_distractor(
    #     'word_swap',
    #     word_bank=word_bank,
    # )

    pipeline = ProofTreeGenerationPipeline(
        generator,
        distractor=distractor,
        translation_distractor=None,
        fallback_from_formula_to_translation_distractor=True,
        translator=translator,
        add_subj_obj_swapped_distractor=True,
    )

    dataset = NLProofSDataset(pipeline,
                              ['PROOF', 'DISPROOF', 'UNKNOWN'],
                              'OWA',
                              _to_range(1, 3),
                              _to_range(0, 0),
                              depth_1_weight=2.0,
                              unknown_ratio=0.333,
                              use_collapsed_translation_nodes_for_unknown_tree=False,
                              word_bank=word_bank,
                              num_distractors=[0],
                              # num_translation_distractors=[0],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


if __name__ == '__main__':
    random.seed(0)
    setup_logger(level=logging.INFO)

    RAISE_IF_TRANSLATION_NOT_FOUND = False
    test_generate_dataset()
