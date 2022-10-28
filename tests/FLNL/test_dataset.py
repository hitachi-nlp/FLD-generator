import json

import random
from typing import List, Optional
import logging
from pprint import pformat

from FLNL.formula import Formula
from FLNL.argument import Argument
from FLNL.proof_tree_generators import ProofTreeGenerator
from FLNL.distractors import build as build_distractor, FormalLogicDistractor
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


def load_proof_tree_generator(arguments: Optional[List[Argument]] = None,
                              config_paths: Optional[List[str]] = None,
                              complicated_arguments_weight=0.0,
                              quantifier_axiom_arguments_weight=0.0,
                              elim_dneg=True):
    arguments = arguments or []

    config_paths = config_paths or []
    for config_path in config_paths:
        arguments.extend([Argument.from_json(json_obj)
                          for json_obj in json.load(open(config_path))
                          if not json_obj['id'].startswith('__')])

    return ProofTreeGenerator(
        arguments,
        elim_dneg=elim_dneg,
        complicated_arguments_weight=complicated_arguments_weight,
        quantifier_axiom_arguments_weight=quantifier_axiom_arguments_weight,
    )


def load_translator(type_: str,
                    from_: str,
                    word_bank_vocab: Optional[str] = None,
                    limit_vocab_size_per_type: Optional[int] = None,
                    do_translate_to_nl=True):

    if type_ == 'templated_translator':
        if from_ == 'config':
            return build_translator(
                [
                    # './configs/FLNL/translations/thing.json',
                    # './configs/FLNL/translations/thing.sentence_negation.json',

                    # './configs/FLNL/translations/thing.e1.json',
                    # './configs/FLNL/translations/thing.sentence_negation.e1.json',

                    # './configs/FLNL/translations/thing.r.json',
                    # './configs/FLNL/translations/thing.sentence_negation.r.json',

                    './configs/FLNL/translations/thing.all.json',
                    './configs/FLNL/translations/thing.sentence_negation.all.json',
                ],
                build_wordnet_wordbank(
                    'eng',
                    vocab_restrictions=json.load(open(word_bank_vocab)) if word_bank_vocab is not None else None
                ),
                use_fixed_translation=False,
                reused_object_nouns_max_factor=1.0,
                limit_vocab_size_per_type=limit_vocab_size_per_type,
                # volume_to_weight='linear',
                volume_to_weight='sqrt',
                do_translate_to_nl=do_translate_to_nl,
            )
        elif from_ == 'minimum':
            raise ValueError()
        else:
            raise ValueError()
    elif type_ == 'iterative_regexp':
        if from_ == 'config':
            raise ValueError()
        else:
            raise ValueError()
    else:
        raise ValueError()


def load_distractor(generator: ProofTreeGenerator, prototype_formulas: Optional[List[Formula]] = None) -> FormalLogicDistractor:
    # name = 'unknown_interprands'
    # name = 'various_form'
    # name = 'negated_hypothesis_tree'

    # name = 'fallback.unknown_interprands.negated_hypothesis_tree'
    name = 'fallback.various_form.negated_hypothesis_tree'
    # name = 'fallback.negated_hypothesis_tree.unknown_interprands'

    # name = 'mixture.unknown_interprands.negated_hypothesis_tree'
    # name = 'mixture.various_form.negated_hypothesis_tree'
    # name = 'mixture.negated_hypothesis_tree.unknown_interprands'

    return build_distractor(name, generator=generator, prototype_formulas=prototype_formulas)


def generate_dataset(dataset: NLProofSDataset,
                     num_dataset: int = 100) -> None:
    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')
    for nlproof_json, proof_tree, distractors, stats in dataset.generate(num_dataset):

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


def test_original():
    translator = load_translator('sentence_wise_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=['./configs/FLNL/arguments/old/syllogistic_corpus-02.json'],

        # the config already includes the complicated and quantifier_axiom arguments
        complicated_arguments_weight=0.0,
        quantifier_axiom_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              [3, 5],
                              [3, 5],
                              num_distractors=[3, 5],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_LP_pred_only():
    translator = load_translator('templated_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_only.json',
        ],
        complicated_arguments_weight=0.3,
        quantifier_axiom_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              [3, 5],
                              [3, 5],
                              num_distractors=[3, 5],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_minimum_PL():
    translator = load_translator('templated_translator', 'config')

    generator = load_proof_tree_generator(
        arguments=[
            Argument(
                [Formula('(x): {A}x -> {B}x'), Formula('{A}{a}')],
                Formula('{B}{a}'),
                {},
                id='MPL.modus_ponens',
            ),
            Argument(
                [Formula('(x): {A}x -> {B}x'), Formula('(x): {B}x -> {C}x')],
                Formula('(x): {A}x -> {C}x'),
                {},
                id='MPL.syllogism',
            ),

        ],
        complicated_arguments_weight=0.3,
        quantifier_axiom_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              [3, 5],
                              [3, 5],
                              num_distractors=[3, 5],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_LP_pred_arg():
    translator = load_translator('templated_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',
        ],
        complicated_arguments_weight=0.3,
        quantifier_axiom_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              [3, 5],
                              [3, 5],
                              num_distractors=[3, 5],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_PL_pred_arg():
    translator = load_translator(
        'templated_translator',
        'config',
        # word_bank_vocab='./configs/FLNL/vocab/proofwriter-dataset-V2020.12.3.preprocessed_OWA.depth-3ext.json',
        # limit_vocab_size_per_type=100,
    )
    
    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',


            # most important universal theorems
            # './configs/FLNL/arguments/universal_theorem.axiom.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.theorem.pred_arg.json',

            # not that important universal theorems
            # './configs/FLNL/arguments/universal_theorem.axiom.and_or.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.axiom.implication_intro.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.axiom.negation.pred_arg.json',
            # './configs/FLNL/arguments/universal_theorem.theorem.and_or.pred_arg.json',
        ],
        complicated_arguments_weight=0.3,
        quantifier_axiom_arguments_weight=0.3,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['PROOF', 'DISPROOF', 'UNKNOWN'],
                              'OWA',
                              # [3, 5],
                              # [3, 5],
                              # num_distractors=[3, 5],
                              [10],
                              [10],
                              num_distractors=[10],
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


if __name__ == '__main__':
    random.seed(0)
    setup_logger(level=logging.INFO)

    RAISE_IF_TRANSLATION_NOT_FOUND = False

    # test_LP_pred_only()
    # test_LP_pred_arg()
    # test_minimum_PL()
    test_PL_pred_arg()
