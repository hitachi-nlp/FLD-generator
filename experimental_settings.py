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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 0.5,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'distractor_factor': 1.0,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.negative_tree.unknown_interprands',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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
        'distractor': 'mixture.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
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









    '20221026__dpth-M__bx-M__dist-unk__dist_size-M__reuse-0.0__transl_weight-linear__size-S': {
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'linear',

        'split_sizes': {
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221026__dpth-M__bx-M__dist-unk__dist_size-M__reuse-0.0__transl_weight-sqrt__size-S': {
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
        'distractor': 'fallback.unknown_interprands.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'sqrt',

        'split_sizes': {
            # 'test': 10,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221028__dpth-M__bx-M__dist-var__dist_size-S__reuse-0.0__transl_weight-linear__size-S': {
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
        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(1, 5),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'linear',

        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221028__dpth-M__bx-M__dist-var__dist_size-M__reuse-0.0__transl_weight-linear__size-S': {
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
        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(1, 10),

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'reused_object_nouns_max_factor': 0.0,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'linear',

        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },














    '20221101__arg-basic__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-True__voc_limit-100__dataset_size-100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],


        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            './configs/FLNL/arguments/theorem.pred_only.json',
            './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'complication': 0.0,
        'quantification': 0.0,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(1, 3),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221101__arg-cmpl__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-True__voc_limit-100__dataset_size-100000': {
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


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221101__arg-cmpl__dpth-3__bx-3__dist-var__dist_size-0__reuse-0.0__fixed_transl-False__voc_limit-None__dataset_size-100000': {
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


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-0__reuse-0.0__fixed_transl-False__voc_limit-None__dataset_size-100000': {
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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-10__reuse-1.0__fixed_transl-False__voc_limit-None__dataset_size-100000': {
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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221101__arg-cmpl__dpth-10__bx-5__dist-var__dist_size-10__reuse-1.0__fixed_transl-False__voc_limit-None__dataset_size-300000': {
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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 300000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221107__arg-cmpl__dpth-03__dist-10__transl-wide__size-100000': {
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
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221107__arg-cmpl__dpth-10__dist-10__transl-wide__size-100000': {
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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },








    '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--0__transl-wide__unk-0.33__size-100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],
        'unknown_ratio': 0.33,


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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 5),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_distractor': 'word_swap',
        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 10000,
            # 'valid': 1000,
            # 'test': 1000,
        }
    },



    '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--10__transl-wide__unk-0.33__size-100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],
        'unknown_ratio': 0.33,


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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 5),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_distractor': 'word_swap',
        'num_translation_distractors': _to_range(0, 10),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },



    '20221112__arg-cmpl__dpth-10__dist-5__transl_dist--0__transl-wide__unk-0.65__size-100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],
        'unknown_ratio': 0.65,


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


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 5),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_distractor': 'word_swap',
        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },



    '20221112__arg-cmpl__dpth-3__dist-5__transl_dist--0__transl-wide__unk-0.33__size-100000': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],
        'unknown_ratio': 0.33,


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
        'branch_extension_steps': _to_range(1, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 5),
        'reused_object_nouns_max_factor': 1.0,
        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'add_subj_obj_swapped_distractor': True,


        'translation_distractor': 'word_swap',
        'num_translation_distractors': _to_range(0, 0),

        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',
        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },






















    '20221115__arg-RT__frml-smpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.0,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'add_subj_obj_swapped_distractor': False,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },




    '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'add_subj_obj_swapped_distractor': False,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },



    '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--10__transl-nrrw__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'add_subj_obj_swapped_distractor': False,


        'num_translation_distractors': _to_range(0, 10),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },




    '20221115__arg-RT__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },





    '20221115__arg-all__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000': {

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
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },




    '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-nrrw__size-100000': {

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
        'quantification': 0.2,


        'complication': 0.3,


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(0, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },



    '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-wide__size-100000': {

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
        'quantification': 0.2,


        'complication': 0.3,


        'depths': _to_range(1, 10),
        'branch_extension_steps': _to_range(0, 5),


        'distractor': 'fallback.various_form.negative_tree',
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,


        'num_translation_distractors': _to_range(0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },















    '20221117__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--20__transl-wide__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 4),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'add_subj_obj_swapped_distractor': False,


        'num_translation_distractors': _to_range(0, 20),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },


    '20221117__arg-RT__frml-cmpl__tree-tiny__dist-0__transl_dist--20__transl-wide__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 2),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'various_form',
        'num_distractors': _to_range(0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'add_subj_obj_swapped_distractor': False,


        'num_translation_distractors': _to_range(0, 20),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 1000,

            'train': 100000,
            'valid': 1000,
            'test': 1000,
        }
    },





    '20221120.negative_tree__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 0),


        'distractor': 'fallback.negative_tree.various_form',
        'try_negated_hypothesis_first': False,  # set as True if complication=0.0
        'num_distractors': _to_range(0, 5),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,

        'num_translation_distractors': _to_range(0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'train': 10000,
            'test': 1000,
        }
    },




    '20221123.and__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-100000': {

        'argument_configs': [
            './configs/FLNL/arguments/axiom.pred_only.json',
            './configs/FLNL/arguments/axiom.pred_arg.json',

            # './configs/FLNL/arguments/axiom.and_or.pred_only.json',
            # './configs/FLNL/arguments/axiom.and_or.pred_arg.json',

            # './configs/FLNL/arguments/axiom.implication_intro.pred_only.json',
            # './configs/FLNL/arguments/axiom.implication_intro.pred_arg.json',

            # './configs/FLNL/arguments/axiom.negation.pred_only.json',
            # './configs/FLNL/arguments/axiom.negation.pred_arg.json',

            # './configs/FLNL/arguments/theorem.pred_only.json',
            # './configs/FLNL/arguments/theorem.pred_arg.json',

            # './configs/FLNL/arguments/theorem.and_or.pred_only.json',
            # './configs/FLNL/arguments/theorem.and_or.pred_arg.json',
        ],
        'quantification': 0.2,

        'complication': 0.3,


        'depths': _to_range(1, 3),
        'branch_extension_steps': _to_range(0, 3),


        'distractor': 'mixture.negative_tree.simplified_formula.various_form',
        'try_negated_hypothesis_first': False,  # set as True if complication=0.0
        'num_distractors': _to_range(0, 10),
        'reused_object_nouns_max_factor': 1.0,
        'add_subj_obj_swapped_distractor': True,

        'num_translation_distractors': _to_range(0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 1000,
            'train': 10000,
        }
    },



}


_DEFAULT_DATASET_SETTINGS = {
    '20221115': {
        'world_assump': 'OWA',
        'proof_stances': ['PROOF', 'DISPROOF', 'UNKNOWN'],
        'unknown_ratio': 0.33,


        'sample_distractor_formulas_from_tree': True,
        'sample_hard_negatives': True,
        'fallback_from_formula_to_translation_distractor': True,


        'translation_distractor': 'word_swap',


        'translation_configs': [
            './configs/FLNL/translations/thing.json',
            './configs/FLNL/translations/thing.sentence_negation.json',
        ],
        'translation_volume_to_weight': 'sqrt',

    },
}


_DATASET_NAME_TO_DEFAULT = {
    '20221115__arg-RT__frml-smpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000': '20221115',
    '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--0__transl-nrrw__size-100000': '20221115',
    '20221115__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--10__transl-nrrw__size-100000': '20221115',

    '20221115__arg-RT__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000': '20221115',  # ~ RuleTaker

    '20221115__arg-all__frml-cmpl__tree-smll__dist-10__transl_dist--0__transl-nrrw__size-100000': '20221115',
    '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-nrrw__size-100000': '20221115',
    '20221115__arg-all__frml-cmpl__tree-lrg__dist-10__transl_dist--0__transl-wide__size-100000': '20221115',

    '20221117__arg-RT__frml-cmpl__tree-smll__dist-0__transl_dist--20__transl-wide__size-100000': '20221115',
    '20221117__arg-RT__frml-cmpl__tree-tiny__dist-0__transl_dist--20__transl-wide__size-100000': '20221115',

    '20221120.negative_tree__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-100000': '20221115',
}


def get_dataset_setting(name: str) -> Dict:
    setting = _DEFAULT_DATASET_SETTINGS[_DATASET_NAME_TO_DEFAULT[name]]
    setting.update(copy.deepcopy(_DATASET_SETTINGS[name]))
    return setting


def maybe_option(option: str, value: Any) -> str:
    if value is None:
        return ''
    else:
        return f'{option} {value}'
