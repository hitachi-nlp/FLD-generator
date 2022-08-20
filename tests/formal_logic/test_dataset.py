import json
import random
from typing import List, Optional
import logging
from pprint import pformat

from formal_logic.formula import Formula
from formal_logic.argument import Argument
from formal_logic.proof_tree_generators import ProofTreeGenerator
from formal_logic.distractors import UnknownFactDistractor
from formal_logic.translators import SentenceWiseTranslator, IterativeRegexpTranslator, ClauseTypedTranslator
from formal_logic.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from formal_logic.datasets import NLProofSDataset
from formal_logic.word_banks import EnglishWordBank
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


RAISE_IF_TRANSLATION_NOT_FOUND = True


def load_proof_tree_generator(arguments: Optional[List[Argument]] = None,
                              config_paths: Optional[List[str]] = None,
                              complicated_arguments_weight=0.3,
                              quantified_arguments_weight=0.1,
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
                    translate_terms=True):
    if type_ == 'sentence_wise_translator':
        if from_ == 'config':
            sentence_translations_config_path = './configs/formal_logic/translations/syllogistic_corpus-02.json'
            sentence_translations = json.load(open(sentence_translations_config_path))
            predicate_translations = [f'red-{str(i).zfill(2)}' for i in range(30)]
            constant_translations = [f'Alice-{str(i).zfill(2)}' for i in range(30)]
            return SentenceWiseTranslator(
                sentence_translations,
                predicate_translations=predicate_translations,
                constant_translations=constant_translations,
                translate_terms=translate_terms,
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
                translate_terms=translate_terms,
            )
        else:
            raise ValueError()

    elif type_ == 'clause_typed_translator':
        if from_ == 'config':
            return ClauseTypedTranslator(
                json.load(open('./configs/formal_logic/translations/clause_typed.thing.json')),
                EnglishWordBank(),
                translate_terms=translate_terms,
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


def generate_dataset(dataset: NLProofSDataset,
                     num_dataset: int = 100) -> None:
    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')
    for nlproof_json, proof_tree, distractors, stats in dataset.generate(num_dataset):

        logger.info('\n')
        logger.info('--------------- tree --------------')

        logger.info('\n')
        logger.info(proof_tree.format_str)

        logger.info('\n')
        logger.info('--------------- distractors --------------')
        logger.info(distractors)

        logger.info('\n')
        logger.info('--------------- NLProofs json --------------')
        logger.info(pformat(nlproof_json))

        logger.info('\n')
        logger.info('--------------- stats --------------')
        # logger.info(dict(stats))
        logger.info(pformat(stats))

        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')


def test_original_pipeline():
    generator = load_proof_tree_generator(
        config_paths=['./configs/formal_logic/arguments/syllogistic_corpus-02.json'],

        # the config already includes the complicated and quantified arguments
        complicated_arguments_weight=0.0,
        quantified_arguments_weight=0.0,
    )

    distractor = UnknownFactDistractor()

    translator = load_translator('sentence_wise_translator', 'config')
    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline, 'CWA',
                              depth=5,
                              num_distractor_factor=2,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_pipeline_with_LP_arguments():
    generator = load_proof_tree_generator(
        config_paths=[
            './configs/formal_logic/arguments/LP.axiom.json',
            './configs/formal_logic/arguments/LP.theorem.json',
        ],
    )

    distractor = UnknownFactDistractor()

    translator = load_translator('clause_typed_translator', 'config')

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline, 'CWA',
                              depth=5,
                              num_distractor_factor=5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_pipeline_with_minumum_PL_arguments():
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

        ]
    )

    distractor = UnknownFactDistractor()

    translator = load_translator('clause_typed_translator', 'config')

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline, 'CWA',
                              depth=5,
                              num_distractor_factor=5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


def test_pipeline_with_PL_arguments():
    generator = load_proof_tree_generator(
        config_paths=[
            './configs/formal_logic/arguments/LP.axiom.json',
            './configs/formal_logic/arguments/LP.theorem.json',

            './configs/formal_logic/arguments/PL_minus_LP.axiom.json',
            './configs/formal_logic/arguments/PL_minus_LP.theorem.json',
        ],
    )

    distractor = UnknownFactDistractor()

    translator = load_translator('clause_typed_translator', 'config')

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline, 'CWA',
                              depth=5,
                              num_distractor_factor=5,
                              raise_if_translation_not_found=RAISE_IF_TRANSLATION_NOT_FOUND)

    generate_dataset(dataset)


if __name__ == '__main__':
    random.seed(0)
    setup_logger(level=logging.INFO)

    RAISE_IF_TRANSLATION_NOT_FOUND = True

    # test_pipeline_with_LP_arguments()
    # test_pipeline_with_minumum_PL_arguments()
    test_pipeline_with_PL_arguments()
