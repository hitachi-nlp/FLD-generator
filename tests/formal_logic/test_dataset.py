import json
import random
from typing import Dict, List
import logging
from pprint import pprint

from formal_logic.formula import Formula
from formal_logic.argument import Argument
from formal_logic.proof import ProofTree, ProofNode
from formal_logic.generators import FormalLogicGenerator
from formal_logic.distractors import FormalLogicDistractor, UnknownFactDistractor
from formal_logic.translators import Translator, SentenceWiseTranslator, IterativeRegexpTranslator
from formal_logic.tree_pipeline import TreePipeline
from formal_logic.dataset import NLProofSDataset
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def test_simple_pipeline():
    arguments = [
        Argument(
            [Formula('(x): {F}x -> {G}x'), Formula('{F}{a}')],
            Formula('{G}{a}'),
            id='modus ponens',
        ),
        Argument(
            [Formula('(x): {F}x -> {G}x'), Formula('(x): {G}x -> {H}x')],
            Formula('(x): {F}x -> {H}x'),
            id='syllogism',
        ),

    ]
    generator = FormalLogicGenerator(arguments, elim_dneg=False, allow_complication=True)

    distractor = UnknownFactDistractor()

    sentence_translations: Dict[str, List[str]] = {
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
    translator = SentenceWiseTranslator(sentence_translations)
    # translator = IterativeRegexpTranslator()

    tree_pipeline = TreePipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(tree_pipeline, 'CWA',
                              depth=5, num_distractors=5)

    for nlproof_json, proof_tree, distractors in dataset.generate(100):
        print('\n\n\n=================== generating proof tree =========================')
        print('\n--------------- tree --------------')
        print(proof_tree.format_str)
        print('\n--------------- distractors --------------')
        print(distractors)
        print('\n--------------- NLProofs json --------------')
        pprint(nlproof_json)


def test_pipeline_from_config():
    arguments_config_path = './configs/formal_logic/arguments/syllogistic_corpus-02.json'
    arguments = [Argument.from_json(json_obj) for json_obj in json.load(open(arguments_config_path))]
    generator = FormalLogicGenerator(
        arguments,
        elim_dneg=False,
        allow_complication=False,  # the config already includes the complicated formulas
    )

    distractor = UnknownFactDistractor()

    sentence_translations_config_path = './configs/formal_logic/sentence_translations/syllogistic_corpus-02.json'
    sentence_translations = json.load(open(sentence_translations_config_path))
    translator = SentenceWiseTranslator(sentence_translations)

    tree_pipeline = TreePipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(tree_pipeline, 'CWA',
                              depth=5, num_distractors=5)

    for nlproof_json, proof_tree, distractors in dataset.generate(100):
        print('\n\n\n=================== generating proof tree =========================')
        print('\n--------------- tree --------------')
        print(proof_tree.format_str)
        print('\n--------------- distractors --------------')
        print(distractors)
        print('\n--------------- NLProofs json --------------')
        pprint(nlproof_json)


if __name__ == '__main__':
    random.seed(0)
    setup_logger()

    test_simple_pipeline()
    # test_pipeline_from_config()
