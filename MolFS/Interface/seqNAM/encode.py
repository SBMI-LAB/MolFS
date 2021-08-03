"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""
import argparse
import json
import math
import os
import string
import sys

from tqdm import tqdm

from fountain import DNAFountain
from mapping import MapObject
from pool import Pool
from processing import read_file
from log import get_logger

"""
encode.py

This file includes the main method for running the encoding 
algorithm program. Functionality includes, parsing command 
line arguments, creating a fountain object and running the 
main loop. The main loop creates droplet objects. 
It also keeps track of seen seed values.

"""


def read_args():
    """
    Parses the command line arguments
    and sets up user feedback for use

    Args: None
    Returns:
        args: data structure with all parsed arguments
    """

    parser = argparse.ArgumentParser(description="Encode a given file to a list of DNA sequences.")
    parser.add_argument("--config_file", help="parameters can be written to the first line of the output file",
                        action='store_true')
    parser.add_argument("-f", "--file_in", help="file to encode", required=True)
    parser.add_argument("-l", "--size", help="number of information bytes per sequence", default=32, type=int)
    parser.add_argument("--delta", help="Degree distribution tuning parameter", default=0.05, type=float)
    parser.add_argument("--c_dist", help="Degree distribution tuning parameter", default=0.1, type=float)
    parser.add_argument("--rs", help="Number of bytes for rs codes", default=2, type=int)
    parser.add_argument("--map", help="File that contains mapping scheme", required=True)
    parser.add_argument("--stop", help="Maximal number of oligos", default=None, type=int)
    parser.add_argument("--alpha",
                        help="How many more fragments to generate on top of first k (example: 0.1 will generate "
                             "10 percent more fragments)", default=0.07, type=float)
    parser.add_argument("--out", help="File with DNA oligos", required=True)
    parser.add_argument("--plate_info", help="Name of the plate", default="Plate")
    parser.add_argument("--plate_cells", help="Size of the plate. available sizes are 96,384,1536",
                        default=384, type=int)
    parser.add_argument("--strand_name", help="Name of the strand after this name the sequence number will be added",
                        default="seqNAM01-seq")
    parser.add_argument("--fwd_primer", help="Forward primer", default="ACATCCAACACTCTACGCCC")
    parser.add_argument("--bwd_primer", help="Backward primer", default="GTGTGTTGCGGCTCCTATTC")
    parser.add_argument("--maximum_gc", help="Maximum amount of GC content", default=.55)
    parser.add_argument("--minimum_gc", help="Minimum amount of GC content", default=.45)
    parser.add_argument("--seed_size", help="Used in conjunction with web app", default=4, type=int)
    parser.add_argument('--output_format', help="Details of the encoding or only sequences. Available options: "
                                                "sequence_only, sequence_with_details", type=str,
                        default="sequence_details")
    parser.add_argument("--ensure_decode_ability", help="This will ensure that encoded file is decodeable", action="store_true")
    parser.add_argument("--verbose", help="Write details on the console", type=int, default=1)

    args = parser.parse_args()
    return args


def main(args):
    """
    Creates a fountain object, then creates
    enough valid droplet objects until done

    Args: None
    Returns: None
    """
    if args is None:
        args = read_args()
    # Setting verbose as the environmental variable so that other file can also access that
    os.environ["seqNAM_verbose"] = str(args.verbose)

    logger = get_logger(args.verbose, logger_name="Encoder")

    logger.info("Reading the file. This may take a few minutes")

    file_data, num_seg, padding = read_file(args.file_in, args.size)

    read_map = MapObject(args.map)

    used_seeds = dict()
    # Encoder
    f = DNAFountain(data_in=file_data,
                    mapping=read_map,
                    args=args)

    # Decoder
    if args.ensure_decode_ability:
        p = Pool(num_seg, mapping=read_map, args=args)

    logger.info("Upper bounds on packets for decoding is %d (x%f)  with %f probability\n",
                 int(json.loads(f.PRNG.debug())['K_prime']), json.loads(f.PRNG.debug())['Z'],
                 json.loads(f.PRNG.debug())['delta'])

    if args.out == '-':
        out = sys.stdout
    else:
        out = open(args.out, 'w')
        if args.verbose > 0:
            pbar = tqdm(total=f.final, desc="Valid oligos")

    # Write params to header of output file
    if args.config_file:
        out.write("-f " + args.file_in + " -l " + str(args.size) + " --delta " + str(args.delta) +
                  " --c_dist " + str(args.c_dist) + " --rs " + str(args.rs) + " --map " + args.map +
                  " --alpha " + str(args.alpha) + " --out " + args.out +
                  " --job_id " + " -n " + str(num_seg) + " -p " + str(padding) + " --seed_size "
                  + str(args.seed_size) + "\n")
    # find out the reverse complementary of backward primer
    backward_primer_reverse_complementary = ''
    for c in args.bwd_primer[::-1]:
        if c == 'C':
            backward_primer_reverse_complementary += 'G'
        elif c == 'G':
            backward_primer_reverse_complementary += 'C'
        elif c == 'A':
            backward_primer_reverse_complementary += 'T'
        elif c == 'T':
            backward_primer_reverse_complementary += 'A'
    # Writing the top row of the CSV
    if args.output_format == "sequence_details":
        out.write("Plate info,Well position,Strand name,sequence,Core length,Core GC content,Forward primer,"
                  "backward primer,sequence with primer,Length,GC content,Degree,Backtrack required\n")

        #  Generating the alphabet list for putting well position.
        #  We will only generate 32 value because our maximum limit will be 32 for 1536 plate
        # we will need these information if we are printing all the details
        well_vertical_position = list(string.ascii_uppercase)
        well_vertical_position.extend(
            [well_vertical_position[i] + well_vertical_position[j] for i in range(1) for j in range(6)])

        prev_plate = ""
        if args.plate_cells == 96:
            # we will divide by 12
            cell_columns = 12
        elif args.plate_cells == 384:
            # we will divide by 24
            cell_columns = 24
        else:
            cell_columns = 48
    elif args.output_format == "sequence_only":
        out.write("sequence\n")

    # variable that track file's overall gc_content
    total_gc_content = 0
    total_backtrack = 0
    total_degree = 0
    single_degree = 0
    total_strand = 0

    while not f.is_done_redundancy():
        #    while not f.is_done():
        d = f.make_droplet()
        if f.is_valid(d) == 1:
            total_strand += 1
            original_sequence = d.get_DNA_strand()
            original_sequence_len = len(original_sequence)
            original_gc = original_sequence.count('g') + original_sequence.count('c')
            original_gc_percentage = round((original_gc / float(original_sequence_len)) * 100)
            primer_sequence = args.fwd_primer + original_sequence + backward_primer_reverse_complementary
            if d.degree == 1:
                single_degree += 1

            if args.output_format == "sequence_details":
                # figuring out the well position and plate information
                # figuring out the plates position
                current_plate = args.plate_info + "-" + str(int(math.ceil(float(total_strand) / args.plate_cells)))
                if prev_plate == current_plate:
                    current_plate = ""
                else:
                    prev_plate = current_plate
                # figuring out well position
                # we will only work with the remainder of the total_strand and plate_cells.
                # division result will reflect the current plate
                current_plate_wells_position = (total_strand - 1) % args.plate_cells
                current_plate_wells = well_vertical_position[
                    int(math.floor(float(current_plate_wells_position) / cell_columns))]
                current_plate_wells += str((current_plate_wells_position % cell_columns) + 1)
                # finding out the sequence number
                sequence_number = args.strand_name + str(total_strand)
                # finding gc content in original sequence

                # generating the sequence with primer
                primer_sequence = args.fwd_primer + original_sequence + backward_primer_reverse_complementary
                primer_sequence_len = len(primer_sequence)
                primer_gc = primer_sequence.count('g') + primer_sequence.count('c')
                primer_gc_percentage = round((primer_gc / float(primer_sequence_len)) * 100)

                out.write(f"{current_plate},{current_plate_wells},{sequence_number},{original_sequence},"
                          f"{original_sequence_len},{original_gc_percentage},{args.fwd_primer},{args.bwd_primer},"
                          f"{primer_sequence},{primer_sequence_len},{primer_gc_percentage},{d.degree},"
                          f"{d.get_backtrack()}\n")
            elif args.output_format == "sequence_only":
                out.write(f"{primer_sequence}\n")

            if args.ensure_decode_ability:
                p.add_dna(d.get_DNA_strand())

                if p.is_done():
                    f.count_redundancy()
            elif total_strand >= num_seg:
                f.count_redundancy()

            if d.seed in used_seeds:
                logger.error("seed %d has been seen before\ndone", d.seed)
                sys.exit(1)

            used_seeds[d.seed] = 1

            if args.out != '-' and args.verbose > 0:
                pbar.update()

    if args.out != '-' and args.verbose > 0:
        pbar.close()
    logger.info("finished. generated %d packets out of %d tries (%.3f)", f.good, f.tries, (f.good + 0.0) / f.tries)
    logger.info("generated %d for decoding and %d redundancy", (f.good - f.final_redundancy), f.final_redundancy)
    print("segments",num_seg)

    out.close()
    # end main method

    # storing the encoding information and return those for testing purpose
    encoding_file_info = {}
    information_density = float((os.path.getsize(args.file_in) * 8)) / (total_strand * len(d.get_DNA_strand()))
    # calculating the redundancy
    actual_redundancy = round((float(total_strand - num_seg) / num_seg) * 100, 2)
    average_gc_content_per_strand = total_gc_content / total_strand
    encoding_file_info['actual_strand_total'] = total_strand
    encoding_file_info['total_backtrack'] = total_backtrack + ((f.tries - f.good) * 500)
    encoding_file_info['average_gc_content_per_strand'] = average_gc_content_per_strand
    encoding_file_info['theoretical_stand_total'] = math.ceil(num_seg * (1 + args.alpha))
    encoding_file_info['average_degree'] = total_degree / total_strand
    encoding_file_info['sequence_discarded'] = f.tries - f.good
    encoding_file_info['total_number_of_segment'] = num_seg
    encoding_file_info['args'] = args
    encoding_file_info['information_density'] = information_density  # bits/nt
    encoding_file_info['actual_redundancy'] = actual_redundancy
    encoding_file_info['single_degree'] = single_degree
    encoding_file_info['segment'] = num_seg
    encoding_file_info['padding'] = padding

    while True:  # Making sure the file is being closed
        if out.closed:
            break

    return encoding_file_info


if __name__ == '__main__':
    main(args=None)
