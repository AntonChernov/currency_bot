# -*- coding: utf-8 -*-
import logging


def initiate_logging(custom_log_format=None, custom_logger=None, log_level=None):

    log = logging.getLogger('aiohttp.access') if not custom_logger else custom_logger
    log.setLevel(logging.DEBUG if not log_level else log.level)
    # f = logging.Formatter('[L:%(lineno)d] %(filename)s # %(levelname)-8s [%(asctime)s]  %(message)s', datefmt = '%d-%m-%Y %H:%M:%S')
    f = logging.Formatter(
        '[%(levelname).1s %(asctime)s %(filename)s: %(lineno)d] %(message)s', datefmt='%d%m%y %H:%M:%S'
    ) if not custom_log_format else custom_log_format
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if not log_level else log_level)
    ch.setFormatter(f)
    log.addHandler(ch)
    return log


_log = initiate_logging()
