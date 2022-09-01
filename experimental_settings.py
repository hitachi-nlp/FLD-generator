from typing import Dict
import copy

_DATASET_SETTINGS = {
    # XXX: Be cared about the max length not to be too large, when you edit the setting.

    '20220828.size--100000': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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

    '20220830.minimal': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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


    '20220830.pred_arg.and_or_not_quant': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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


    '20220830.depth-3': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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

        'depth': 3,
        'max_leaf_extensions': 3,
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },


    '20220830.depth-3.distractor': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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

        'depth': 3,
        'max_leaf_extensions': 3,
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },


    '20220830.depth-5': {
        'world_assump': 'OWA',
        'proof_types': ['proof', 'disproof'],

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
        'max_leaf_extensions': 3,
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/formal_logic/translations/clause_typed.thing.json'
        ],
    },

}


def get_dataset_setting(name: str) -> Dict:
    return copy.deepcopy(_DATASET_SETTINGS[name])
