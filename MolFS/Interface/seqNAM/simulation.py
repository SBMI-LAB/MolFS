from collections import namedtuple
import os
import filecmp
import time
import random
from datetime import date
import encode
import decode

random_file_name = "test"
encoded_file_name = "test_encoded"
degraded_file_name = "test_degraded"
decoded_file_name = "test_decoded"
reed_solomon = 4


encoding_args = namedtuple('args',
                      'file_in size map delta c_dist rs stop alpha out config_file job_id plate_info plate_cells stranc_name fwd_primer bwd_primer maximum_gc minimum_gc seed_size');
encoding_args.file_in = random_file_name
encoding_args.size = 36
encoding_args.map = 'original_map.txt'
encoding_args.delta = .05
encoding_args.c_dist = .1
encoding_args.rs = reed_solomon
encoding_args.alpha = .1
encoding_args.stop = None
encoding_args.config_file = None
encoding_args.out = encoded_file_name
# Golam added this
encoding_args.plate_info = "plate"
encoding_args.plate_cells = 96
encoding_args.strand_name = "StrandName-"
encoding_args.fwd_primer = "ATGCAGCATTAAGGCC"
encoding_args.bwd_primer = "ATGCAGCATTAAGGCC"
encoding_args.maximum_gc = .55
encoding_args.minimum_gc = .45
encoding_args.seed_size = 4
encoding_args.config_file = True

# 1% of each sequence is degraded
def degrade(file_in, file_out):
    nts = ['A', 'T', 'G', 'C']
    file_out_file = open(file_out, "w")
    total_insertion = 0
    total_deletion = 0
    total_mutation = 0
    sequence_affected_by_insertion = 0
    sequence_affected_by_mutation = 0
    sequence_affected_by_deletion = 0
    total_sequence = 0
    with open(file_in, "r") as file_read:
        file_out_file.write(file_read.readline())  # Writing the first row in the degrade file
        file_out_file.write(file_read.readline())  # Writing the first row in the degrade file
        # next(file_read)  # Ignoring the first line
        for line in file_read:
            line = line.rstrip("\n");
            total_sequence += 1
            single_line = line.split(",")
            seq = list(single_line[3])
            seq_len = len(seq)
            number_of_error = int(seq_len * .01) # 1% of each sequence is degraded
            sequence_insertion = 0
            sequence_mutation = 0
            sequence_deletion = 0
            # Now we will randomly insert {number_of_error} errors in these locations
            # Error can be insertion, deletion, mutation
            for i in range(number_of_error):
                # we will randomly choose what types of error we will insert
                # error_type_choice = random.choice(list(range(3)))
                error_type_choice = 0
                if error_type_choice == 0:  # It will be an mutation
                    # Choose random index for mutating
                    random_index_to_mutate = random.choice(list(range(seq_len)))
                    # randomly choose a nt
                    nts_for_this_mutation = nts[:]
                    # we are remvoing the current nt from the list so that we don't pick that randomly
                    nts_for_this_mutation.remove(seq[random_index_to_mutate])
                    seq[random_index_to_mutate] = random.choice(nts_for_this_mutation)
                    total_mutation += 1
                    sequence_mutation += 1
                elif error_type_choice == 1:  # It will be a insertion
                    random_index_to_insert = random.choice(list(range(seq_len)))
                    seq.insert(random_index_to_insert, random.choice(nts))
                    total_insertion += 1
                    sequence_insertion += 1
                else: # It will be a deletion
                    random_index_to_delete = random.choice(list(range(len(seq))))
                    del seq[random_index_to_delete]
                    total_deletion += 1
                    sequence_deletion += 1

            if sequence_insertion > 0:
                sequence_affected_by_insertion += 1
            elif sequence_deletion > 0:
                sequence_affected_by_deletion += 1
            elif sequence_mutation > 0:
                sequence_affected_by_mutation += 1
            # Write back this file
            single_line[3] = "".join(l for l in seq)
            # Add the array element using a comma
            file_out_file.write(",".join(s for s in single_line) +"\n")
    file_out_file.close()
    degrade_details = {}
    degrade_details["total_insertion"] = total_insertion
    degrade_details["total_mutation"] = total_mutation
    degrade_details["total_deletion"] = total_deletion
    degrade_details["sequence_affected_by_mutation"] = round(sequence_affected_by_mutation/total_sequence, 2)
    degrade_details["sequence_affected_by_deletion"] = round(sequence_affected_by_deletion/total_sequence, 2)
    degrade_details["sequence_affected_by_insertion"] = round(sequence_affected_by_insertion/total_sequence, 2)
    while True:
        if file_out_file.closed:
            return degrade_details

def start_simulation():
    file_sizes_to_check = [5120, 10240, 20480, 81920, 1048576, 2097152, 1048576, 10485760, 20971520] * 5 # 5 test for each of the file
    for file_size in file_sizes_to_check:
        with open(random_file_name, 'wb') as fout:
            fout.write(os.urandom(file_size))
        result_file_name = str(date.today()).replace("-", "_")+"_result_file.csv";
        if os.path.isfile(result_file_name):
            result_file = open(result_file_name, "a")
        else:
            result_file = open(result_file_name, "w")
            result_file.write('File size(KB),Number of segment,c_dist,delta,theoretical redundancy,actual redundancy,'
                              'reed solomon,gc content,number of backtrack required,actual_strand_total,theoretical_stand_total,'
            'Average degree,Number of single degree segment,sequence discared,decoding_status,percentage of sequence affected by insertion,'
            'percentage of sequence affected by mutation,percentage of sequence affected by deletion,total_mutation,total_deletion,'
            'total_insertion,encoding_time,decoding_time,info_density\n')
        encoding_time = time.time()
        encoding_info = encode.main(encoding_args)
        encoding_time = time.time() - encoding_time
        degrade_details = degrade(encoded_file_name, degraded_file_name)
        # Start decodnig
        output_args=namedtuple('output_args', 'config_file file_in out no_correction');
        output_args.config_file = True
        output_args.no_correction = False
        output_args.file_in = degraded_file_name
        output_args.out = decoded_file_name
        decoding_time = time.time()
        try:
            decoding_status = decode.main(output_args)
        except Exception as e:
            print(e)
            decoding_status = -2
        decoding_time = time.time() - decoding_time

        if decoding_status == 1: # File recovery successfull
            if(filecmp.cmp(random_file_name, decoded_file_name)): # Cross check
                decoding_status = 1
            else:
                decoding_status = 0

        result_file.write(
            '{file_size},{num_seg},{c_dist},{delta},{alpha},{redundancy},{rs},{gc},{backtrack},{num_seq},{the_num_seq},'
            '{ave_degree},{single_degree},{seq_dis},{decoding_status},{insertion_percentage},'
            '{mutation_percentage},{deletion_percentage},{total_mutation},{total_deletion},'
            '{total_insertion},{encoding_time},{decoding_time},{info_density}\n'.format(
                file_size=file_size, num_seg=encoding_info['total_number_of_segment'],
                c_dist=encoding_info['args'].c_dist, delta=encoding_info['args'].delta,
                alpha=encoding_info['args'].alpha, redundancy=encoding_info['actual_redundancy'],
                rs=encoding_info['args'].rs, gc=encoding_info['average_gc_content_per_strand'],
                backtrack=encoding_info['total_backtrack'], num_seq=encoding_info['actual_strand_total'],
                the_num_seq=encoding_info['theoretical_stand_total'], ave_degree=encoding_info['average_degree'],
                single_degree=encoding_info['single_degree'], seq_dis=encoding_info['sequence_discarded'],
                decoding_status=decoding_status,
                insertion_percentage=degrade_details['sequence_affected_by_insertion'],
                mutation_percentage=degrade_details['sequence_affected_by_mutation'],
                deletion_percentage=degrade_details['sequence_affected_by_deletion'],
                total_mutation=degrade_details['total_mutation'], total_deletion=degrade_details['total_deletion'],
                total_insertion=degrade_details['total_insertion'],
                encoding_time=round(encoding_time, 2), decoding_time=round(decoding_time, 2),
                info_density=round(encoding_info['information_density'], 2)))
        result_file.flush()
    os.remvoe(random_file_name)
    os.remove(encoded_file_name)
    os.remove(degrade_details)
    os.remove(decoded_file_name)

    result_file.close()


if __name__ == '__main__':
    start_simulation()