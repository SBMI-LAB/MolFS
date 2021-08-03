from degrade import Degrade
import os
import filecmp
import time
import random
from datetime import date
from collections import namedtuple
import encode
import decode
import numpy as np

result_file_name = str(date.today()).replace("-", "_") + "_result_file.csv"
# Opening the csv for testing result
# Checking if result file already exists or not. If exits then will start the calculation where it was stopped
previous_result = 0
current_number_of_result = 0
if os.path.isfile(result_file_name):
    # File exists so we will just open the files
    testing_result = open(result_file_name, 'r+')
    # getting how many lines has been written so far
    for line in testing_result:
        previous_result += 1
    # The first one is the header. It's not the result so we will subtract one from that
    # previous_result = previous_result - 1
else:
    # File does not exists so we will create the file
    testing_result = open(result_file_name, 'w')

    testing_result.write('File Size(MB),Number of segment,c distribution,delta,Theoretical redundancy,Actual redundancy'
                         ',reed solomon,GC content per strand,Number of backtrack,Total DNA sequence,Theoretical DNA '
                         'sequence,Average degree,Single degree droplets,Sequence discarded,Decoded status,decoding '
                         'cross checked,Insertion percentage,Mutation Percentage,deletion percentage,strand deletion '
                         'percentage,Total mutation,Total deletion,Total Insertion,Total Strand deletion,Error '
                         'concentrated in start and end,Encoding time,Decoding time,Information density (bits/nt),'
                         'Total affected sequence for insertion error, total affected sequence for deletion error,'
                         'Total affected sequence for mutation error,Percentage of affected sequence for insertion '
                         'error, Percentage of affected sequence for mutation error, percentage of affected sequence '
                         'for deletion error,Sequence affected by all kinds of error,Percentage of sequence affected '
                         'by all kinds of error\n')
# Generating random binary file
testing_file_name = 'random_file'
output_file_name = testing_file_name + '.dna'
degraded_file_name = output_file_name + '-degraded'
after_decode_file_name = output_file_name + '-decoded'

# Generate the random file
# Looping through the file
file_sizes = range(1024 * 1024, 51200 * 1024, 1024 * 1024)
# file_sizes = [10*1024*1024*1024]

for file_size in file_sizes:
    # Generate the file
    with open(testing_file_name, 'wb', 0) as fout:
        fout.write(os.urandom(file_size))

    encoding_args = namedtuple('args',
                               'file_in size map delta c_dist rs stop alpha out config_file job_id plate_info '
                               'plate_cells strand_name fwd_primer bwd_primer maximum_gc minimum_gc seed_size verbose')
    encoding_args.file_in = testing_file_name
    encoding_args.size = 32
    encoding_args.map = 'original_map.txt'
    encoding_args.delta = .001
    encoding_args.c_dist = .025
    encoding_args.rs = 2
    encoding_args.alpha = .15
    encoding_args.stop = None
    encoding_args.out = output_file_name
    encoding_args.plate_info = "plate"
    encoding_args.plate_cells = 96
    encoding_args.strand_name = "StrandName-"
    encoding_args.fwd_primer = ""
    encoding_args.bwd_primer = ""
    encoding_args.maximum_gc = .55
    encoding_args.minimum_gc = .45
    encoding_args.seed_size = 4
    encoding_args.config_file = False
    encoding_args.output_format = "sequence_only"
    encoding_args.verbose = 0
    encoding_args.ensure_decode_ability = False

    encoding_starting_time = time.time()
    encoding_info = encode.main(encoding_args)
    encoding_time = time.time() - encoding_starting_time

    # Degrade the file in the loop
    # Degrade option
    seed = 100
    insertion = list(np.linspace(0, .04, 10))
    deletion = list(np.linspace(0, 0.04, 10))
    mutation = list(np.linspace(0, 0.04, 10))
    random.seed(seed)

    for i in range(10):  # run 10 test for each file
        seed += 1
        current_number_of_result += 1
        # Don't need to run this test as it was already ran in previous test
        if previous_result > current_number_of_result:
            continue
        if i == 0:
            degrade = Degrade(encoding_info['args'], deletion=0, insertion=0, mutation=0, start_end_con=1)
        else:
            degrade = Degrade(encoding_info['args'], deletion=random.choice(deletion),
                              insertion=random.choice(insertion), mutation=random.choice(mutation),
                              start_end_con=random.choice([1, 0]))
        degrade_details = degrade.degrade_file(file_in=output_file_name, file_out=degraded_file_name)

        decoding_starting_time = time.time()

        output_args = namedtuple('output_args', 'config_file file_in out no_correction size map delta c_dist '
                                                'rs alpha' ' stop seed_size padding verbose')
        output_args.config_file = False
        output_args.no_correction = False
        output_args.file_in = degraded_file_name
        output_args.out = after_decode_file_name
        output_args.verbose = 0

        output_args.size = 32
        output_args.map = 'original_map.txt'
        output_args.delta = .001
        output_args.c_dist = .025
        output_args.rs = 2
        output_args.alpha = .1
        output_args.seed_size = 4
        output_args.stop = None
        output_args.num_segments = encoding_info['segment']
        output_args.padding = encoding_info['padding']
        output_args.file_format = "csv"
        output_args.primer_length = 0

        decoding_time = time.time()
        decoding_status = decode.main(output_args)
        decoding_time = time.time() - decoding_time

        if decoding_status == 1:
            if filecmp.cmp(testing_file_name, after_decode_file_name):
                decoding_status_crosschecked = 1
            else:
                decoding_status_crosschecked = -1
        else:
            decoding_status_crosschecked = 0

        file_size_in_mb = round(float(os.path.getsize(testing_file_name)) / (1024 * 1024), 2)
        # calculating total redundancy
        testing_result.write(
            f"{file_size_in_mb},{encoding_info['total_number_of_segment']},{encoding_info['args'].c_dist},"
            f"{encoding_info['args'].delta},{encoding_info['args'].alpha},{encoding_info['actual_redundancy']},"
            f"{encoding_info['args'].rs},{encoding_info['average_gc_content_per_strand']},"
            f"{encoding_info['total_backtrack']},{encoding_info['actual_strand_total']},"
            f"{encoding_info['theoretical_stand_total']},{encoding_info['average_degree']},"
            f"{encoding_info['single_degree']},{encoding_info['sequence_discarded']},{decoding_status},"
            f"{decoding_status_crosschecked},{degrade_details['insertion_percentage']},"
            f"{degrade_details['mutation_percentage']},{degrade_details['deletion_percentage']},"
            f"{degrade_details['segment_deletion_percentage']},{degrade_details['total_mutation']},"
            f"{degrade_details['total_deletion']},{degrade_details['total_insertion']},"
            f"{degrade_details['total_segment_deletion']},{degrade_details['start_end_con']},{encoding_time},"
            f"{decoding_time},{encoding_info['information_density']},"
            f"{degrade_details['total_insertion_affected_in_seq']},"
            f"{degrade_details['total_deletion_affected_in_seq']},"
            f"{degrade_details['total_mutation_affected_in_seq']},"
            f"{degrade_details['percentage_insertion_aff_seq']},"
            f"{degrade_details['percentage_mutation_aff_seq']},{degrade_details['percentage_deletion_aff_seq']}"
            f",{degrade_details['total_affected_sequence_for_all_error']},"
            f"{degrade_details['percentage_all_aff_seq']}\n")
        os.fsync(testing_result)
        try:
            os.remove(degraded_file_name)
            os.remove(after_decode_file_name)
        except OSError:
            pass

    # Deleting all the file
    os.remove(output_file_name)
