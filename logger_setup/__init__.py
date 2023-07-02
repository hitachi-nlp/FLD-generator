import logging
from typing import Union, List
from pathlib import Path

import colorlog

logger = logging.getLogger(__name__)


def blockAddingHandler(logger, handler, *args, **kwargs) -> None:
    logger.warning('Could not add handler %s since "block_other_handlers" option is used in logger_setup.setup().', str(handler))


def setup(logger = None,
          filepaths: List[Union[str, Path]] = None,
          do_stderr=True,
          level: str = 'INFO',
          block_other_handlers=False,
          clear_other_handlers=False):
    filepaths = filepaths or []
    logger = logger or logging.getLogger()
    logger.setLevel(level)

    handlers = []

    if clear_other_handlers:
        logging.getLogger().handlers.clear()

    if do_stderr:
        handlers.append(create_stream_handler())

    for filepath in filepaths:
        handlers.append(create_file_handler(filepath))
        logger.info('logging to "%s"', filepath)

    for handler in handlers:
        logger.addHandler(handler)

    if block_other_handlers:
        logger.addHandler = lambda handler: blockAddingHandler(logger, handler)


def create_stream_handler():
    handler = logging.StreamHandler()
    _format_handler(handler)
    return handler


def create_file_handler(filepath: str):
    _filepath = Path(filepath)
    if _filepath.exists():
        _filepath.unlink()
    _filepath.parent.mkdir(exist_ok=True, parents=True)
    handler = logging.FileHandler(str(_filepath))
    _format_handler(handler)
    return handler


def _format_handler(handler) -> None:
    handler.setFormatter(
        colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(process)d] %(levelname)s %(name)s %(cyan)s%(message)s'))
