import re
from typing import Optional, Iterable, List, Dict, Set, Tuple
import logging
from enum import Enum
from typing import Optional

from ordered_set import OrderedSet
from lemminflect import getInflection
from FLD_generator.word_banks.base import WordBank, POS, UserWord
from FLD_generator.utils import starts_with_vowel_sound
from FLD_generator.person_names import get_person_names
from FLD_generator.word_banks.word_utils import WordUtil

logger = logging.getLogger(__name__)


BE_VERBS = [
    'am', 'was',
    'are', 'were',
    'is', 'was',
]

MODAL_VERBS = [
    'do', 'does', 'did',
    'can', 'could',
    'may', 'might',
    'must',
    'shall', 'should',
    'will', 'would',
]

PARTICLES = [
    'a', 'an',
    'the',
]


def strip_negation(rep: str) -> Tuple[str, bool]:
    rep_org = rep
    for verb in BE_VERBS + MODAL_VERBS:
        if verb in ['do', 'does', 'did']:
            tgt = ''
        else:
            tgt = verb
        rep = rep.replace(f'{verb} not', tgt)
        rep = rep.replace(f'{verb} n\'t', tgt)
        rep = rep.replace(f'{verb}n\'t', tgt)

    # special cases
    rep = rep.replace('can\'t', 'can')
    rep = rep.replace('shan\'t', 'can')

    return rep, rep != rep_org


class EnglishWordBank(WordBank):

    class VerbForm(Enum):
        """ https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html """
        NORMAL = 'normal'
        ING = 'ing'
        S = 's'

        ANTI = 'anti'

    class AdjForm(Enum):
        NORMAL = 'normal'
        NESS = 'ness'

        ANTI = 'anti'
        NEG = 'neg'

    class PresentForm(Enum):
        NORMAL = 'normal'

    class PastForm(Enum):
        NORMAL = 'normal'

    class NounForm(Enum):
        NORMAL = 'normal'
        SINGULAR = 's'
        SINGULAR_WITH_PARTICLE = 'swa'
        PLURAL = 'p'   # not implemented

        ANTI = 'anti'
        NEG = 'neg'

    # INTERMEDIATE_CONSTANT_PREFIXES = [
    #     'THING',
    #     'PERSON',
    # ]

    def __init__(self,
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 extra_vocab: Optional[List[UserWord]] = None):
        super().__init__(extra_vocab=extra_vocab)
        self._person_names: OrderedSet[str] = OrderedSet(get_person_names(country='US'))

        self._word_util = WordUtil(
            'eng',
            transitive_verbs=transitive_verbs,
            intransitive_verbs=intransitive_verbs,
            extra_vocab=extra_vocab,
        )

        self._verb_inflation_mapping = {
            self.VerbForm.NORMAL: 'VB',
            self.VerbForm.ING: 'VBG',
            self.VerbForm.S: 'VBZ',
        }

    def _get_all_lemmas(self) -> Iterable[str]:
        return sorted(self._word_util.get_all_lemmas()) + list(self._person_names)

    def _get_pos(self, word: str) -> List[POS]:
        if word in self._person_names:
            return [POS.NOUN]

        return self._word_util.get_pos(word)

    def _change_verb_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.VerbForm.NORMAL, self.VerbForm.ING, self.VerbForm.S]:
            if verb in BE_VERBS:
                logger.warning('Changing verb form for be-verb "{%s}" is subtle. Thus, we do not change it\'s form.', verb)
                return [verb]
            else:
                verb = self._word_util.get_lemma(verb)

            results = getInflection(verb, tag=self._verb_inflation_mapping[form])

            if results is not None:
                return [results[0]]

            else:

                if form == self.VerbForm.NORMAL:
                    # watch
                    inflated_verb = verb

                elif form == self.VerbForm.ING:
                    # [現在分詞](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo82.htm)
                    if re.match('.*[^aeiou]e$', verb):
                        # date -> dating
                        inflated_verb = verb[:-1] + 'ing'
                    elif re.match('.*[^aeiou][aeiou][^aeiou]$', verb):
                        # sit -> sitting
                        inflated_verb = verb + verb[-1] + 'ing'
                    else:
                        inflated_verb = verb + 'ing'

                elif form == self.VerbForm.S:
                    # [３単現及び名詞の複数形の -s, -es](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo52.htm)
                    if re.match('.*(s|sh|ch|x|o)$', verb):
                        # wash -> washes
                        inflated_verb = verb + 'es'
                    elif re.match(r'.*[^aeiou]y$', verb):
                        # study -> studies
                        inflated_verb = verb[:-1] + 'ies'
                    else:
                        inflated_verb = verb + 's'

                else:
                    raise NotImplementedError()

                return [inflated_verb]

        elif form == self.VerbForm.ANTI:
            antonyms = self._get_antonyms(verb)

            if len(antonyms) == 0 and force:
                raise NotImplementedError()

            return antonyms

        else:
            raise ValueError()

    def _change_adj_form(self, adj: str, form: Enum, force=False) -> List[str]:

        if form == self.AdjForm.NORMAL:
            return [adj]

        elif form == self.AdjForm.NESS:
            ness_adjs: List[str] = []

            if adj.endswith('y'):
                # peaky -> peakiness
                ness_adj = adj[:-1] + 'iness'
            else:
                ness_adj = adj + 'ness'
            if ness_adj in self._word_util.get_all_lemmas():
                ness_adjs.append(ness_adj)

            if len(ness_adjs) == 0 and force:
                ness_adjs.append(ness_adj)

            return ness_adjs

        elif form == self.AdjForm.ANTI:
            antonyms = self._get_antonyms(adj)
            antonyms += [
                word
                for word in self._change_adj_form(adj, self.AdjForm.NEG, force=False)
                if word not in antonyms]

            if len(antonyms) == 0 and force:
                antonyms += self._change_adj_form(adj, self.AdjForm.NEG, force=True)

            return antonyms

        elif form == self.AdjForm.NEG:
            negnyms = self._get_negnyms(adj)

            if len(negnyms) == 0 and force:
                return [f'non-{adj}']

            return negnyms

        else:
            raise ValueError(f'Unknown form {form}')

    def _change_present_particle_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.PresentForm.NORMAL]:
            return [verb]
        else:
            raise ValueError()

    def _change_past_particle_form(self, verb: str, form: Enum, force=False) -> List[str]:

        if form in [self.PastForm.NORMAL]:
            return [verb]
        else:
            raise ValueError()

    def _change_noun_form(self, noun: str, form: Enum, force=False) -> List[str]:

        if form == self.NounForm.NORMAL:
            if noun in self._person_names:
                return [noun]

            return [noun]

        elif form == self.NounForm.SINGULAR:
            if noun in self._person_names:
                return [noun]

            return [noun]

        elif form == self.NounForm.SINGULAR_WITH_PARTICLE:
            """
            We assume that all the words are countable, thus, all the words in singular form need an indefinite particle, i.e., "a" or "an".
            This approximation is because that detecting the word countability is a challenging problem.
            See [here](https://stackoverflow.com/questions/7822922/noun-countability) for example.

            For detecting "a" vs "an", we borrowed implementation from https://stackoverflow.com/questions/20336524/verify-correct-use-of-a-and-an-in-english-texts-python .

            TODO: We might be able to detect the countability
                  using existent resources like [Category:Uncountable nouns - Simple English Wiktionary](https://simple.wiktionary.org/wiki/Category:Uncountable_nouns).
            """
            if noun in self._person_names:
                return [noun]

            return [f'an {noun}' if starts_with_vowel_sound(noun) else f'a {noun}']

        elif form == self.NounForm.PLURAL:
            raise NotImplementedError()

        elif form == self.NounForm.ANTI:
            if noun in self._person_names:
                return []

            antonyms = self._get_antonyms(noun)
            antonyms += [word for word in self._change_noun_form(noun, self.NounForm.NEG, force=False)
                         if word not in antonyms]

            if len(antonyms) == 0 and force:
                return self._change_noun_form(noun, self.NounForm.NEG, force=True)

            return antonyms

        elif form == self.NounForm.NEG:
            if noun in self._person_names:
                return []

            negnyms = self._get_negnyms(noun)
            if len(negnyms) == 0 and force:
                return [f'non-{noun}']

            return negnyms

        else:
            raise ValueError(f'Unknown form {form}')

    def _can_be_intransitive_verb(self, verb: str) -> bool:
        return self._word_util.can_be_intransitive_verb(verb)

    def _can_be_transitive_verb(self, verb: str) -> bool:
        return self._word_util.can_be_transitive_verb(verb)

    def _can_be_event_noun(self, noun: str) -> bool:
        if noun in self._person_names:
            return False
        return self._word_util.can_be_event_noun(noun)

    def _can_be_entity_noun(self, noun: str) -> bool:
        if noun in self._person_names:
            return True
        return self._word_util.can_be_entity_noun(noun)

    def _can_be_predicate_noun(self, noun: str) -> bool:
        return not self._can_be_entity_noun(noun) and not self._can_be_event_noun(noun)

    def _get_antonyms(self, word: str) -> List[str]:
        return self._word_util.get_antonyms(word)

    def _get_negnyms(self, word) -> List[str]:
        # See [here](https://langsquare.exblog.jp/28548624/) for the following detection rules.
        negnyms = []
        negation_prefixes = ['in', 'im', 'il', 'ir', 'un', 'dis', 'non']
        negation_postfixes = ['less']

        for antonym in self._get_antonyms(word):
            if any([antonym == f'{prefix}{word}' for prefix in negation_prefixes])\
                    or any([antonym == f'{word}{postfix}' for postfix in negation_postfixes]):
                negnyms.append(antonym)

            if any((word.startswith(prefix) and word.lstrip(prefix) in self._word_util.get_all_lemmas()
                    for prefix in negation_prefixes))\
                    or any((word.endswith(postfix) and word.rstrip(postfix) in self._word_util.get_all_lemmas()
                            for postfix in negation_postfixes)):
                negnyms.append(antonym)
        return negnyms
