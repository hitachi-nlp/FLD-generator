#!/usr/bin/env python
import logging
import json
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
        scheme_converted = {
            'id': scheme['id'],
            'base_scheme_group': scheme['base_scheme_group'],
            'scheme_variant': scheme['scheme_variant'],
        }

        formulas = []
        for ABC_template_formula, ABC2FGH_mapping in scheme['scheme']:
            ABC2FGH_mapping_wo_template = {
                key: val[2:-1]
                for key, val in ABC2FGH_mapping.items()
            }
            formula = Template(ABC_template_formula).substitute(ABC2FGH_mapping_wo_template)
            formulas.append(formula)

        scheme_converted['premises'] = formulas[:-1]
        scheme_converted['conclusion'] = formulas[-1]

        schemes_converted.append(scheme_converted)

    Path(config_out_path).parent.mkdir(exist_ok=True, parents=True)
    with open(str(config_out_path), 'w') as f_out:
        json.dump(schemes_converted,
                  f_out,
                  ensure_ascii=False,
                  indent=4)


@click.command()
def main():
    setup_logger(level=logging.INFO)

    # convert(
    #     './configs.org/conf_syllogistic_corpus-01.json',
    #     './configs/formal_logic/syllogistic_corpus-01.json',
    # )

    convert(
        './configs.org/conf_syllogistic_corpus-02.json',
        './configs/formal_logic/syllogistic_corpus-02.json',
    )


if __name__ == '__main__':
    main()
