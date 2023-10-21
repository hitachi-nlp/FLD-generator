# FLD Generator
This repository includes the code for generating the FLD corpus.  

See [the entry-point repository](https://github.com/hitachi-nlp/FLD.git) about the whole FLD project.

## About this release
* This is version 2.0 of FLD corpora. See [the arXiv version of our paper](https://arxiv.org/abs/2308.0733) for details.

## Installation
The code has been tested on Python 3.7.7.
```console
$ pip install -r ./requirements/requrements.txt
```

## Additional Resources Required

### Japanese FLD
```console
git clone https://github.com/taku910/mecab ./res/word_banks/japanese/mecab
```

### Knowledge FLD
In order to create the corpora with "knowledge injection", you need to download ATOMIC dataset preprocessed in [allenai/commonsense-kg-completion](https://github.com/allenai/commonsense-kg-completion), as follows:
```console
mkdir -p ./res/knowledge/
FILE_NAME="./res/knowledge/commonsense-kg-completion.zip";

file_id="1dpSK-eV_USdQ9XvqBuj2rjvtgz_97P0E";
CONFIRM=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate "https://drive.google.com/uc?export=download&id=$file_id" -O- | sed -En 's/.*confirm=([0-9A-Za-z_]+).*/\1/p');
wget --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$CONFIRM&id=$file_id" -O $FILE_NAME;
rm -f /tmp/cookies.txt

unzip ./res/knowledge/commonsense-kg-completion.zip -d ./res/knowledge/commonsense-kg-completion```
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
