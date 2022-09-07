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

    '20220901.atmf-P.arg-basic.dpth-1.dstrct-off': {
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


    '20220901.atmf-PA.arg-basic.dpth-1.dstrct-off': {
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


    '20220901.atmf-PA.arg-compl.dpth-1.dstrct-off': {
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


    '20220901.atmf-PA.arg-compl.dpth-3.dstrct-off': {
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


    '20220901.atmf-PA.arg-compl.dpth-3.dstrct-on': {
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


    '20220901.atmf-PA.arg-compl.dpth-5.dstrct-on': {
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

    '20220902.atmf-P.arg-basic.dpth-1.dstrct-off.disproof-off': {
        'world_assump': 'OWA',
        'proof_types': ['proof'],

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


}


def get_dataset_setting(name: str) -> Dict:
    return copy.deepcopy(_DATASET_SETTINGS[name])
