# FLD Generator
Code for generating FLD corpus.

## Installation
`pip install -r ./requrements.txt`

## How to use
The main script is `./create_FLD_corpus.py`, which takes various options that specify the design of corpora, such as:
```sh
python ./create_FLD_corpus.py\
    <output_dir>\
    <dataset_size>\
    --ac ./configs/FLNL/arguments/axiom.pred_only.json\
    --ac ./configs/FLNL/arguments/axiom.pred_arg.json\
    --ac ./configs/FLNL/arguments/theorem.G_MP.pred_arg.json\
    --tc ./configs/FLNL/translations/thing.json\
    --tc ./configs/FLNL/translations/thing.sentence_negation.json\
    --depths '[1, 2, 3, 4, 5]'\
    --complication 0.5\
    --quantification 0.2\
    --distractor mixture.negative_tree.simplified_formula.various_form\
    --num-distractors '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]'\
    --proof-stances '["PROOF", "DISPROOF", "UNKNOWN"]'\
    --world-assump OWA\
    --num-workers 5\
    --seed 0 
```
In the above command, each option correspond to one design aspect, as follows:
* `ac`              : argument (deduction rule) configuration files
* `tc`              : natural language translation config files
* `depths`          : the depths of proof trees
* `complication`    : the ratio of complex formulas included in the dataset
* `quantification`  : the ratio of quantification formulas (i.e., formulas that use ∀,∃)
* `distractors`     : type of distractor
* `num-distractors`     : possible number of distractors in each example
* `proof-stances`   : possible proof stance of each example
* `world-assump`   : the world assumption (Open World Assumption vs Closed World Assumption)

See the source for full options.
