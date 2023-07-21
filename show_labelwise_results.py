#!/usr/bin/env python
import json
from pprint import pformat
import logging
from pathlib import Path
from collections import defaultdict

import click
from logger_setup import setup as setup_logger


logger = logging.getLogger(__name__)



@click.command()
@click.argument('input_jsonl_path')
@click.argument('output_txt_path')
def main(input_jsonl_path, output_txt_path):
    setup_logger(do_stderr=True, level=logging.INFO)
    output_txt_path = Path(output_txt_path)

    labelwise_formulas = defaultdict(list)
    for line in open(input_jsonl_path):
        instance = json.loads(line.rstrip('\n'))
        labelwise_formulas[instance['proof_label']].append(instance['hypothesis_formula'])

    output_txt_path.parent.mkdir(exist_ok=True, parents=True)
    with open(str(output_txt_path), 'w') as f_out:
        for label in ['PROVED', 'DISPROVED', 'UNKNOWN']:
            formulas = labelwise_formulas[label]
            print('\n\n', file=f_out)
            print(f'====================== {label} ========================', file=f_out)
            for formula in sorted(formulas):
                print(f'    {formula}', file=f_out)



if __name__ == '__main__':
    main()
