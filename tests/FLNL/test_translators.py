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
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
            './configs/FLNL/translations/clause_typed.EB_task1_train.json',
        ],
        build_wordnet_wordbank('eng'),
        reuse_object_nouns=True,
    )

    def show_translations(formulas: List[Formula], trial: int) -> None:
        print('\n\n\n================   translate  ================')
        for i_trial in range(0, trial):
            print()
            print(f'---------- trial={trial} ----------')
            translations, _ = translator.translate(formulas)
            for formula, (_, translation) in zip(formulas, translations):
                print(formula, '  ->  ', translation)

    # show_translations(
    #     [
    #         Formula('{A}'),
    #         Formula('{B}'),
    #         Formula('{C}'),
    #     ],
    #     5
    # )

    # show_translations(
    #     [
    #         Formula('{A}{a}'),
    #         Formula('{B}{b}'),
    #         Formula('{C}{c}'),
    #     ],
    #     5
    # )

    # show_translations(
    #     [
    #         Formula('{A}{a} -> {B}{b}'),
    #         Formula('{B}{b} -> {C}{c}'),
    #         Formula('{C}{c} -> {D}{d}'),
    #     ],
    #     5
    # )

    # show_translations(
    #     [
    #         Formula('{A}'),
    #         Formula('{B}'),
    #         Formula('{C}'),
    #         Formula('{D}{d}'),
    #         Formula('{E}{e}'),
    #         Formula('{F}{f}'),
    #     ],
    #     5,
    # )

    show_translations(
        [
            Formula('(x): {A}x -> {B}x'),
            Formula('(x): {B}x -> {C}x'),
            Formula('(x): {C}x -> {D}x'),
        ],
        100
    )


if __name__ == '__main__':
    test_clause_typed_translator()
