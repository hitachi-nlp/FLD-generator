from typing import Dict, List, Any
import glob
import copy


def _to_range(begin: int, end: int) -> List[int]:
    return list(range(begin, end + 1))


_TRANSLATION_THING_CONFIGS_ENG = ['./configs/translations/eng/thing/']
_TRANSLATION_THING_CONFIGS_ENG_V1 = ['./configs/translations/eng/thing.v1/']
_TRANSLATION_THING_PERSON_CONFIGS_ENG_V0 = ['./configs/translations/eng/thing_person.v0/']
_TRANSLATION_THING_CONFIGS_JPN_V1 = ['./configs/translations/jpn/thing.v1/']



_DATASET_SETTINGS = {

    '20221203.first_exp__arg-RT__frml-smpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.0,


        'distractors_range': (0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'disallow_subj_obj_swapped_distractor': True,

        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-RT__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 0),
        'reused_object_nouns_max_factor': 0.0,
        'disallow_subj_obj_swapped_distractor': True,

        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-AA__frml-cmpl__dist-20__transl-nrrw__tree-1__dataset_size-30000': {

        'argument_configs': [
            './configs/arguments/others/AACorpus.pred_arg.json',

            # './configs/arguments/axioms/axiom.pred_only.json',
            # './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.0,  # can not be used with AACorpus


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 1),
        'branch_extensions_range': (0, 0),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },







    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },




    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 1000,
            'train': 100000,
        }
    },












    # ---------------------------------- 20221215 additional experiments ------------------------------------


    '20221203.first_exp__arg-RT__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.0,

        # ---- since complex_formula_arguments_weight = 0.0
        'distractor': 'various_form',
        'disallow_simplified_tree_formulas_as_distractor_prototype': True,
        'sample_distractor_prototype_formulas_from_all_possible_formulas': True,
        'disallow_hard_negative_distractors': True,
        'fallback_from_formula_to_translation_distractor': True,

        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },



    # ---------------------------------- 20221216 additional experiments ------------------------------------


    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 0),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-FLNL__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.0,

        # ---- since complex_formula_arguments_weight = 0.0
        'distractor': 'various_form',
        'disallow_simplified_tree_formulas_as_distractor_prototype': True,
        'sample_distractor_prototype_formulas_from_all_possible_formulas': True,
        'disallow_hard_negative_distractors': True,
        'fallback_from_formula_to_translation_distractor': True,

        'distractors_range': (0, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 5),
        'branch_extensions_range': (0, 4),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-8__dataset_size-30000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),
        'depth_distrib': 'ruletaker.ours.20221202',


        'split_sizes': {
            'test': 1000,
            # 'train': 30000,
        }
    },


    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),
        'depth_distrib': 'ruletaker.ours.20221202',


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },



    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },


    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 5),
        'branch_extensions_range': (0, 4),


        'split_sizes': {
            'test': 1000,
            'train': 30000,
        }
    },





    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 1000,
            'train': 100000,
        }
    },





    # ---------------------------------- 20221217.back_to_the_past ------------------------------------

    '20221217.back_to_the_past__arg-FLNL__frml-cmpl__dist-10__transl-wide__tree-10__dataset_size-100000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.3,


        'distractor': 'fallback(various_form.negative_tree)',
        'disallow_simplified_tree_formulas_as_distractor_prototype': True,
        'sample_distractor_prototype_formulas_from_all_possible_formulas': True,
        'disallow_hard_negative_distractors': True,
        'fallback_from_formula_to_translation_distractor': False,


        'distractors_range': (0, 10),
        'disallow_subj_obj_swapped_distractor': True,


        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 10),
        'branch_extensions_range': (1, 5),


        'split_sizes': {
            # 'test': 1000,
            'train': 100000,
        }
    },


    '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            # 'train': 30000,
        }
    },


    '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 1000,
            # 'train': 30000,
        }
    },


    '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            './configs/arguments/theorems/theorem.pred_only.json',
            './configs/arguments/theorems/theorem.pred_arg.json',

            './configs/arguments/theorems/theorem.and_or.pred_only.json',
            './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }
    },


    '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }
    },



    '20230616.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }
    },


    '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 1000,
            # 'train': 30000,
        }
    },


    '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems.wo_translation_dist': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),
        'fallback_from_formula_to_translation_distractor': False,

        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': None,


        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }
    },



    '20230626.many_bugs_fixed.20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            # './configs/arguments/axioms/axiom.and_or.pred_only.json',
            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            # './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            # './configs/arguments/axioms/axiom.negation.pred_only.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',

            './configs/arguments/theorems/theorem.G_MP.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,

        'quantifier_axioms': [
            'universal_quantifier_elim',
            # 'universal_quantifier_intro',

            # we do not use existential_quantifier_intro since it has no linkable_args without existential_quantifier_elim, which is not implemented yet.
            # 'existential_quantifier_intro',
        ],

        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 15),


        'use_fixed_translation': True,
        'limit_vocab_size_per_type': 100,


        'depth_distrib': 'flat',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },



    '20230626.many_bugs_fixed.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.plus_quantifiers': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (0, 20),


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 1000,
            'train': 30000,
        }
    },




    '20230626.many_bugs_fixed.D3.hard': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },




    '20230626.many_bugs_fixed.D3.hard.dist-trees': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },
    



    '20230626.many_bugs_fixed.D3.hard.unk-0.1': {
        'unknown_ratio': 0.1,

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },




    '20230626.many_bugs_fixed.D3.hard.brnch-high': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },



    '20230626.many_bugs_fixed.D3.hard.dist-neg-1.0': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        'distractor': 'negative_tree-1.0',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },



    '20230626.many_bugs_fixed.D3.hard.dist-neg-0.5': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        # 'negative_tree_negated_hypothesis_ratio': 0.5,
        'distractor': 'negative_tree-0.5',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },


    '20230626.many_bugs_fixed.D3.hard.dist-neg-0.0': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        # 'negative_tree_negated_hypothesis_ratio': 0.0,
        'distractor': 'negative_tree-0.0',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },




    '20230626.many_bugs_fixed.D3.hard.dist-trees-only': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        'distractor': 'mixture(negative_tree_double)',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 3),


        'split_sizes': {
            # 'test': 500,
            'train': 15000,
        }
    },





    '20230626.many_bugs_fixed.D8.hard': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },







    '20230626.many_bugs_fixed.D8.hard.dist-trees': {

        'argument_configs': [
            # './configs/arguments/others/AACorpus.pred_arg.json',

            './configs/arguments/axioms/axiom.pred_only.json',
            './configs/arguments/axioms/axiom.pred_arg.json',

            './configs/arguments/axioms/axiom.and_or.pred_only.json',
            './configs/arguments/axioms/axiom.and_or.pred_arg.json',

            './configs/arguments/axioms/axiom.implication_intro.pred_only.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',

            './configs/arguments/axioms/axiom.negation.pred_only.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',

            # './configs/arguments/theorems/theorem.pred_only.json',
            # './configs/arguments/theorems/theorem.pred_arg.json',

            # './configs/arguments/theorems/theorem.and_or.pred_only.json',
            # './configs/arguments/theorems/theorem.and_or.pred_arg.json',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractors_range': (15, 20),
        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_vocab': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 8),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },




    '20230701.D3.default': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_vocab': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),

        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },





    '20230701.D3.wo_transl_dist': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_vocab': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },



    '20230701.D3.brnch-small': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (0, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },




    '20230701.D3.dist-small': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (0, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },



    '20230701.D3.default.refactor_test': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            # 'test': 50,
            'test': 300,
            # 'test': 1000,
        }
    },



    '20230701.D3.default.dist-tree-triple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_triple)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            # 'test': 50,
            'test': 300,
            # 'test': 1000,
        }
    },



    '20230701.D3.default.dist-tree-quadruple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_quadruple)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            # 'test': 50,
            'test': 300,
            # 'test': 1000,
        }
    },




    '20230701.D8.default': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 8),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            'test': 500,
            'train': 15000,
        }
    },





    '20230701.D3.debug': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axiom_arguments_weight': 0.2,


        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],


        'complex_formula_arguments_weight': 0.5,


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),

        'translation_distractors_range': (0, 5),
        'use_collapsed_translation_nodes_for_unknown_tree': True,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'depth_distrib': 'flat.no_reference',
        'depth_range': (1, 3),
        'branch_extensions_range': (2, 5),


        'split_sizes': {
            'test': 100,
            # 'train': 15000,
        }
    },












    '20230706.finalize.D3.dist-double': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'train': 15000,
        }

    },



    '20230706.finalize.D3.dist-quadruple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_quadruple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'train': 15000,
        }

    },



    '20230706.finalize.D8.dist-double': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'train': 15000,
        }

    },




    '20230706.finalize.D8.dist-quadruple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_quadruple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'train': 15000,
        }

    },











    '20230707.finalize.D3.dist-double': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }

    },



    '20230707.finalize.D3.dist-triple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_triple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 500,
            'train': 30000,
        }

    },



    '20230707.finalize.D3.dist-quadruple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_quadruple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            # 'test': 500,
            'train': 30000,
        }

    },



    '20230711.dist-fallback': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'fallback(mixture(negative_tree_double).simplified_formula.various_form)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 100,
            # 'train': 30000,
        }

    },





    '20230707.finalize.D8.dist-double': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },




    '20230707.finalize.D8.dist-triple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_triple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },




    '20230707.finalize.D8.dist-quadruple': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_quadruple)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },





    '20230711.finalize.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'fallback(mixture(negative_tree_double).simplified_formula.various_form)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            # 'train': 30000,
        }

    },



    '20230711.finalize.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'fallback(mixture(negative_tree_double).simplified_formula.various_form)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            # 'train': 30000,
        }

    },








    '20230718.case_study.D3.dist-mixture': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (15, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },


    '20230718.case_study.D3.num_dist-wide': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'fallback(mixture(negative_tree_double).simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },


    '20230718.case_study.D3.dist-mixture.num_dist-wide': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },



    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_logE': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'logE',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },



    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_log10': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'log10',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },




    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_log10.adj_verb_noun_equal': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },



    '20230718.case_study.D8.dist-mixture.num_dist-wide': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat.no_reference',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'use_fixed_translation': False,
        'limit_vocab_size_per_type': None,


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },







    '20230729.case_study_finalize.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            # 'train': 30000,
        }

    },



    '20230729.case_study_finalize.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            # 'train': 30000,
        }

    },




    '20230826.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            # 'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }

    },

    '20230826.jpn.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            # 'test': 500,
            # 'valid': 5000,
            'train': 15000,
        }
    },



    '20230901.random_transitive_verbs.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            'train': 15000,
        }

    },



    '20230901.random_transitive_verbs.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            # 'train': 30000,
        }

    },



    '20230904.jpn.D1.wo_brnch.wo_dstrct': {
        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            'train': 1000,
        }
    },


    '20230904.jpn.D1.wo_brnch': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            'train': 1000,
        }

    },



    '20230904.jpn.D1': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            'train': 1000,
        }

    },



    '20230904.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            'train': 10000,
        }

    },



    '20230912.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 20000,
        }

    },



    '20230914.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            # 'train': 20000,
            'train': 1000,
        }

    },



    '20230916.jpn.D1_wo_dist': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },


    '20230916.jpn.D1': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },


    '20230916.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },



    '20230916.jpn.D5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 5),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 30000,
        }

    },




    '20231010.D3.large_vocab': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': False,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 30000,
        },

    },


    '20231012.D3.large_vocab': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': False,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 15000,
        },

    },


    '20231012.D3.large_vocab.smpl_stncs': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 45000,
        },

    },


    '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 1,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 135000,
        },

    },


    '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3.trnsl_vrnts-3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 3,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 405000,
        },

    },









    '20231018.knowledge.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': False,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 15000,
        },

    },



    '20231018.knowledge.D3.w_knowledge': {

        'knowledge_range': [0.49, 0.5],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': False,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            'train': 3000,
        },

    },



    '20231018.knowledge.D3.w_knowledge.complex-0.3': {

        'knowledge_range': [0.49, 0.5],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': False,
                'context_shuffles_per_instance': 1,
                'translation_variants_per_logic': 1,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
            },
        },
        'split_sizes': {
            'test': 500,
            # 'valid': 500,
            'train': 3000,
        },

    },




    '20231021.knowledge.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 3,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            'train': 300000,
        },

    },



    '20231021.knowledge.D3.complex-0.3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 3,
            },
            'valid': {
            },
            'test': {
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            'train': 300000,
        },

    },



    '20231021.knowledge.D3.complex-0.3.w_knowledge': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.49, 0.5],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'knowledge_no_shuffle': False,
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'knowledge_no_shuffle': True,
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'knowledge_no_shuffle': True,
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            'train': 300000,
        },

    },




    '20231028.knowledge.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            'train': 3000,
        },

    },



    '20231029.knowledge.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            # 'train': 3000,
            'train': 500,
        },

    },


    '20231029.knowledge.D3.wo_knowledge': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            # 'train': 3000,
            'train': 500,
        },

    },


    '20231029.knowledge.D3.wo_knowledge.cmplx-0.5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                # 'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                # 'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                # 'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            # 'train': 3000,
            'train': 500,
        },

    },






    '20231030.knowledge.D3.knowledge_factor-1.0': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': [0.0, 1.0],
        'knowledge_argument_factor': 1.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            'train': 3000,
            # 'train': 500,
        },

    },




    '20231030.knowledge.D3.knowledge_factor-5.0': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': [0.0, 1.0],
        'knowledge_argument_factor': 5.0,

        'split_wise_settings': {
            'train': {
                # 'sample_all_stances_per_logic': True,
                # 'context_shuffles_per_instance': 3,
                # 'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 500,
            # 'valid': 500,
            # 'train': 300000,
            'train': 3000,
            # 'train': 500,
        },

    },





    '20231103.knowledge.D3.knowledge_factor-5.0': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.3,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',

        'knowledge_range': [0.0, 1.0],
        'collapsed_knowledge_range': [0.0, 1.0],
        'knowledge_argument_factor': 5.0,

        'split_wise_settings': {
            'train': {
                'sample_all_stances_per_logic': True,
                'context_shuffles_per_instance': 3,
                'translation_variants_per_logic': 3,
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/train1.txt',
            },
            'valid': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/valid.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/valid.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/valid.txt',
            },
            'test': {
                'atomic_filepath': './res/knowledge_banks/commonsense-kg-completion/data/atomic/test.txt',
                'concept_net_100k_filepath': './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/test.txt',
                'dbpedia_filepath': './res/knowledge_banks/DBpedia500/test.txt',
            },
        },
        'split_sizes': {
            # 'test': 1000,
            # 'valid': 500,
            'train': 300000,
        },

    },





    '20231203.jpn.D1_wo_dist': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 10000,
        }

    },


    '20231203.jpn.D1': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 10000,
        }

    },


    '20231203.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            # 'test': 500,
            'train': 1000,

            # 'test': 1000,
        }

    },



    '20231203.jpn.D5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 5),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 500,
            'train': 1000,
        }

    },




    '20231203.jpn.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            # 'test': 500,
            'train': 1000,
        }

    },








    '20231213.jpn.D1_wo_dist': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }

    },


    '20231213.jpn.D1': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }

    },


    '20231213.jpn.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }

    },



    '20231213.jpn.D5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 5),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }

    },




    '20231213.jpn.D8': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': _TRANSLATION_THING_CONFIGS_JPN_V1,
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }

    },













    '20230115.jpn.BCCWJ.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1.pretty'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            # 'train': 30000,
        }

    },

    '20230115.jpn.punipuni.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1.pretty'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 100,
            # 'valid': 5000,
            # 'train': 30000,
        }

    },




    '20230116.jpn.BCCWJ.D3.argument_pred_arg_only': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            'test': 300,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },

    '20230116.jpn.punipuni.D3.argument_pred_arg_only': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 300,
            # 'valid': 5000,
            # 'train': 30000,
        }

    },






    '20230118.jpn.wordnet.D3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 30000,
        }
    },


    '20230118.jpn.wordnet.D3.argument_pred_arg_only': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 30000,
        }
    },


    '20230118.jpn.wordnet.D3.argument_pred_arg_only.no_kaku': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 30000,
        }
    },





    '20230118.jpn.BCCWJ.D3': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 30000,
        }
    },




    '20230118.jpn.punipuni.D3': {

        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            'train': 30000,
        }

    },






    '20230118.jpn.wordnet.D3.extension-3.distractor-10': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 3),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 10),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },



    '20230118.jpn.wordnet.D3.extension-3.distractor-5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 3),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 5),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },


    '20230118.jpn.wordnet.D3.extension-3.distractor-3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 3),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 3),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },



    '20230118.jpn.wordnet.D3.extension-2.distractor-5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 2),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 5),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },


    '20230118.jpn.wordnet.D3.extension-2.distractor-3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 2),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 3),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },



    '20230118.jpn.wordnet.D3.extension-1.distractor-5': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 1),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 5),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },


    '20230118.jpn.wordnet.D3.extension-1.distractor-3': {

        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 1),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 3),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },

















    '20230120.jpn.wordnet.D3': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },










    '20230120.jpn.wordnet_repro_w_proposition.D1_wo_dist': {


        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',

            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',
            # './configs/arguments/axioms/axiom.pred_arg.json',
            # './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },


    '20230120.jpn.wordnet_repro_w_proposition.D1': {


        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',

            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',
            # './configs/arguments/axioms/axiom.pred_arg.json',
            # './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.wordnet_repro_w_proposition.D3': {


        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',

            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',
            # './configs/arguments/axioms/axiom.pred_arg.json',
            # './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.wordnet_repro_w_proposition.D8': {


        'argument_configs': [
            './configs/arguments/axioms/',
            './configs/arguments/references/',

            # './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            # './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            # './configs/arguments/axioms/axiom.negation.pred_arg.json',
            # './configs/arguments/axioms/axiom.pred_arg.json',
            # './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },










    '20230120.jpn.wordnet_repro_wo_proposition.D1_wo_dist': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },


    '20230120.jpn.wordnet_repro_wo_proposition.D1': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.wordnet_repro_wo_proposition.D3': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.wordnet_repro_wo_proposition.D8': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': False,
        'translation_vocab': 'wordnet',


        'split_sizes': {
            'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },











    '20230120.jpn.BCCWJ.D1_wo_dist': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },


    '20230120.jpn.BCCWJ.D1': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.BCCWJ.D3': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.BCCWJ.D8': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['thing.v1'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'BCCWJ',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },















    '20230120.jpn.punipuni.D1_wo_dist': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },


    '20230120.jpn.punipuni.D1': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.punipuni.D3': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },



    '20230120.jpn.punipuni.D8': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 8),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            # 'test': 5000,
            'valid': 5000,
            'train': 30000,
        }
    },


















    '20230122.jpn.ICL.punipuni.D1_wo_dist': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },


    '20230122.jpn.ICL.punipuni.D1': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 1),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 0),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },



    '20230122.jpn.ICL.punipuni.D3_wo_dist': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 0),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },




    '20230122.jpn.ICL.punipuni.D3': {


        'argument_configs': [
            # './configs/arguments/axioms/',
            # './configs/arguments/references/',

            './configs/arguments/axioms/axiom.and_or.pred_arg.json',
            './configs/arguments/axioms/axiom.implication_intro.pred_arg.json',
            './configs/arguments/axioms/axiom.negation.pred_arg.json',
            './configs/arguments/axioms/axiom.pred_arg.json',
            './configs/arguments/references/reference.pred_arg.json',
        ],
        'quantifier_axioms': [
            'universal_quantifier_elim',
            'universal_quantifier_intro',
            'existential_quantifier_intro',
            'existential_quantifier_elim',
        ],
        'quantifier_axiom_arguments_weight': 0.2,
        'complex_formula_arguments_weight': 0.5,


        'depth_range': (1, 3),
        'depth_distrib': 'flat',
        'branch_extensions_range': (0, 5),


        'distractor': 'mixture(negative_tree_double.simplified_formula.various_form)',
        'distractors_range': (0, 20),
        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,


        'translation_lang': 'jpn',
        'translation_configs': ['punipuni.v0'],
        'translation_volume_to_weight': 'log10',
        'translation_adj_verb_noun_ratio': '1-1-1',
        'translation_no_transitive_object': True,
        'translation_vocab': 'punipuni',


        'split_sizes': {
            'test': 500,
            # 'valid': 5000,
            # 'train': 30000,
        }
    },


}


_DEFAULT_DATASET_SETTINGS = {

    '20221115': {
        'unknown_ratio': 0.33,
        'sample_all_stances_per_logic': False,
        'context_shuffles_per_instance': 1,

        'knowledge_range': None,
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,
        'atomic_filepath': None,
        'concept_net_100k_filepath': None,
        'dbpedia_filepath': None,

        'quantifier_axioms': [
            'universal_quantifier_elim',
            # 'universal_quantifier_intro',

            # we do not use existential_quantifier_intro since it has no linkable_args without existential_quantifier_elim, which is not implemented yet.
            # 'existential_quantifier_intro',
        ],

        'fallback_from_formula_to_translation_distractor': True,



        'translation_volume_to_weight': 'sqrt',
        'translation_adj_verb_noun_ratio': '1-2-1',
        'translation_configs': _TRANSLATION_THING_CONFIGS_ENG,
        'translation_no_transitive_object': False,

        'translation_variants_per_logic': 1,
    },


    '20221203': {
        'unknown_ratio': 0.33,
        'sample_all_stances_per_logic': False,
        'context_shuffles_per_instance': 1,

        'knowledge_range': None,
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,
        'atomic_filepath': None,
        'concept_net_100k_filepath': None,
        'dbpedia_filepath': None,

        'quantifier_axioms': [
            'universal_quantifier_elim',
            # 'universal_quantifier_intro',

            # we do not use existential_quantifier_intro since it has no linkable_args without existential_quantifier_elim, which is not implemented yet.
            # 'existential_quantifier_intro',
        ],

        'distractor': 'mixture(negative_tree.simplified_formula.various_form)',
        'fallback_from_formula_to_translation_distractor': True,
        'swap_ng_words_config': './configs/translation_distractors/swap_ng_words.json',



        'translation_volume_to_weight': 'sqrt',
        'translation_adj_verb_noun_ratio': '1-2-1',
        'translation_configs': _TRANSLATION_THING_CONFIGS_ENG,
        'translation_no_transitive_object': False,


        'depth_distrib': 'flat',

        'translation_variants_per_logic': 1,

    },


    '20230626.many_bugs_fixed': {
        'unknown_ratio': 0.33,
        'sample_all_stances_per_logic': False,
        'context_shuffles_per_instance': 1,

        'knowledge_range': None,
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,
        'atomic_filepath': None,
        'concept_net_100k_filepath': None,
        'dbpedia_filepath': None,

        # 'negative_tree_negated_hypothesis_ratio': 0.5,
        'distractor': 'mixture(negative_tree-0.5.simplified_formula.various_form)',
        'fallback_from_formula_to_translation_distractor': False,


        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'sqrt',
        'translation_adj_verb_noun_ratio': '1-2-1',
        'translation_lang': 'eng',
        'translation_configs': _TRANSLATION_THING_CONFIGS_ENG_V1,
        'translation_no_transitive_object': False,

        'translation_variants_per_logic': 1,

    },


    '20231018.thing_person_config_translation': {
        'unknown_ratio': 0.33,
        'sample_all_stances_per_logic': False,
        'context_shuffles_per_instance': 1,

        'knowledge_range': None,
        'collapsed_knowledge_range': None,
        'knowledge_argument_factor': 1.0,
        'atomic_filepath': None,
        'concept_net_100k_filepath': None,
        'dbpedia_filepath': None,

        # 'negative_tree_negated_hypothesis_ratio': 0.5,
        'distractor': 'mixture(negative_tree-0.5.simplified_formula.various_form)',
        'fallback_from_formula_to_translation_distractor': False,


        'translation_distractors_range': (0, 0),
        'use_collapsed_translation_nodes_for_unknown_tree': False,

        'translation_volume_to_weight': 'sqrt',
        'translation_adj_verb_noun_ratio': '1-2-1',
        'translation_lang': 'eng',
        'translation_configs': _TRANSLATION_THING_PERSON_CONFIGS_ENG_V0,
        'translation_no_transitive_object': False,

        'translation_variants_per_logic': 1,

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

    '20221123.and__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000': '20221115',

    '20221124.and__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000': '20221115',

    '20221125.full__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-10000': '20221115',
    '20221126.transl__arg-RT__frml-cmpl__tree-small__dist-5__transl_dist--5__transl-wide__size-30000': '20221115',
    '20221130.transl__arg-AA__frml-smpl__tree-1__dist-5__transl_dist--5__transl-wide__size-30000': '20221115',

    '20221203.first_exp__arg-RT__frml-smpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-RT__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-AA__frml-cmpl__dist-20__transl-nrrw__tree-1__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000': '20221203',


    '20221203.first_exp__arg-RT__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': '20221203',

    # ---------------------------------- 20221216 additional experiments ------------------------------------
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-0__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-smpl__dist-20__transl-nrrw__tree-3__dataset_size-30000': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000': '20221203',

    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP': '20221203',
    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-8__dataset_size-30000.G_MP': '20221203',

    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT.G_MP': '20221203',
    '20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000__dpth-RT': '20221203',

    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.G_MP': '20221203',

    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-5__dataset_size-30000.G_MP': '20221203',
    '20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-100000.G_MP': '20221203',

    # ---------------------------------- 20221217.back_to_the_past ------------------------------------
    '20221217.back_to_the_past__arg-FLNL__frml-cmpl__dist-10__transl-wide__tree-10__dataset_size-100000': '20221203',

    # ---------------------------------- 20230529.use_fixed_translation_for_LLM ------------------------------------
    '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': '20221203',
    '20230529.use_fixed_translation_for_LLM.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-8__dataset_size-30000': '20221203',

    # ---------------------------------- 20230615.formula_checkers ------------------------------------
    # '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000': '20221203',
    # '20230615.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': '20221203',

    # ---------------------------------- 20230616.formula_checkers ------------------------------------
    '20230616.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': '20221203',

    # ---------------------------------- 20230621.formula_checkers ------------------------------------
    '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems': '20221203',
    '20230621.formula_checkers.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.wo_theorems.wo_translation_dist': '20221203',

    # ---------------------------------- 20230626.many_bugs_fixed ------------------------------------
    '20230626.many_bugs_fixed.20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.20221203.first_exp__arg-FLNL__frml-cmpl__dist-20__transl-wide__tree-3__dataset_size-30000.plus_quantifiers': '20230626.many_bugs_fixed',

    '20230626.many_bugs_fixed.D3.hard': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.dist-trees': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.unk-0.1': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.brnch-high': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.dist-neg-1.0': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.dist-neg-0.5': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.dist-neg-0.0': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D3.hard.dist-trees-only': '20230626.many_bugs_fixed',

    '20230626.many_bugs_fixed.D8.hard': '20230626.many_bugs_fixed',
    '20230626.many_bugs_fixed.D8.hard.dist-trees': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230701.finalize ------------------------------------
    '20230701.D3.default': '20230626.many_bugs_fixed',
    '20230701.D3.debug': '20230626.many_bugs_fixed',
    '20230701.D3.wo_transl_dist': '20230626.many_bugs_fixed',
    '20230701.D3.brnch-small': '20230626.many_bugs_fixed',
    '20230701.D3.dist-small': '20230626.many_bugs_fixed',
    '20230701.D3.default.refactor_test': '20230626.many_bugs_fixed',
    '20230701.D3.default.dist-tree-triple': '20230626.many_bugs_fixed',
    '20230701.D3.default.dist-tree-quadruple': '20230626.many_bugs_fixed',

    '20230701.D8.default': '20230626.many_bugs_fixed',


    # ---------------------------------- 20230706.finalize ------------------------------------
    '20230706.finalize.D3.dist-double': '20230626.many_bugs_fixed', 
    '20230706.finalize.D3.dist-quadruple': '20230626.many_bugs_fixed', 
    '20230706.finalize.D8.dist-double': '20230626.many_bugs_fixed', 
    '20230706.finalize.D8.dist-quadruple': '20230626.many_bugs_fixed', 


    # ---------------------------------- 20230707.finalize ------------------------------------
    '20230707.finalize.D3.dist-double': '20230626.many_bugs_fixed', 
    '20230707.finalize.D3.dist-triple': '20230626.many_bugs_fixed', 
    '20230707.finalize.D3.dist-quadruple': '20230626.many_bugs_fixed', 

    '20230707.finalize.D8.dist-double': '20230626.many_bugs_fixed', 
    '20230707.finalize.D8.dist-triple': '20230626.many_bugs_fixed', 
    '20230707.finalize.D8.dist-quadruple': '20230626.many_bugs_fixed', 

    # ---------------------------------- 20230711.finalize ------------------------------------
    '20230711.dist-fallback': '20230626.many_bugs_fixed',
    '20230711.finalize.D3': '20230626.many_bugs_fixed',
    '20230711.finalize.D8': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230718.case_study ------------------------------------
    '20230718.case_study.D3.dist-mixture': '20230626.many_bugs_fixed',
    '20230718.case_study.D3.num_dist-wide': '20230626.many_bugs_fixed',
    '20230718.case_study.D3.dist-mixture.num_dist-wide': '20230626.many_bugs_fixed',
    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_logE': '20230626.many_bugs_fixed',
    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_log10': '20230626.many_bugs_fixed',
    '20230718.case_study.D3.dist-mixture.num_dist-wide.transl_vol_log10.adj_verb_noun_equal': '20230626.many_bugs_fixed',
    '20230718.case_study.D8.dist-mixture.num_dist-wide': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230729.case_study_finalize ------------------------------------
    '20230729.case_study_finalize.D3': '20230626.many_bugs_fixed',
    '20230729.case_study_finalize.D8': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230826.jpn ------------------------------------
    '20230826.jpn.D3': '20230626.many_bugs_fixed',
    '20230826.jpn.D8': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230901.random_transitive_verbs ------------------------------------
    '20230901.random_transitive_verbs.D3': '20230626.many_bugs_fixed',
    '20230901.random_transitive_verbs.D8': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230904.jpn ------------------------------------
    '20230904.jpn.D1.wo_brnch.wo_dstrct': '20230626.many_bugs_fixed', 
    '20230904.jpn.D1.wo_brnch': '20230626.many_bugs_fixed', 
    '20230904.jpn.D1': '20230626.many_bugs_fixed', 
    '20230904.jpn.D3': '20230626.many_bugs_fixed', 

    # ---------------------------------- 20230912.jpn ------------------------------------
    '20230912.jpn.D3': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230914.jpn ------------------------------------
    '20230914.jpn.D3': '20230626.many_bugs_fixed',

    # ---------------------------------- 20230916.jpn ------------------------------------
    '20230916.jpn.D1_wo_dist': '20230626.many_bugs_fixed',
    '20230916.jpn.D1': '20230626.many_bugs_fixed',
    '20230916.jpn.D3': '20230626.many_bugs_fixed',
    '20230916.jpn.D5': '20230626.many_bugs_fixed',

    # ---------------------------------- 20231010.D3.large_vocab ------------------------------------
    '20231010.D3.large_vocab': '20230626.many_bugs_fixed',

    # ---------------------------------- 20231012.D3.large_vocab ------------------------------------
    '20231012.D3.large_vocab': '20230626.many_bugs_fixed',
    '20231012.D3.large_vocab.smpl_stncs': '20230626.many_bugs_fixed',
    '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3': '20230626.many_bugs_fixed',
    '20231012.D3.large_vocab.smpl_stncs.cntx_shffls-3.trnsl_vrnts-3': '20230626.many_bugs_fixed',

    # ---------------------------------- 20231018.knowledge.D3 ------------------------------------
    '20231018.knowledge.D3': '20231018.thing_person_config_translation',
    '20231018.knowledge.D3.w_knowledge': '20231018.thing_person_config_translation',
    '20231018.knowledge.D3.w_knowledge.complex-0.3': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231021.knowledge.D3 ------------------------------------
    '20231021.knowledge.D3': '20231018.thing_person_config_translation',
    '20231021.knowledge.D3.complex-0.3': '20231018.thing_person_config_translation',
    '20231021.knowledge.D3.complex-0.3.w_knowledge': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231028.knowledge ------------------------------------
    '20231028.knowledge.D3': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231029.knowledge ------------------------------------
    '20231029.knowledge.D3': '20231018.thing_person_config_translation',
    '20231029.knowledge.D3.wo_knowledge': '20231018.thing_person_config_translation',
    '20231029.knowledge.D3.wo_knowledge.cmplx-0.5': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231030.knowledge ------------------------------------
    '20231030.knowledge.D3.knowledge_factor-1.0': '20231018.thing_person_config_translation',
    '20231030.knowledge.D3.knowledge_factor-5.0': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231103.knowledge.D3 ------------------------------------
    '20231103.knowledge.D3.knowledge_factor-5.0': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231203.jpn ------------------------------------
    '20231203.jpn.D1_wo_dist': '20231018.thing_person_config_translation',
    '20231203.jpn.D1': '20231018.thing_person_config_translation',
    '20231203.jpn.D3': '20231018.thing_person_config_translation',
    '20231203.jpn.D5': '20231018.thing_person_config_translation',
    '20231203.jpn.D8': '20231018.thing_person_config_translation',

    # ---------------------------------- 20231213.jpn ------------------------------------
    '20231213.jpn.D1_wo_dist': '20231018.thing_person_config_translation',
    '20231213.jpn.D1': '20231018.thing_person_config_translation',
    '20231213.jpn.D3': '20231018.thing_person_config_translation',
    '20231213.jpn.D5': '20231018.thing_person_config_translation',
    '20231213.jpn.D8': '20231018.thing_person_config_translation',

    # ---------------------------------- 20230115.jpn ------------------------------------
    '20230115.jpn.BCCWJ.D3': '20231018.thing_person_config_translation',
    '20230115.jpn.punipuni.D3': '20231018.thing_person_config_translation',

    # ---------------------------------- 20230116.jpn ------------------------------------
    '20230116.jpn.wordnet.D3': '20231018.thing_person_config_translation',
    '20230116.jpn.BCCWJ.D3.argument_pred_arg_only': '20231018.thing_person_config_translation',
    '20230116.jpn.punipuni.D3.argument_pred_arg_only': '20231018.thing_person_config_translation',

    # ---------------------------------- 20230116.jpn ------------------------------------
    '20230118.jpn.wordnet.D3': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.argument_pred_arg_only': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.argument_pred_arg_only.no_kaku': '20231018.thing_person_config_translation',
    '20230118.jpn.BCCWJ.D3': '20231018.thing_person_config_translation',
    '20230118.jpn.punipuni.D3': '20231018.thing_person_config_translation',

    # ---------------------------------- 20230118.jpn.ICL ------------------------------------
    '20230118.jpn.wordnet.D3.extension-3.distractor-10': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-3.distractor-5': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-3.distractor-3': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-2.distractor-5': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-2.distractor-3': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-1.distractor-5': '20231018.thing_person_config_translation',
    '20230118.jpn.wordnet.D3.extension-1.distractor-3': '20231018.thing_person_config_translation',

    # ---------------------------------- 20230120.jpn.punipuni ------------------------------------
    '20230120.jpn.wordnet.D3': '20231018.thing_person_config_translation',

    '20230120.jpn.wordnet_repro_w_proposition.D1_wo_dist': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_w_proposition.D1': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_w_proposition.D3': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_w_proposition.D8': '20231018.thing_person_config_translation',

    '20230120.jpn.wordnet_repro_wo_proposition.D1_wo_dist': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_wo_proposition.D1': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_wo_proposition.D3': '20231018.thing_person_config_translation',
    '20230120.jpn.wordnet_repro_wo_proposition.D8': '20231018.thing_person_config_translation',

    '20230120.jpn.BCCWJ.D1_wo_dist': '20231018.thing_person_config_translation',
    '20230120.jpn.BCCWJ.D1': '20231018.thing_person_config_translation',
    '20230120.jpn.BCCWJ.D3': '20231018.thing_person_config_translation',
    '20230120.jpn.BCCWJ.D8': '20231018.thing_person_config_translation',

    '20230120.jpn.punipuni.D1_wo_dist': '20231018.thing_person_config_translation',
    '20230120.jpn.punipuni.D1': '20231018.thing_person_config_translation',
    '20230120.jpn.punipuni.D3': '20231018.thing_person_config_translation',
    '20230120.jpn.punipuni.D8': '20231018.thing_person_config_translation',


    # ---------------------------------- 20230122.jpn.ICL ------------------------------------
    '20230122.jpn.ICL.punipuni.D1_wo_dist': '20231018.thing_person_config_translation',
    '20230122.jpn.ICL.punipuni.D1': '20231018.thing_person_config_translation',
    '20230122.jpn.ICL.punipuni.D3_wo_dist': '20231018.thing_person_config_translation',
    '20230122.jpn.ICL.punipuni.D3': '20231018.thing_person_config_translation',
}


def get_dataset_setting(name: str) -> Dict:
    setting = copy.deepcopy(_DEFAULT_DATASET_SETTINGS[_DATASET_NAME_TO_DEFAULT[name]])
    setting.update(copy.deepcopy(_DATASET_SETTINGS[name]))
    return setting


def maybe_option(option: str, value: Any) -> str:
    if value is None:
        return ''
    else:
        return f'{option} {value}'
