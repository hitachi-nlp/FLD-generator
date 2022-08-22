import random
import json
from pathlib import Path
import logging
from pprint import pformat

import click
from tqdm import tqdm
from formal_logic.argument import Argument
from formal_logic.generators import FormalLogicGenerator
from formal_logic.distractors import UnkownPASDistractor
from formal_logic.translators import SentenceWiseTranslator
from formal_logic.tree_pipeline import TreePipeline
from formal_logic.dataset import NLProofSDataset
from logger_setup import setup as setup_logger

logger = logging.getLogger(__name__)


@click.command()
@click.argument('output-path')
@click.argument('argument-config')
@click.argument('translation-config')
@click.argument('size', type=int)
@click.option('--depth', type=int, default=5)
@click.option('--num-distractors', type=int, default=5)
@click.option('--world-assump', default='CWA')
@click.option('--elim-dneg', is_flag=True, default=False)
def main(output_path, argument_config, translation_config, size, depth, num_distractors, world_assump, elim_dneg):
    setup_logger(do_stderr=True, level=logging.INFO)
    random.seed(0)

    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True, parents=True)

    arguments = [Argument.from_json(json_obj) for json_obj in json.load(open(argument_config))]
    generator = FormalLogicGenerator(arguments, elim_dneg=elim_dneg)

    distractor = UnkownPASDistractor()

    sentence_translations = json.load(open(translation_config))
    translator = SentenceWiseTranslator(sentence_translations)

    tree_pipeline = TreePipeline(generator, distractor=distractor, translator=translator)

    dataset = NLProofSDataset(tree_pipeline, world_assump,
                              depth=depth, num_distractors=num_distractors)

    with open(output_path, 'w') as f_out:
        for nlproof_json, proof_tree, distractors in tqdm(dataset.generate(size)):
            logger.info('')
            logger.info('')
            logger.info('')
            logger.info('=================== generating proof tree =========================')

            logger.info('')
            logger.info('--------------- tree --------------')
            logger.info(proof_tree.format_str)

            logger.info('')
            logger.info('--------------- distractors --------------')
            logger.info(str(distractors))

            logger.info('')
            logger.info('--------------- NLProofs json --------------')
            logger.info(pformat(nlproof_json))

            print(json.dumps(nlproof_json), file=f_out)


if __name__ == '__main__':
    main()
