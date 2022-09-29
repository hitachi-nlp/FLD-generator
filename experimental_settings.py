from typing import Dict
import copy

_DATASET_SETTINGS = {
    # XXX: Be cared about the max length not to be too large, when you edit the setting.

    '20220828.size--100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 5,
        'branch_extension_steps': 5,
        'distractor': 'unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

    '20220901.atmf-P.arg-basic.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220901.atmf-PA.arg-basic.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220901.atmf-PA.arg-compl.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220901.atmf-PA.arg-compl.dpth-3': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 3,
        'branch_extension_steps': 3,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

    '20220901.atmf-PA.arg-compl.dpth-5': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 5,
        'branch_extension_steps': 3,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

    '20220902.atmf-P.arg-basic.dpth-1.disproof-off': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },











    '20220916.atmf-P.arg-basic.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220916.atmf-PA.arg-basic.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220916.atmf-PA.arg-compl.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220916.atmf-PA.arg-compl.dpth-3.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 3,
        'branch_extension_steps': 3,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

    '20220916.atmf-PA.arg-compl.dpth-5.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 5,
        'branch_extension_steps': 3,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },









    '20220928.atmf-P.arg-basic.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220928.atmf-PA.arg-basic.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220928.atmf-PA.arg-compl.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 1,
        'branch_extension_steps': 0,
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },


    '20220928.atmf-PA.arg-compl.dpth-3.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 3,
        'branch_extension_steps': 3,
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

    '20220928.atmf-PA.arg-compl.dpth-5.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom--and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom--and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem--and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem--and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depth': 5,
        'branch_extension_steps': 3,
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
    },

}


def get_dataset_setting(name: str) -> Dict:
    return copy.deepcopy(_DATASET_SETTINGS[name])
