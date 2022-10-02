import json


import random
from typing import List, Optional
import logging
from pprint import pformat

from FLNL.formula import Formula
from FLNL.argument import Argument
from FLNL.proof_tree_generators import ProofTreeGenerator
from FLNL.distractors import build as build_distractor, FormalLogicDistractor
from FLNL.translators import SentenceWiseTranslator, IterativeRegexpTranslator, ClauseTypedTranslator
from FLNL.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from FLNL.datasets import NLProofSDataset
from FLNL.word_banks import EnglishWordBank
from FLNL.utils import nested_merge
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


RAISE_IF_TRANSLATION_NOT_FOUND = True


def load_proof_tree_generator(arguments: Optional[List[Argument]] = None,
                              config_paths: Optional[List[str]] = None,
                              complicated_arguments_weight=0.0,
                              quantified_arguments_weight=0.0,
                              elim_dneg=True):
    arguments = arguments or []

    config_paths = config_paths or []
    for config_path in config_paths:
        arguments.extend([Argument.from_json(json_obj)
                          for json_obj in json.load(open(config_path))
                          if not json_obj['id'].startswith('__')])

    return ProofTreeGenerator(arguments,
                              elim_dneg=elim_dneg,
                              complicated_arguments_weight=complicated_arguments_weight,
                              quantified_arguments_weight=quantified_arguments_weight)


def load_translator(type_: str,
                    from_: str,
                    do_translate_to_nl=True):
    if type_ == 'sentence_wise_translator':
        if from_ == 'config':
            sentence_translations_config_path = './configs/FLNL/translations/old/syllogistic_corpus-02.json'
            sentence_translations = json.load(open(sentence_translations_config_path))
            predicate_translations = [f'red-{str(i).zfill(2)}' for i in range(30)]
            constant_translations = [f'Alice-{str(i).zfill(2)}' for i in range(30)]
            return SentenceWiseTranslator(
                sentence_translations,
                predicate_translations=predicate_translations,
                constant_translations=constant_translations,
                do_translate_to_nl=do_translate_to_nl,
            )
        elif from_ == 'minimum':
            sentence_translations = {
                '{A}{a}': [
                    '{a} is {A}.',
                ],

                '(x): {A}x -> {B}x': [
                    'If someone is {A}, then the one is {B}.',
                    'Every {A} is a {B}.',
                ],

                '(x): ({A} v {B})x -> {C}x': [
                    'If someone is {A} or {B}, then the one is {C}.',
                ],
                '(x): ({A} & {B})x -> {C}x': [
                    'If someone is {A} and {B}, then the one is {C}.',
                ],
            }
            predicate_translations = [f'red-{str(i).zfill(2)}' for i in range(30)]
            constant_translations = [f'Alice-{str(i).zfill(2)}' for i in range(30)]
            return SentenceWiseTranslator(
                sentence_translations,
                predicate_translations=predicate_translations,
                constant_translations=constant_translations,
                do_translate_to_nl=do_translate_to_nl,
            )
        else:
            raise ValueError()

    elif type_ == 'clause_typed_translator':
        if from_ == 'config':
            config_json = nested_merge(
                json.load(open('./configs/FLNL/translations/clause_typed.thing.json')),
                json.load(open('./configs/FLNL/translations/clause_typed.thing.sentence_negation.json')),
            )
            return ClauseTypedTranslator(
                config_json,
                EnglishWordBank(),
                do_translate_to_nl=do_translate_to_nl,
            )
        elif from_ == 'minimum':
            raise ValueError()
        else:
            raise ValueError()
    elif type_ == 'iterative_regexp':
        if from_ == 'config':
            raise ValueError()
        elif from_ == 'minimum':
            return IterativeRegexpTranslator()
        else:
            raise ValueError()
    else:
        raise ValueError()


def load_distractor(generator: ProofTreeGenerator) -> FormalLogicDistractor:
    # distractor = build_distractor('unknown_interprands', 1, generator=generator)
    # distractor = build_distractor('negated_hypothesis_tree', 1, generator=generator)
    distractor = build_distractor('fallback.negated_hypothesis_tree.unknown_interprands', 1, generator=generator)
    return distractor


def generate_dataset(dataset: NLProofSDataset,
                     num_dataset: int = 1000) -> None:
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

        # logger.info('\n')
        # logger.info('--------------- stats --------------')
        # logger.info(dict(stats))
        # logger.info('\n' + pformat(stats))

        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')


def test_original():
    translator = load_translator('sentence_wise_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=['./configs/FLNL/arguments/old/syllogistic_corpus-02.json'],

        # the config already includes the complicated and quantified arguments
        complicated_arguments_weight=0.0,
        quantified_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              5,
                              5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_LP_pred_only():
    translator = load_translator('clause_typed_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_only.json',
        ],
        complicated_arguments_weight=0.3,
        quantified_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              5,
                              5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_minimum_PL():
    translator = load_translator('clause_typed_translator', 'config')

    generator = load_proof_tree_generator(
        arguments=[
            Argument(
                [Formula('(x): {A}x -> {B}x'), Formula('{A}{a}')],
                Formula('{B}{a}'),
                id='MPL.modus_ponens',
            ),
            Argument(
                [Formula('(x): {A}x -> {B}x'), Formula('(x): {B}x -> {C}x')],
                Formula('(x): {A}x -> {C}x'),
                id='MPL.syllogism',
            ),

        ],
        complicated_arguments_weight=0.3,
        quantified_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              5,
                              5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_LP_pred_arg():
    translator = load_translator('clause_typed_translator', 'config')

    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',
        ],
        complicated_arguments_weight=0.3,
        quantified_arguments_weight=0.0,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['proof'],
                              'CWA',
                              5,
                              5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_PL_pred_arg():
    translator = load_translator('clause_typed_translator', 'config')
    
    generator = load_proof_tree_generator(
        config_paths=[
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',

            './configs/FLNL/arguments/axioms.with_assumption.json',
        ],
        complicated_arguments_weight=0.3,
        quantified_arguments_weight=0.3,
    )

    distractor = load_distractor(generator)

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline,
                              ['PROOF', 'DISPROOF', 'UNKNOWN'],
                              'OWA',
                              5,
                              5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


if __name__ == '__main__':
    random.seed(0)
    setup_logger(level=logging.DEBUG)

    RAISE_IF_TRANSLATION_NOT_FOUND = False

    # test_LP_pred_only()
    # test_LP_pred_arg()
    # test_minimum_PL()
    test_PL_pred_arg()
