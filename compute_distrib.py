#!/usr/bin/env python
import math
import random
import json
from typing import List, Dict, Optional
from pathlib import Path
from pprint import pformat
import logging
from collections import defaultdict

import click
from tqdm import tqdm
import dill


@click.command()
@click.argument('input_path', type=str)
@click.argument('output_path', type=str)
def main(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    # ./outputs/10.create_FLD_corpus/20230626.many_bugs_fixed/dataset_name=20230626.many_bugs_fixed.20221203.first_exp__arg-RT__frml-cmpl__dist-20__transl-nrrw__tree-3__dataset_size-30000.G_MP/rsd_objct_nns_mx_fctr=1.0/smpl_hrd_ngtvs=True/try_ngtd_hypthss_frst=True/us_fxd_trnsltn=True/us_smplfd_tr_frmls_as_dstrctr_prttyp=True/test/test.jsonl
    attr_names = [
        'proof_stance',
        'answer',
        'original_tree_depth',
        'depth',

        'negative_original_tree_depth',
        'negative_proof_stance',

        'num_formula_distractors',
        'num_translation_distractors',
        'num_all_distractors',
    ]

    counts = defaultdict(lambda: defaultdict(int))
    tot = 0
    for line in open(input_path):
        instance = json.loads(line.rstrip('\n'))
        for attr_name in attr_names:
            val = instance[attr_name]
            counts[attr_name][val] += 1
        tot += 1

    with open(output_path, 'w') as f_out:
        for attr_name in attr_names:
            print('\n\n\n', file=f_out)
            print(f'------------------ {attr_name} ------------------', file=f_out)
            for val, count in sorted(item for item in counts[attr_name].items() if item[0] is not None):
                print(f'{str(val):<10}    [{count:<6} / {tot}]    {count/tot:.2f}', file=f_out)
            for val, count in sorted(item for item in counts[attr_name].items() if item[0] is None):
                print(f'{str(val):<10}    [{count:<6} / {tot}]    {count/tot:.2f}', file=f_out)



if __name__ == '__main__':
    main()
