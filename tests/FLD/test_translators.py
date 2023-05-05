from typing import List, Optional
import logging

from FLD.formula import Formula
from FLD.translators import build as build_translator
from FLD.word_banks import build_wordnet_wordbank
from logger_setup import setup as setup_logger


def test_templated_translator():
    setup_logger(level=logging.DEBUG)

    translator = build_translator(
        [
            './configs/translations/thing.json',
            './configs/translations/thing.sentence_negation.json',
        ],
        build_wordnet_wordbank('eng'),
        use_fixed_translation=False,
        reused_object_nouns_max_factor=1.0,

        # volume_to_weight='linear',
        volume_to_weight='sqrt',
        # volume_to_weight='pow-0.7',
        # volume_to_weight='pow-0.7',
        # volume_to_weight='inv_linear',
    )

    def show_translations(formulas: List[Formula],
                          trial: int,
                          intermediate_constant_formulas: Optional[List[Formula]] = None) -> None:
        print('\n\n\n================   translate  ================')
        for i_trial in range(0, trial):
            print()
            print(f'---------- trial={i_trial} ----------')
            translations, _ = translator.translate(formulas, intermediate_constant_formulas or [])
            for formula, (_, translation, _) in zip(formulas, translations):
                print(formula, f'with intermediate {intermediate_constant_formulas}', '  ->  ', translation)

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

    show_translations(
        [
            Formula('{A}{a} -> {B}{b}'),
            Formula('{C}{c} -> {D}{d}'),
            Formula('{F}{f} -> {G}{g}'),
        ],
        100,
        intermediate_constant_formulas=[Formula('{a}'), Formula('{d}')],
    )


if __name__ == '__main__':
    test_templated_translator()
