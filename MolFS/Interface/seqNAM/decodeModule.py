"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

import argparse
import csv
import os
import sys

#import namedtuple

from collections import defaultdict

from mapping import MapObject
from pool import Pool
from log import get_logger
from Bio import SeqIO

"""
 decode.py

This file includes the main method for running the decoding 
algorithm program. Functionality includes, parsing command 
line arguments, creating a pool object and running the 
main loop. The main loop reads and processes dna sequences. 
It also keeps track of seen seed values.

"""


def read_args():
    """
    Parses the command line arguments
    and sets up user feedback for use

    Args: None
    Returns: data structure with all given arguments
    """

    parser = argparse.ArgumentParser(description="Decode a given list of DNA sequences to the original data.")
    parser.add_argument("--config_file", help="parameters can be found on the first line of the input file",
                        action='store_true')
    parser.add_argument("-f", "--file_in", nargs="+", help="List of file to decode.", required=True)
    parser.add_argument("-n", "--num_segments", help="the total number of segments in the decoded file", type=int)
    parser.add_argument("-l", "--size", help="number of information bytes per sequence", default=32, type=int)
    parser.add_argument("-p", "--padding", help="number of bytes of padding added to file during encoding", default=0,
                        type=int)
    parser.add_argument("--delta", help="Degree distribution tuning parameter", default=0.05, type=float)
    parser.add_argument("--c_dist", help="Degree distribution tuning parameter", default=0.1, type=float)
    parser.add_argument("--rs", help="number of bytes for rs codes", type=int)
    parser.add_argument("--map", help="File that contains mapping scheme")
    parser.add_argument("--no_correction", help="Skip error correcting", action='store_true')
    parser.add_argument("--out", help="Output file", required=True, type=str)
    parser.add_argument("--seed_size", help="Used in conjunction with web app", default=4)
    parser.add_argument("--verbose", help="Show details of the decoding steps", type=int, default=1)
    parser.add_argument("--primer_length", help="Length of the primer. Primers will be ignored from the decoding "
                                                "process", type=int, default=0)
    parser.add_argument("--file_format", help="Formats of the file. options: csv, fasta, fastaq", default="fastq")

    args = parser.parse_args()
    return args


def seqNAMdecode(args=None):
    """
    Creates a pool object, then reads
    and processes dna sequences until done

    Args: None
    Returns: None
    """
    if not args:
        # If no argument was passed then read that from the console
        args = read_args()
    # Setting verbose as the environmental variable so that other file can also access that
    os.environ["seqNAM_verbose"] = str(args.verbose)
    logger = get_logger(args.verbose, "Decoder")
    # sequences can be distributed in multiple files.
    # We will use all the file for decoding
    # If there is a single file we will convert that into list to make this simpler
    args.file_in = args.file_in if isinstance(args.file_in, list) else [args.file_in]
    # Setting arguments from the config line
    if args.config_file:
        # config will be in the first file
        with open(args.file_in[0], 'r') as cf:
            config_line = cf.readline().rstrip('\n')
            params = config_line.split()
            try:
                args.num_segments = int(params[params.index("-n") + 1])
                args.size = int(params[params.index("-l") + 1])
                args.padding = int(params[params.index("-p") + 1])
                args.delta = float(params[params.index("--delta") + 1])
                args.c_dist = float(params[params.index("--c_dist") + 1])
                args.rs = int(params[params.index("--rs") + 1])
                args.map = params[params.index("--map") + 1]
                args.seed_size = int(params[params.index("--seed_size") + 1])
            except IndexError:
                logger.error("Could not read parameters from config file, %s", args.file_in)
                sys.exit()

    # Store the hex-to-codon mapping information
    read_map = MapObject(args.map)

    # Decoder
    p = Pool(args.num_segments,
             mapping=read_map,
             args=args,
             flag_correct=not args.no_correction)

    line = 0  # total sequences
    errors = 0  # total erroneous sequences
    seen_seeds = defaultdict(int)

    # Main loop
    for i, file in enumerate(args.file_in):

        if args.file_format == "csv":
            f = open(file)
            if i == 0 and args.config_file:
                next(f)
            file_reader = csv.DictReader(f)
        else:
            file_reader = SeqIO.parse(file, format=args.file_format)

        for row in file_reader:
            try:
                if args.file_format == "csv":
                    dna = row["sequence"]
                else:
                    dna = str(row.seq)
                # Remove the primer
                dna = dna[args.primer_length: -args.primer_length] if args.primer_length else dna
            except KeyError:
                logger.info("The file Format isn't correct")
                return -1

            if len(dna) == 0:
                logger.info("Finished reading input file!")
                break

            line += 1
            # Add this sequences to our decoder
            seed = p.add_dna(dna)
            if seed == -1:  # reed-solomon error!
                errors += 1
            else:
                seen_seeds[seed] += 1

            if line % 1000 == 0:
                logger.info("After reading %d lines, %d segments are done. So far: %d rejections (%f) %d seen seeds", line,
                            p.num_done_segments(), errors, errors / (line + 0.0), p.num_seen_seeds())

            if p.is_done():
                logger.info("After reading %d lines, %d segments are done. So far: %d rejections (%f) %d seen seeds", line,
                            p.num_done_segments(), errors, errors / (line + 0.0), p.num_seen_seeds())
                logger.info("Done!")
                break
        if args.file_format == "csv":
            f.close()

    if not p.is_done():
        logger.info("Could not decode all file...")
        return -1

    logger.info("Writing to file")
    out_string = p.get_string()
    write_output = open(args.out, 'wb')
    # Write all the sequences without the last sequences
    # the last sequences might contains the padding remove that padding before writing the sequence
    for x in out_string[:-1]:
        write_output.write(bytearray(x))
    # If padding exists then remove that from the last sequences
    if args.padding > 0:
        write_output.write(bytearray(out_string[-1][:-args.padding]))
    else:  # There was no padding so write the entire sequences
        write_output.write(bytearray(out_string[-1]))
    write_output.close()
    # Wait until file is really closed
    # This is useful during the simulation
    while True:
        if write_output.closed:
            logger.info("Done Writing file")
            break
    return 1


