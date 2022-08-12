import json
import random
from typing import Dict, List
import logging
from pprint import pprint, pformat

from formal_logic.formula import Formula
from formal_logic.argument import Argument
from formal_logic.proof import ProofTree, ProofNode
from formal_logic.generators import FormalLogicGenerator
from formal_logic.distractors import FormalLogicDistractor, UnknownFactDistractor
from formal_logic.translators import Translator, SentenceWiseTranslator, IterativeRegexpTranslator, ClauseTypedTranslator
from formal_logic.tree_pipeline import TreePipeline
from formal_logic.dataset import NLProofSDataset
from formal_logic.word_banks import EnglishWordBank
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def load_translator(type_: str, from_: str, translate_terms=True):
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


def test_simple_pipeline():
    arguments = [
        # Argument(
        #     [Formula('{A} -> {B}'), Formula('{A}')],
        #     Formula('{B}'),
        #     id='LP.modus_ponens',
        # ),
        # Argument(
        #     [Formula('{A} -> {B}'), Formula('{B} -> {C}')],
        #     Formula('{A} -> {C}'),
        #     id='LP.syllogism',
        # ),

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
    generator = FormalLogicGenerator(arguments, elim_dneg=False, allow_complication=True)

    distractor = UnknownFactDistractor()

    translator = load_translator('clause_typed_translator', 'config')

    tree_pipeline = TreePipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(tree_pipeline, 'CWA',
                              depth=5, num_distractors=5,
                              raise_if_translation_not_found=False)

    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')
    for nlproof_json, proof_tree, distractors, stats in dataset.generate(1000):

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


def test_pipeline_from_config():
    arguments_config_path = './configs/formal_logic/arguments/syllogistic_corpus-02.json'
    arguments = [Argument.from_json(json_obj) for json_obj in json.load(open(arguments_config_path))]
    generator = FormalLogicGenerator(
        arguments,
        elim_dneg=False,
        allow_complication=False,  # the config already includes the complicated formulas
    )

    distractor = UnknownFactDistractor()

    translator = load_translator('sentence_wise_translator', 'config')
    tree_pipeline = TreePipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(tree_pipeline, 'CWA',
                              depth=5, num_distractors=5,
                              raise_if_translation_not_found=False)

    logger.info('\n\n')
    logger.info('=================== generating proof tree =========================')

    for nlproof_json, proof_tree, distractors, stats in dataset.generate(1000):
        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')

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
        logger.info(pformat(stats))

        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')


if __name__ == '__main__':
    random.seed(0)
    # setup_logger(level=logging.WARNING)
    setup_logger(level=logging.INFO)

    test_simple_pipeline()
    # test_pipeline_from_config()
