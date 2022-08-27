import random
import json
from typing import List
from pathlib import Path
from pprint import pformat
import logging

import click
from tqdm import tqdm

from formal_logic.translators import ClauseTypedTranslator
from formal_logic.word_banks import EnglishWordBank
from formal_logic.distractors import SameFormUnkownInterprandsDistractor
from formal_logic.argument import Argument
from formal_logic.proof_tree_generation_pipeline import ProofTreeGenerationPipeline
from formal_logic.proof_tree_generators import ProofTreeGenerator
from formal_logic.datasets import NLProofSDataset

from logger_setup import setup as setup_logger


logger = logging.getLogger(__name__)


def load_arguments(config_paths: List[str]) -> List[Argument]:
    arguments = []
    for config_path in config_paths:
        arguments.extend([Argument.from_json(json_obj)
                          for json_obj in json.load(open(config_path))
                          if not json_obj['id'].startswith('__')])
    return arguments


@click.command()
@click.argument('output-path')
@click.argument('size', type=int)
@click.option('--argument-config', '--ac',
              multiple=True, default=[])
@click.option('--translation-config', '--tc',
              multiple=True, 
              default=['./configs/formal_logic/translations/clause_typed.thing.json'])
@click.option('--depth', type=int, default=5)
@click.option('--complication', type=float, default=0.0)
@click.option('--quantification', type=float, default=0.0)
@click.option('--keep-dneg', is_flag=True, default=False)
@click.option('--distractor-factor', type=float, default=1.0)
@click.option('--world-assump', default='CWA')
def main(output_path,
         argument_config,
         translation_config,
         size,
         depth,
         complication,
         quantification,
         keep_dneg,
         distractor_factor,
         world_assump):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(0)

    if len(argument_config) == 0:
        raise ValueError()

    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    arguments = load_arguments(argument_config)
    generator = ProofTreeGenerator(
        arguments,
        elim_dneg=not keep_dneg,
        complicated_arguments_weight=complication,
        quantified_arguments_weight=quantification,
    )

    distractor = SameFormUnkownInterprandsDistractor(distractor_factor)

    print(translation_config)
    translator = ClauseTypedTranslator(
        {key: value
         for config_path in translation_config
         for key, value in json.load(open(config_path)).items()},
        EnglishWordBank(),
        do_translate_to_nl=True,
    )

    pipeline = ProofTreeGenerationPipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(pipeline, world_assump, depth=depth)

    with open(output_path, 'w') as f_out:
        logger.info('\n\n')
        logger.info('=================== generating proof tree =========================')

        for nlproof_json, proof_tree, distractors, stats in tqdm(dataset.generate(size)):

            logger.info('\n')
            logger.info('--------------- tree --------------')

            logger.info('\n')
            logger.info('\n' + proof_tree.format_str)

            logger.info('\n')
            logger.info('--------------- distractors --------------')
            logger.info('\n' + pformat(distractors))

            logger.info('\n')
            logger.info('--------------- NLProofs json --------------')
            logger.info('\n' + pformat(nlproof_json))

            logger.info('\n')
            logger.info('--------------- stats --------------')
            # logger.info(dict(stats))
            logger.info('\n' + pformat(stats))

            logger.info('\n\n')
            logger.info('=================== generating proof tree =========================')

            print(json.dumps(nlproof_json), file=f_out)


if __name__ == '__main__':
    main()
