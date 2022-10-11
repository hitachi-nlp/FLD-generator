from typing import List
from FLNL.formula import Formula
from FLNL.translators import build as build_translator
from FLNL.word_banks import build_wordnet_wordbank
from logger_setup import setup as setup_logger


def test_clause_typed_translator():
    setup_logger()

    translator = build_translator(
        [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json'
        ],
        build_wordnet_wordbank('eng')
    )

    def show_translations(formulas: List[Formula]) -> None:
        print('\n========== translate ==========')
        translations, _ = translator.translate(formulas)
        for formula, (_, translation) in zip(formulas, translations):
            print(formula, '  ->  ', translation)

    for i in range(0, 5):
        show_translations([
            Formula('{A}{a}'),
            Formula('{B}{b}'),
            Formula('{C}{c}'),
        ])

    for i in range(0, 5):
        show_translations([
            Formula('{A}{a} -> {B}{b}'),
            Formula('{B}{b} -> {C}{c}'),
            Formula('{C}{c} -> {D}{d}'),
        ])


if __name__ == '__main__':
    test_clause_typed_translator()
