from typing import Optional, Iterable, List, Dict, Iterable
import re
import logging
from string import ascii_uppercase
from functools import lru_cache

from lemminflect import getInflection, getLemma

from FLD_generator.word_banks.base import WordBank, POS, VerbForm, AdjForm, NounForm
from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import wordnet as wn
from FLD_generator.utils import starts_with_vowel_sound
from .base import WordNetWordBank

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1000000)
def _getLemma(word: str) -> str:
    # TODO: pos other than VERB
    return getLemma(word, upos='VERB')[0]


class EnglishWordBank(WordNetWordBank):

    language = 'eng'

    _verb_inflation_mapping = {
        VerbForm.NORMAL: 'VB',
        VerbForm.ING: 'VBG',
        VerbForm.S: 'VBZ',
    }

    __intermediate_constant_words  = [
        f'THING-{alphabet}'
        for alphabet in ascii_uppercase
    ]

    def __init__(self,
                 transitive_verbs: Optional[Iterable[str]] = None,
                 intransitive_verbs: Optional[Iterable[str]] = None,
                 vocab_restrictions: Optional[Dict[POS, Iterable[str]]] = None):
        super().__init__(vocab_restrictions=vocab_restrictions)

        self._transitive_verbs = set(verb.lower() for verb in transitive_verbs) if transitive_verbs is not None else None
        self._intransitive_verbs = set(verb.lower() for verb in intransitive_verbs) if intransitive_verbs is not None else None

    @property
    def _intermediate_constant_words(self) -> List[str]:
        return self.__intermediate_constant_words

    @profile
    def get_lemma(self, word: str) -> str:
        return _getLemma(word)

    def _change_verb_form(self, verb: str, form: VerbForm, force=False) -> List[str]:
        if form in [VerbForm.NORMAL, VerbForm.ING, VerbForm.S]:
            if verb in ['am', 'are', 'is', 'was', 'were']:
                logger.warning('Changing verb form for be-verb "{%s}" is subtle. Thus, we do not change it\'s form.', verb)
                return [verb]
            else:
                verb = self.get_lemma(verb)

            results = getInflection(verb, tag=self._verb_inflation_mapping[form])

            if results is not None:
                return [results[0]]
            else:
                if form == VerbForm.NORMAL:
                    # watch
                    inflated_verb = verb
                elif form == VerbForm.ING:
                    # [現在分詞](https://www2.kaiyodai.ac.jp/~takagi/econ/kougo82.htm)
                    if re.match('.*[^aeiou]e$', verb):
                        # date -> dating
                        inflated_verb = verb[:-1] + 'ing'
                    elif re.match('.*[^aeiou][aeiou][^aeiou]$', verb):
                        # sit -> sitting
                        inflated_verb = verb + verb[-1] + 'ing'
                    else:
                        inflated_verb = verb + 'ing'
                elif form == VerbForm.S:
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
        elif form == VerbForm.ANTI:
            antonyms = self.get_antonyms(verb)
            if len(antonyms) == 0 and force:
                raise NotImplementedError()
            return antonyms
        else:
            raise ValueError()


    def _change_adj_form(self, adj: str, form: AdjForm, force=False) -> List[str]:
        if form == AdjForm.NORMAL:
            return [adj]

        elif form == AdjForm.NESS:
            if adj.endswith('y'):
                # peaky -> peakiness
                ness_adj = adj[:-1] + 'iness'
            else:
                ness_adj = adj + 'ness'
            if force or ness_adj in self._cached_word_set:
                return [ness_adj]
            else:
                return []

        elif form == AdjForm.ANTI:
            antonyms = self.get_antonyms(adj)
            antonyms += self._change_adj_form(adj, AdjForm.NEG)
            if len(antonyms) == 0 and force:
                return self._change_adj_form(adj, AdjForm.NEG, force=True)
            return antonyms

        elif form == AdjForm.NEG:
            negnyms = self.get_negnyms(adj)
            if len(negnyms) == 0 and force:
                return [f'non-{adj}']
            return negnyms

        else:
            raise ValueError(f'Unknown form {form}')

    def _change_noun_form(self, noun: str, form: NounForm, force=False) -> List[str]:
        if form == NounForm.NORMAL:
            return [noun]

        elif form == NounForm.SINGULAR:
            return [noun]

        elif form == NounForm.SINGULAR_WITH_PARTICLE:
            """
            We assume that all the words are countable, thus, all the words in singular form need an indefinite particle, i.e., "a" or "an".
            This approximation is because that detecting the word countability is a challenging problem.
            See [here](https://stackoverflow.com/questions/7822922/noun-countability) for example.

            For detecting "a" vs "an", we borrowed implementation from https://stackoverflow.com/questions/20336524/verify-correct-use-of-a-and-an-in-english-texts-python .

            TODO: We might be able to detect the countability
                  using existent resources like [Category:Uncountable nouns - Simple English Wiktionary](https://simple.wiktionary.org/wiki/Category:Uncountable_nouns).
            """

            return [f'an {noun}' if starts_with_vowel_sound(noun) else f'a {noun}']

        elif form == NounForm.PLURAL:
            raise NotImplementedError()

        elif form == NounForm.ANTI:
            antonyms = self.get_antonyms(noun)
            antonyms += self._change_noun_form(noun, NounForm.NEG)
            if len(antonyms) == 0 and force:
                return self._change_noun_form(noun, NounForm.NEG, force=True)
            return antonyms

        elif form == NounForm.NEG:
            negnyms = self.get_negnyms(noun)
            if len(negnyms) == 0 and force:
                return [f'non-{noun}']
            return negnyms

        else:
            raise ValueError(f'Unknown form {form}')

    def _can_be_transitive_verb_synset(self, syn: Synset) -> bool:
        if self._can_be_intransitive_verb is None:
            raise ValueError('Set transitive verb list')
        lemma = self._get_lemma(syn)
        return lemma is not None and lemma.name().lower() in self._transitive_verbs

    def _can_be_intransitive_verb_synset(self, syn: Synset) -> bool:
        if self._intransitive_verbs is None:
            raise ValueError('Set intransitive verb list')

        lemma = self._get_lemma(syn)
        return lemma is not None and lemma.name().lower() in self._intransitive_verbs

    def get_negnyms(self, word) -> List[str]:
        # See [here](https://langsquare.exblog.jp/28548624/) for the following detection rules.
        negnyms = []
        negation_prefixes = ['in', 'im', 'il', 'ir', 'un', 'dis', 'non']
        negation_postfixes = ['less']

        for antonym in self.get_antonyms(word):
            if any([antonym == f'{prefix}{word}' for prefix in negation_prefixes])\
                    or any([antonym == f'{word}{postfix}' for postfix in negation_postfixes]):
                negnyms.append(antonym)

            if any((word.startswith(prefix) and word.lstrip(prefix) in self._cached_word_set
                    for prefix in negation_prefixes))\
                    or any((word.endswith(postfix) and word.rstrip(postfix) in self._cached_word_set
                            for postfix in negation_postfixes)):
                negnyms.append(antonym)
        return negnyms
