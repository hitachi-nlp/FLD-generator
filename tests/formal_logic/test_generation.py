import json
import random
from typing import Dict, List

from formal_logic import generate_tree, Formula, Argument, load_argument_config
from formal_logic.translators import load_sentence_translation_config, add_translations_to_tree, SentenceTranslator
from logger_setup import setup as setup_logger


def test_simple_generation():
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

    sentence_translations: Dict[str, List[str]] = {
        '(x): {A}x -> {B}x': [
            'Every {A} is a {B}.',
        ],
        '{A}{a}': [
            '{a} is {A}.',
        ],
    }
    translator = SentenceTranslator(sentence_translations)

    for _ in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(arguments, elim_dneg=False, depth=5)
        if proof_tree is not None:
            add_translations_to_tree(proof_tree, translator)
            print(proof_tree.format_str)


def test_generation_from_loaded_config():
    arguments_config_path = './configs/formal_logic/arguments/syllogistic_corpus-02.json'
    arguments = load_argument_config(arguments_config_path)

    sentence_translations_config_path = './configs/formal_logic/sentence_translations/syllogistic_corpus-02.json'
    sentence_translations = load_sentence_translation_config(sentence_translations_config_path)
    translator = SentenceTranslator(sentence_translations['general'])

    for _ in range(100):
        print('=================== generating proof tree =========================')
        proof_tree = generate_tree(arguments, elim_dneg=False, depth=5)
        if proof_tree is not None:
            add_translations_to_tree(proof_tree, translator)
            print(proof_tree.format_str)


if __name__ == '__main__':
    random.seed(0)
    setup_logger()

    test_simple_generation()
    # test_generation_from_loaded_config()
