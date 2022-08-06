from formal_logic.word_banks import EnglishWordBank
import logging

from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)

wb = EnglishWordBank()

for word in wb.get_words(pos=EnglishWordBank.VERB):
    print()
    print(f'============ {word} =============')
    print('is_intransitive:', wb.can_be_intransitive_verb(word))
    for form in ['VB', 'VBG', 'VBZ']:
        print(form, wb.change_verb_form(word, form))

# for word in wb.get_words(pos=EnglishWordBank.NOUN):
#     print('noun:', word)
# 
# for word in wb.get_words(pos=EnglishWordBank.ADJ):
#     print('adj :', word)