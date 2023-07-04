# FLD Generator
This is one of the official repositories of the paper `Learning Deductive Reasoning from Synthetic Corpus based on Formal Logic`.
This repository includes the code for generating the FLD corpus.  

See [the entry-point repository](https://github.com/hitachi-nlp/FLD) for the other repositories used in the paper.

## About this release
* This is the version 2.0 of FLD corpus generator with improved natural language template quality, logical proof consistency and harder distractors.
    - The version 2.0 generates corpora slightly different from those generated by version 1.0 used in the paper, which is now deprecated.
* See [FLD-corpus](https://github.com/hitachi-nlp/FLD-corpus) for the released corpora and the language model prover performance on them.

## Installation
The code has been tested on Python 3.7.7.
```console
$ pip install -r ./requrements.txt
```

## How to generate FLD corpus
`./create_corpus.py` generates corpus with the design specified by the given options.

### Creating FLD.3

```console
$ python ./create_corpus.py\
    <output_dir>\
    <dataset_size>\
    --ac ./configs/arguments/axiom.pred_only.json\
    --ac ./configs/arguments/axiom.pred_arg.json\
    --ac ./configs/arguments/axiom.and_or.pred_only.json\
    --ac ./configs/arguments/axiom.and_or.pred_arg.json\
    --ac ./configs/arguments/axiom.implication_intro.pred_only.json\
    --ac ./configs/arguments/axiom.implication_intro.pred_arg.json\
    --ac ./configs/arguments/axiom.negation.pred_only.json\
    --ac ./configs/arguments/axiom.negation.pred_arg.json\
    --tc ./configs/translations/thing.v1/negated_sentence.zeroary_predicates.json\
    --tc ./configs/translations/thing.v1/negated_sentence.others.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.it.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.existentials.json\
    --tc ./configs/translations/thing.v1/sentence.others.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.something.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.constants.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.universals.json\
    --tc ./configs/translations/thing.v1/negated_sentence.unary_predicates.existentials.json\
    --tc ./configs/translations/thing.v1/sentence.zeroary_predicates.json\
    --tc ./configs/translations/thing.v1/negated_sentence.unary_predicates.constants.json\
    --tc ./configs/translations/thing.v1/clauses.json\
    --tc ./configs/translations/thing.v1/phrases.json\
    --tc ./configs/translations/thing.v1/sentence.unary_predicates.everything.json\
    --tc ./configs/translations/thing.v1/negated_sentence.unary_predicates.universals.json \
    --reused-object-nouns-max-factor 1.0 \
    --translation-volume-to-weight sqrt\
    --depths '[1, 2, 3]'\
    --depth-distribution flat.no_reference\
    --branch-extension-steps '[0, 1, 2, 3, 4, 5]'\
    --complication 0.5\
    --quantification 0.2\
    --quantifier-axiom universal_quantifier_elim\
    --quantifier-axiom universal_quantifier_intro\
    --quantifier-axiom existential_quantifier_intro\
    --quantifier-axiom existential_quantifier_elim \
    --quantify-all-at-once\
    --distractor mixture.negative_tree.negative_tree\
    --num-distractors '[15, 16, 17, 18, 19, 20]'\
    --sample-distractor-formulas-from-tree\
    --use-simplified-tree-formulas-as-distractor-prototype \
    --negated-hypothesis-ratio 1.0\
    --add-subj-obj-swapped-distractor \
    --swap-ng-words-config ./configs/translation_distractors/swap_ng_words.2023-06-16.json\
    --translation-distractor word_swap\
    --num-translation-distractors '[0, 1, 2, 3, 4, 5]'\
    --proof-stances '["PROVED", "DISPROVED", "UNKNOWN"]'\
    --world-assump OWA\
    --unknown-ratio 0.33\
    --use-collapsed-translation-nodes-for-unknown-tree\
    --num-workers 5\
    --seed 0
```

### Creating FLD.4
TODO


## Citation
```bibtex
@inproceedings{morishita2023FLD,
  title={Learning Deductive Reasoning from Synthetic Corpus based on Formal Logic},
  author={Morishita, Terufumi and Morio, Gaku and Yamaguchi, Atsuki and Sogawa, Yasuhiro},
  booktitle={International Conference on Machine Learning},
  year={2023},
  organization={PMLR}
}
```
