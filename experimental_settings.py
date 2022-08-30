from typing import Dict
import copy

_DATASET_SETTINGS = {
    '20220828.size--100000': {
        'world_assump': 'label_true_only',

        'argument_configs': [
            './configs/formal_logic/arguments/axiom.pred_only.json',
            './configs/formal_logic/arguments/axiom--and_or.pred_only.json',

            './configs/formal_logic/arguments/axiom.pred_arg.json',
            './configs/formal_logic/arguments/axiom--and_or.pred_arg.json',

            './configs/formal_logic/arguments/theorem.pred_only.json',
            './configs/formal_logic/arguments/theorem--and_or.pred_only.json',

            './configs/formal_logic/arguments/theorem.pred_arg.json',
            './configs/formal_logic/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 5,
        'max_leaf_extensions': 5,
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },

    '20220830.basic': {
        'world_assump': 'label_true_only',

        'argument_configs': [
            './configs/formal_logic/arguments/axiom.pred_only.json',
            # './configs/formal_logic/arguments/axiom--and_or.pred_only.json',

            # './configs/formal_logic/arguments/axiom.pred_arg.json',
            # './configs/formal_logic/arguments/axiom--and_or.pred_arg.json',

            './configs/formal_logic/arguments/theorem.pred_only.json',
            # './configs/formal_logic/arguments/theorem--and_or.pred_only.json',

            # './configs/formal_logic/arguments/theorem.pred_arg.json',
            # './configs/formal_logic/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'max_leaf_extensions': 0,
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },


    '20220830.pred_arg': {
        'world_assump': 'label_true_only',

        'argument_configs': [
            './configs/formal_logic/arguments/axiom.pred_only.json',
            # './configs/formal_logic/arguments/axiom--and_or.pred_only.json',

            './configs/formal_logic/arguments/axiom.pred_arg.json',
            # './configs/formal_logic/arguments/axiom--and_or.pred_arg.json',

            './configs/formal_logic/arguments/theorem.pred_only.json',
            # './configs/formal_logic/arguments/theorem--and_or.pred_only.json',

            './configs/formal_logic/arguments/theorem.pred_arg.json',
            # './configs/formal_logic/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'max_leaf_extensions': 0,
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },


    '20220830.and_or_not_quant': {
        'world_assump': 'label_true_only',

        'argument_configs': [
            './configs/formal_logic/arguments/axiom.pred_only.json',
            './configs/formal_logic/arguments/axiom--and_or.pred_only.json',

            './configs/formal_logic/arguments/axiom.pred_arg.json',
            './configs/formal_logic/arguments/axiom--and_or.pred_arg.json',

            './configs/formal_logic/arguments/theorem.pred_only.json',
            './configs/formal_logic/arguments/theorem--and_or.pred_only.json',

            './configs/formal_logic/arguments/theorem.pred_arg.json',
            './configs/formal_logic/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 1,
        'max_leaf_extensions': 0,
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },


}


def get_dataset_setting(name: str) -> Dict:
    return copy.deepcopy(_DATASET_SETTINGS[name])
