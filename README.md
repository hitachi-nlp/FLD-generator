# FLD Generator
![framework_overview](./images/framework_overview.PNG)

This repository includes the code for generating the FLD corpus.  

See [the entry-point repository](https://github.com/hitachi-nlp/FLD.git) about the whole FLD project.




## Releases (READ CAREFULLY to determine which branch suits you)
* **`NLP_2024_KOBE_BEEF`** branch (2024-01-24) 
    - Release at LREC-COLING 2024 and 言語処理学会 2024.
    - **Now capable of generating Japanese corpora (JFLD).**
    - Slight changes in the corpus schema.
    - **This branch and the generated corpora might not be compatible with older branches of related repositories.**
* **`main`** branch (2023-08-22)
    - Initial release at ICML 2023.
    - This is version 2.0 of FLD corpora. See the Appendix H of [our paper](https://arxiv.org/abs/2308.07336) for details.

## Installation
The code has been tested on Python 3.7.7.
```console
pip install -r ./requrements.txt
export PYTHONPATH=`pwd -P`:$PYTHONPATH
```

## How to generate FLD corpus
Use `./create_corpus.py`, which generates a corpus with the design specified by the option values.

We can create **FLD** (FLD.3) by running the follows command:
```console
python ./create_corpus.py\
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
python ./create_corpus.py\
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
