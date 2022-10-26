from typing import Dict, List, Any
import copy


def _to_range(begin: int, end: int) -> List[int]:
    return list(range(begin, end + 1))


_DATASET_SETTINGS = {
    # XXX: Be cared about the max length not to be too large, when you edit the setting.

    '20220828.size--100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [5],
        'distractor': 'unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220901.atmf-P.arg-basic.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220901.atmf-PA.arg-basic.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220901.atmf-PA.arg-compl.dpth-1': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220901.atmf-PA.arg-compl.dpth-3': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220901.atmf-PA.arg-compl.dpth-5': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220902.atmf-P.arg-basic.dpth-1.disproof-off': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },











    '20220916.atmf-P.arg-basic.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220916.atmf-PA.arg-basic.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220916.atmf-PA.arg-compl.dpth-1.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220916.atmf-PA.arg-compl.dpth-3.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220916.atmf-PA.arg-compl.dpth-5.UNKNOWN': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },









    '20220928.atmf-P.arg-basic.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220928.atmf-PA.arg-basic.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.0,
        'quantification': 0.0,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220928.atmf-PA.arg-compl.dpth-1.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [1],
        'branch_extension_steps': [0],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20220928.atmf-PA.arg-compl.dpth-3.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220928.atmf-PA.arg-compl.dpth-5.neg_tree_distractor': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20220929.atmf-PA.arg-compl.dpth-3.20220929.assump.debug': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            # './configs/FLNL/arguments/axiom.pred_arg.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            # './configs/FLNL/arguments/theorem.pred_arg.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'limit_vocab_size_per_type': None,
        'reused_object_nouns_max_factor': 0.0,
    },


    '20220929.atmf-PA.arg-compl.dpth-3.20221001.assump.void': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'limit_vocab_size_per_type': None,
    },


    '20220929.atmf-PA.arg-compl.dpth-5.20221001.assump.void': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20221002.atmf-PA.arg-compl.dpth-3.neg_tree_distractor.more': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20221002.atmf-PA.arg-compl.dpth-5.neg_tree_distractor.more': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_only.json',

            './configs/FLNL/arguments/axiom.pred_arg.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_only.json',

            './configs/FLNL/arguments/theorem.pred_arg.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20221007.atmf-PA.arg-compl.dpth-3.add-axioms-theorems': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },

    '20221007.atmf-PA.arg-compl.dpth-5.add-axioms-theorems': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20221007.atmf-PA.arg-compl.dpth-10.add-axioms-theorems': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [10],
        'branch_extension_steps': [5],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },


    '20221007.atmf-PA.arg-compl.dpth-1-3.add-axioms-theorems': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [1, 2, 3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
    },



    '20221007.atmf-PA.arg-compl.dpth-3.add-axioms-theorems.limit_vocab': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': 100,
    },


    '20221007.atmf-PA.arg-compl.dpth-5.add-axioms-theorems.limit_vocab': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [5],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': 100,
    },


    '20221007.atmf-PA.arg-compl.dpth-10.add-axioms-theorems.limit_vocab': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [10],
        'branch_extension_steps': [5],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': 100,
    },


    '20221007.atmf-PA.arg-compl.dpth-1-3.add-axioms-theorems.limit_vocab': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': [1, 2, 3],
        'branch_extension_steps': [3],
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': 100,
    },

















    '20221011__dpth-S__bx-S__dist-neg__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-neg__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-S__bx-S__dist-neg__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-neg__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-neg__dist_size-M__size-M': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.negated_hypothesis_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 300000,
            # 'valid': 1000,
            # 'test': 1000,
        }
    },


    '20221011__dpth-S__bx-S__dist-unk__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-unk__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-S__bx-S__dist-unk__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-unk__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-unk__dist_size-M__size-M': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 300000,
            'valid': 1000,
            'test': 1000,
        }
    },






    '20221011__dpth-S__bx-S__dist-mix__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-mix__dist_size-S__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-S__bx-S__dist-mix__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-M': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 300000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221015__debug': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.5,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            'train': 1000,
            # 'valid': 10,
            # 'test': 10,
        }
    },







    '20221015__dpth-S__bx-S__dist-mix__dist_size-M__size-S.reuse_object_nouns': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.5,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },

    '20221011__dpth-M__bx-M__dist-mix__dist_size-M__size-S.reuse_object_nouns': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'mixture.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.5,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },









    '20221026__dpth-M__bx-M__dist-unk__dist_size-M__size-S': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            './configs/FLNL/arguments/axiom.negation.pred_only.json',
            './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],

        'complication': 0.3,
        'quantification': 0.2,

        'depths': _to_range(1, 8),
        'branch_extension_steps': _to_range(1, 5),
        'distractor': 'fallback.unknown_interprands.negated_hypothesis_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/clause_typed.thing.json',
            './configs/FLNL/translations/clause_typed.thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,

        'split_sizes': {
            # 'train': 10,
            # 'valid': 10,
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


}


def get_dataset_setting(name: str) -> Dict:
    return copy.deepcopy(_DATASET_SETTINGS[name])


def maybe_option(option: str, value: Any) -> str:
    if value is None:
        return ''
    else:
        return f'{option} {value}'
