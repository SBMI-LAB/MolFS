import logging
import sys
import os


def get_logger(verbose=None, logger_name=__name__):
    """
    Format the logger to show the debug information
    :param: verbose: 0 -> Print only error. This is the default.
                     1 -> Print debug, information, warning and error
                     2 -> Print information, warning and error
                     3 -> Print warning and error
    :return: Logger
    """
    if not verbose:
        # get it from environmental variable
        # if it is not set then default value is 0
        verbose = int(os.environ.get("seqNAM_verbose", "0"))
    logger = logging.getLogger(logger_name)
    # Add only one handler.
    # During simulation multiple decoding is done at a single time.
    # so it adds multiple logger
    if len(logger.handlers) > 0:
        return logger
    stream_handler = logging.StreamHandler(sys.stdout)
    if verbose == 1:
        stream_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif verbose == 2:
        stream_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif verbose == 3:
        stream_handler.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    else:
        stream_handler.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)

    stream_handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

    logger.addHandler(stream_handler)

    return logger
