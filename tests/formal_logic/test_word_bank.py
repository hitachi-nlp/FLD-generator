from formal_logic.word_banks import EnglishWordBank, POS, VerbForm, AdjForm
import logging

from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)

wb = EnglishWordBank()

for word in wb.get_words(pos=POS.VERB):
    print()
    print(f'============ verb: {word}   is_intransitive: {wb.can_be_intransitive_verb(word)} =============')
    for form in VerbForm:
        print(form, wb.change_verb_form(word, form))

for word in wb.get_words(pos=POS.NOUN):
    print('noun:', word)


cnt = 0
for word in wb.get_words(pos=POS.NOUN):
    if wb.can_be_event_noun(word):
        cnt += 1
        print(f'event noun ({cnt}):', word)


cnt = 0
for word in wb.get_words(pos=POS.NOUN):
    if wb.can_be_entity_noun(word):
        cnt += 1
        print(f'entity noun ({cnt}):', word)


for word in wb.get_words(pos=POS.ADJ):
    print()
    print(f'============ adj: {word} =============')
    for form in AdjForm:
        print(form, wb.change_adj_form(word, form))

