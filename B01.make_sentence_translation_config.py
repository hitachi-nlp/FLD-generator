#!/usr/bin/env python
import logging
import json
from pathlib import Path
from string import Template

import click
from logger_setup import setup as setup_logger
from formal_logic.formula import AND, OR, NOT

logger = logging.getLogger(__name__)


def convert_config(config_in_path: str, config_out_path: str):
    config_in = json.load(open(config_in_path))

    translation_config = {key: val for key, val in config_in.items()
                          if key.find('fss+') >= 0}

    converted_config = {}
    for domain_name, domain_config in translation_config.items():
        if domain_name == 'fss+translations':
            converted_name = 'general'
        else:
            converted_name = domain_name.replace('fss+translations_', '')

        converted_config[converted_name] = {}
        for formula, translations in domain_config.items():
            converted_formula = convert_formula(formula)
            converted_config[converted_name][converted_formula] = []
            for translation in translations:
                converted_config[converted_name][converted_formula].append(convert_formula(translation).rstrip(' '))

    Path(config_out_path).parent.mkdir(exist_ok=True, parents=True)
    with open(str(config_out_path), 'w') as f_out:
        json.dump(converted_config,
                  f_out,
                  ensure_ascii=False,
                  indent=4)


def convert_formula(rep: str) -> str:
    rep = rep.replace('$', '')
    rep = rep.replace('&', AND)
    rep = rep.replace('v', OR)
    rep = rep.replace('¬', NOT)
    return rep


@click.command()
def main():
    setup_logger(level=logging.INFO)

    convert_config(
        './configs.org/conf_syllogistic_corpus-02.json',
        './configs/formal_logic/sentence_translations/syllogistic_corpus-02.domains.json',
    )


if __name__ == '__main__':
    main()
