# FLD Generator
This repository includes the code for generating the FLD corpus.  

See [the entry-point repository](https://github.com/hitachi-nlp/FLD.git) about the whole FLD project.

## About this release
* This is version 2.0 of FLD corpora. See [the Appendix.H of our paper](https://arxiv.org/abs/2308.07336) for details.

## Installation
The code has been tested on Python 3.7.7.
```console
$ pip install -r ./requirements/requrements.txt
$ export PYTHONPATH=`pwd -P`:$PYTHONPATH
```

## Additional Resources Required

### Japanese FLD
```console
./download_scripts/00.download_JFLD_resources.sh
```
### Knowledge FLD
```console
./download_scripts/00.download_knowledge_banks.sh
```

### For Japanese
Additionally:
```console
git clone https://github.com/taku910/mecab/ ./res/word_banks/japanese/mecab/
```

## How to generate FLD corpus
Use `./create_corpus.py`, which generates a corpus with the design specified by the option values.

We can create **FLD** (FLD.3) by running the follows command:
```console
$ python ./create_corpus.py\
    <output_dir>\
    <dataset_size>\
    --depth-range '[1, 3]'\
    --depth-distrib flat\
    --branch-extensions-range '[0, 5]'\
    --argument-config ./configs/arguments/axioms/\
    --complex-formula-arguments-weight 0.5\
    --quantifier-axiom-arguments-weight 0.2\
    --quantifier-axiom universal_quantifier_elim\
    --quantifier-axiom universal_quantifier_intro\
    --quantifier-axiom existential_quantifier_intro\
    --quantifier-axiom existential_quantifier_elim\
    --translation-config ./configs/translations/thing.v1/\
    --distractor "mixture(negative_tree_double.simplified_formula.various_form)"\
    --distractors-range '[0, 20]'\
    --num-workers 5\
    --seed 0
```

We can create **FLD★** (FLD.4) by running the follows command:
```console
$ python ./create_corpus.py\
    <output_dir>\
    <dataset_size>\
    --depth-range '[1, 8]'\
    --depth-distrib flat\
    --branch-extensions-range '[0, 5]'\
    --argument-config ./configs/arguments/axioms/\
    --complex-formula-arguments-weight 0.5\
    --quantifier-axiom-arguments-weight 0.2\
    --quantifier-axiom universal_quantifier_elim\
    --quantifier-axiom universal_quantifier_intro\
    --quantifier-axiom existential_quantifier_intro\
    --quantifier-axiom existential_quantifier_elim\
    --translation-config ./configs/translations/thing.v1/\
    --distractor "mixture(negative_tree_double.simplified_formula.various_form)"\
    --distractors-range '[0, 20]'\
    --num-workers 5\
    --seed 0
```
