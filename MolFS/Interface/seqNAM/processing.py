"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

import math
import os
import sys
from hashlib import md5

from log import get_logger

"""
 processing.py

This file includes a helper method for 
reading in a file to encode and breaking 
it up into segments of a given size.

"""

logger = get_logger(logger_name=__name__)


def read_file(file_in, size):
    """
    Reads in the given file and prepares the data for processing
    by dividing into equal length segments (with possible padding)
    and converting each byte to its integer representation

    Args:
        file_in (str): The name of the file to read
        size (int): Number of bytes per segment
    Returns:
        data_array (2D list): list of segments, each segment
                               is a list of integers
    """

    segment_size = size

    try:
        f = open(file_in, 'rb')
    except FileNotFoundError:
        logger.error("%s file not found", file_in)
        sys.exit(0)

    data = f.read()
    original_size = os.path.getsize(file_in)
    logger.debug("Input file has %d bytes", original_size)

    pad = -len(data) % segment_size
    if pad > 0:
        logger.debug("Padded the file with %d zero to have a round number of blocks of data", pad)
    data += str.encode("\0") * pad  # zero padding.
    total_size = len(data)
    logger.info("File MD5 is %s", md5(data).hexdigest())

    num_segments = math.ceil(total_size / segment_size)
    data_array = []
    logger.info("There are %d input segments", num_segments)

    for num in range(num_segments):
        start = segment_size * num
        end = segment_size * (num + 1)
        segment_binary = data[start:end]

        segment_ords = []
        for i in range(segment_size):
            segment_ords.append(segment_binary[i])

        data_array.append(segment_ords)

    return data_array, num_segments, pad
