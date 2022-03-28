import logging

MODULE_LOGGER = 'swagger_gen'


def _get_console_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    return handler


def _get_logger():
    logger = logging.getLogger(MODULE_LOGGER)
    logger.setLevel(logging.INFO)
    logger.addHandler(_get_console_handler())

    return logger


_logger = _get_logger()


def get_logger():
    return _logger
