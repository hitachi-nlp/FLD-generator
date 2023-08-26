import re
import random
import logging

from FLD_generator.formula import Formula
from FLD_generator.utils import starts_with_vowel_sound
from FLD_generator.word_banks import POS
from .templated import TemplatedTranslator

import line_profiling


logger = logging.getLogger(__name__)


class EnglishTranslator(TemplatedTranslator):

    def _postprocess_template(self, template: str) -> str:
        return self._replace_following_constants_with_the_or_it(template)

    def _make_pred_with_obj_transl(self, translation: str) -> str:
        return translation.replace('__O__', ' ')

    def _postprocess_translation(self, translation: str) -> str:
        translation = self._correct_indefinite_particles(translation)
        translation = self._fix_pred_singularity(translation)
        translation = self._reduce_degenerate_blanks(translation)
        translation = self._uppercase_beggining(translation)
        translation = self._add_ending_period(translation)
        return translation

    @profile
    def _replace_following_constants_with_the_or_it(self, sentence_with_templates: str) -> str:
        constants = [c.rep for c in Formula(sentence_with_templates).constants]

        with_definite = sentence_with_templates
        for constant in constants:
            if with_definite.count(constant) < 2:
                continue

            first_pos = with_definite.find(constant)

            until_first = with_definite[:first_pos + len(constant)]
            from_second = with_definite[first_pos + len(constant):]

            if re.match(f'.*a {constant} is.*', from_second):
                replace_with_it = random.random() >= 0.5
            else:
                replace_with_it = False

            if replace_with_it:
                from_second_with_definite = re.sub(
                    f'a {constant} is',
                    'it is',
                    from_second,
                )
            else:
                from_second_with_definite = re.sub(
                    f'(.*)a (.*){constant}',
                    f'\g<1>the \g<2>{constant}',
                    from_second,
                )
            with_definite = until_first + from_second_with_definite
        if sentence_with_templates != with_definite:
            logger.info('particles "a (...) %s" are modified as:    "%s"    ->    "%s"',
                        constant,
                        sentence_with_templates,
                        with_definite)
        return with_definite

    @profile
    def _correct_indefinite_particles(self, sentence_wo_templates: str) -> str:
        """ choose an appropriate indefinite particls, i.e., "a" or "an", depending on the word pronounciation """
        words = sentence_wo_templates.split(' ')
        corrected_words = []
        for i_word, word in enumerate(words):
            if word.lower() in ['a', 'an']:
                if len(words) >= i_word + 2:
                    next_word = words[i_word + 1]
                    if starts_with_vowel_sound(next_word):
                        corrected_words.append('an')
                    else:
                        corrected_words.append('a')
                else:
                    logger.warning('Sentence might end with particle: "%s"', sentence_wo_templates)
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        corrected_sentence = ' '.join(corrected_words)
        return corrected_sentence

    def _fix_pred_singularity(self, translation: str) -> str:
        # TODO: A and B {is, runs} => currently, we do not have ({A}{a} and {B}{a}) so that we do not this fix.
        translation_fixed = translation

        def fix_all_thing_is(translation: str, src_pred: str, dst_pred: str) -> str:
            if re.match(f'.*all .*things? {src_pred}.*', translation):
                translation_fixed = re.sub(f'(.*)all (.*)things? {src_pred}(.*)', '\g<1>all \g<2>things ' + dst_pred + '\g<3>', translation)
                return translation_fixed
            else:
                return translation

        translation_fixed = fix_all_thing_is(translation_fixed, 'is an', 'are')
        translation_fixed = fix_all_thing_is(translation_fixed, 'is a', 'are')
        translation_fixed = fix_all_thing_is(translation_fixed, 'is', 'are')

        translation_fixed = fix_all_thing_is(translation_fixed, 'was an', 'were')
        translation_fixed = fix_all_thing_is(translation_fixed, 'was a', 'were')
        translation_fixed = fix_all_thing_is(translation_fixed, 'was', 'wer')

        translation_fixed = fix_all_thing_is(translation_fixed, 'does', 'do')

        # all kind thing squashes apple -> all kind thing squash apple
        if re.match('(.*)all (.*)things? ([^ ]*)(.*)', translation_fixed):
            word_after_things = re.sub('(.*)all (.*)things? ([^ ]*)(.*)', '\g<3>', translation_fixed)
            if POS.VERB in self._word_bank.get_pos(word_after_things):
                verb_normal = self._word_bank.change_word_form(word_after_things, POS.VERB, 'normal')[0]
                translation_fixed = re.sub('(.*)all (.*)things? ([^ ]*)(.*)', '\g<1>all \g<2>things ' + verb_normal + '\g<4>', translation_fixed)

        # target   : A and B causes C -> A and B cause C
        # negagive : A runs and it is also kind
        # def fix_A_and_B_is(translation: str, src_pred: str, dst_pred: str) -> str:
        #     if re.match(f'.*[^ ]* and [^ ]* {src_pred}.*', translation):
        #         translation_fixed = re.sub('.*([^ ]*) and ([^ ]*) {src_pred}(.*)', '\g<1>all \g<2>things ' + dst_pred + '\g<3>', translation)
        #         return translation_fixed
        #     else:
        #         return translation

        if translation_fixed != translation:
            logger.info('translation is fixed as:\norig : "%s"\nfixed: "%s"', translation, translation_fixed)

        return translation_fixed

    def _reduce_degenerate_blanks(self, translation: str) -> str:
        return re.sub(r'\s+', ' ', translation).strip(' ')

    def _uppercase_beggining(self, translation: str) -> str:
        return translation[0].upper() + translation[1:]

    def _add_ending_period(self, translation: str) -> str:
        return translation + '.'
