# FLD Generator
![framework_overview](./images/framework_overview.PNG)

This repository includes the code for generating the FLD corpus.  

See [the entry-point repository](https://github.com/hitachi-nlp/FLD.git) about the whole FLD project.




## Releases
* (2024-01-24) `NLP_2024_KOBE_BEEF` branch
    - Release at LREC-COLING 2024 and NLP(言語処理学会) 2024．
    - **We made it possible to generate Japanese corpora (JFLD)**.
    - The corpus schema is changed a bit.
    - **This branch and generated corpora might not be compatible with the older branches of relevant repositories.**
* (2023-08-22) `main` branch.
    - Initial release at ICML 2023.
    * This is version 2.0 of FLD corpora. See the Appendix.H of [our paper](https://arxiv.org/abs/2308.07336) for details.



## Installation
The code has been tested on Python 3.7.7.
```console
pip install -r ./requirements/requrements.txt
export PYTHONPATH=`pwd -P`:$PYTHONPATH
```




## Additional Resources Required

### For Japanese FLD
```console
./download_scripts/00.download_JFLD_resources.sh
```

### For Knowledge FLD
```console
./download_scripts/00.download_knowledge_banks.sh
```




## How to generate FLD corpus
Use `./scripts/create_corpus.py`, which generates a corpus with the design specified by the option values.
Note that creating corpora takes much computationally cost, e.g., ~ 500 CPUs times 30 minutes for 30,000 exmaples.

* **FLD** (FLD.3):
    ```console
    python ./scripts/create_corpus.py \
        <output_dir> \
        <dataset_size> \
        --depth-range '[1, 3]' \
        --depth-distrib flat \
        --branch-extensions-range '[0, 5]' \
        --argument-config ./configs/arguments/axioms/ \
        --complex-formula-arguments-weight 0.5 \
        --quantifier-axiom-arguments-weight 0.2 \
        --quantifier-axiom universal_quantifier_elim \
        --quantifier-axiom universal_quantifier_intro \
        --quantifier-axiom existential_quantifier_intro \
        --quantifier-axiom existential_quantifier_elim \
        --translation-config ./configs/translations/thing.v1/ \
        --distractor "mixture(negative_tree_double.simplified_formula.various_form)" \
        --distractors-range '[0, 20]' \
        --num-workers 5 \
        --seed 0
    ```

* **FLD★** (FLD.4):
    ```console
    python ./scripts/create_corpus.py \
        <output_dir> \
        <dataset_size> \
        --depth-range '[1, 8]' \
        --depth-distrib flat \
        --branch-extensions-range '[0, 5]' \
        --argument-config ./configs/arguments/axioms/ \
        --complex-formula-arguments-weight 0.5 \
        --quantifier-axiom-arguments-weight 0.2 \
        --quantifier-axiom universal_quantifier_elim \
        --quantifier-axiom universal_quantifier_intro \
        --quantifier-axiom existential_quantifier_intro \
        --quantifier-axiom existential_quantifier_elim \
        --translation-config ./configs/translations/thing.v1/ \
        --distractor "mixture(negative_tree_double.simplified_formula.various_form)" \
        --distractors-range '[0, 20]' \
        --num-workers 5 \
        --seed 0
    ```

* **JFLD_punipuni.D3**
    ```console
    python ./scripts/create_corpus.py \
        <output_dir> \
        <dataset_size> \
        --depth-range '[1, 3]' \
        --depth-distrib flat \
        --branch-extensions-range '[0, 5]' \
        --argument-config ./configs/arguments/axioms/axiom.and_or.pred_arg.json \
        --argument-config ./configs/arguments/axioms/axiom.implication_intro.pred_arg.json \
        --argument-config ./configs/arguments/axioms/axiom.negation.pred_arg.json \
        --argument-config ./configs/arguments/axioms/axiom.pred_arg.json \
        --argument-config ./configs/arguments/references/reference.pred_arg.json \
        --complex-formula-arguments-weight 0.5 \
        --quantifier-axiom-arguments-weight 0.2 \
        --quantifier-axiom universal_quantifier_elim \
        --quantifier-axiom universal_quantifier_intro \
        --quantifier-axiom existential_quantifier_intro \
        --quantifier-axiom existential_quantifier_elim  \
        --translation-lang jpn \
        --translation-config thing.v1     \
        --translation-volume-to-weight log10 \
        --translation-adj-verb-noun-ratio 1-1-1 \
        --translation-vocab wordnet \
        --distractor "mixture(negative_tree_double.simplified_formula.various_form)" \
        --distractors-range '[0, 20]'      \
        --translation-distractors-range '[0, 0]'     \
        --knowledge-argument-factor 1.0      \
        --unknown-ratio 0.33  \
        --context-shuffles-per-instance 1  \
        --translation-variants-per-logic 1 \
        --num-workers 5 \
        --seed 0
    ```
