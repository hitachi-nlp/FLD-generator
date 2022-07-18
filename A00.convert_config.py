#!/usr/bin/env python
import logging
import json
import copy
from pathlib import Path
from string import Template

import click
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


def convert(config_in_path: str, config_out_path: str):
    config_in = json.load(open(config_in_path))

    schemes = config_in["formal_argument_schemes"]
    schemes_converted = []
    for scheme in schemes:
        scheme_converted = copy.deepcopy(scheme)
        scheme_converted['scheme'] = []
        for ABC_template_formula, ABC2FGH_mapping in scheme['scheme']:
            formula = Template(ABC_template_formula).substitute(ABC2FGH_mapping)
            FGH2ABC_mapping = {}
            for ABC, FGH in ABC2FGH_mapping.items():
                FGH2ABC_mapping[FGH[2]] = f'{ABC}'
            scheme_converted['scheme'].append([formula, FGH2ABC_mapping])
        schemes_converted.append(scheme_converted)

    config_out = copy.deepcopy(config_in)
    config_out['formal_argument_schemes'] = schemes_converted
    Path(config_out_path).parent.mkdir(exist_ok=True, parents=True)
    with open(str(config_out_path), 'w') as f_out:
        json.dump(config_out,
                  f_out,
                  ensure_ascii=False,
                  indent=4)


@click.command()
def main():
    setup_logger(level=logging.INFO)

    convert(
        './configs.org/conf_syllogistic_corpus-01.json',
        './configs/conf_syllogistic_corpus-01.json',
    )

    convert(
        './configs.org/conf_syllogistic_corpus-02.json',
        './configs/conf_syllogistic_corpus-02.json',
    )





if __name__ == '__main__':
    main()
