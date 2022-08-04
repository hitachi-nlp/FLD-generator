from formal_logic.word_banks import EnglishWordBank


wb = EnglishWordBank()

for word in wb.get_words(pos=EnglishWordBank.VERB):
    if wb.can_be_intransitive_verb(word):
        print('verb (intransitive):', word)
    else:
        print('verb   (transitive):', word)
    print('        continuous form:', wb.change_verb_form(word, 'VBG'))

for word in wb.get_words(pos=EnglishWordBank.NOUN):
    print('noun:', word)

for word in wb.get_words(pos=EnglishWordBank.ADJ):
    print('adj :', word)
