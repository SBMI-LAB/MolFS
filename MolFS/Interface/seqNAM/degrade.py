import logging
import os
import sys
import random
from tqdm import tqdm
import csv
import numpy as np

logging.basicConfig(level=logging.DEBUG)


class Degrade:
    def __init__(self, args, start_end_con=0, deletion=0, mutation=0, insertion=0, segment_deletion=0):
        self.start_end_con = start_end_con
        self.deletion = deletion
        self.mutation = mutation
        self.insertion = insertion
        self.segment_deletion = segment_deletion
        self.args = args
        self.first_nt_con = 50
        self.last_nt_con = 50
        self.single_sequence_length = -1

    def read_file(self,file_in):
        sequences = []
        try:
            f_in = open(file_in, 'r')
            # The first will the be the configuration line
            self.config_line = next(f_in)
            self.header = next(f_in)
        except:
            logging.error("%s file not found", file_in)
            return sequences

        for line in f_in:
            sequences.append(line.strip("\n"))

        self.single_sequence_length = len(sequences[0])
        f_in.close()
        return sequences

    def write_file(self, sequences, file_out):

        f_out = open(file_out, 'w')
        f_out.write("{}".format(self.config_line))
        f_out.write("{}".format(self.header))
        for line in sequences:
            f_out.write("{}\n".format(line))

        f_out.close()

    def degrade_file(self,file_in,file_out):
        sequences = self.read_file(file_in)
        #
        total_insertion = 0
        total_mutation = 0
        total_deletion = 0
        total_segment_deletion = 0
        total_mutation_affected_in_seq = set()
        total_deletion_affected_in_seq = set()
        total_insertion_affected_in_seq = set()
        total_affected_sequence_for_all_error = set()

        nts = ["A", "T", "C", "G"]
        sequences_out = []
        total_segment = len(sequences)
        # Get the total number of sequence error
        insertion_sequences = np.random.choice(np.arange(total_segment),int(self.insertion*total_segment),replace=True)
        mutation_sequences = np.random.choice(np.arange(total_segment),int(self.mutation*total_segment),replace=True)
        deletion_sequences = np.random.choice(np.arange(total_segment),int(self.deletion*total_segment),replace=True)
        start_end_con_seq = list(range(self.first_nt_con))+list(range(self.single_sequence_length-self.last_nt_con,self.single_sequence_length))


        for i in insertion_sequences:
            if self.start_end_con == 1:
                #error should be in the beginning and at the end
                error_index=random.choice(start_end_con_seq)
            else:
                #error should be random
                error_index = random.randint(0,self.single_sequence_length)
            random_nt = random.choice(nts)
            sequences[i] = str(sequences[i][:error_index])+str(random_nt)+str(sequences[i][error_index:])
            # sequences[i][3]=str(sequences[i][3][:error_index])+str(random_nt)+str(sequences[i][3][error_index:])
            total_insertion += 1
            total_insertion_affected_in_seq.add(i)
            total_affected_sequence_for_all_error.add(i)

        #Doning the mutation error
        for i in mutation_sequences:
            if(self.start_end_con == 1):
                #error should be in the beginning and at the end
                error_index=random.choice(start_end_con_seq)
            else:
                #error should be random
                error_index = random.randint(0,self.single_sequence_length)
            random_nt = random.choice(nts)

            sequences[i] = str(sequences[i][:error_index]) + str(random_nt) + str(sequences[i][error_index+1:])

            # sequences[i][3]=str(sequences[i][3][:error_index])+str(random_nt)+str(sequences[i][3][error_index+1:])
            total_mutation += 1
            total_mutation_affected_in_seq.add(i)
            total_affected_sequence_for_all_error.add(i)

        #Doing the deletion error
        for i in deletion_sequences:
            if(self.start_end_con == 1):
                #error should be in the beginning and at the end
                error_index=random.choice(start_end_con_seq)
            else:
                #error should be random
                error_index = random.randint(0,self.single_sequence_length)

            sequences[i] = str(sequences[i][:error_index]) + str(sequences[i][error_index+1:])

            # sequences[i][3]=str(sequences[i][3][:error_index])+str(sequences[i][3][error_index+1:])
            total_deletion += 1
            total_deletion_affected_in_seq.add(i)
            total_affected_sequence_for_all_error.add(i)

        self.write_file(sequences,file_out)


        percentage_mutation_aff_seq = round((float(len(total_mutation_affected_in_seq))/total_segment)*100,2)
        percentage_deletion_aff_seq = round((float(len(total_deletion_affected_in_seq))/total_segment)*100,2)
        percentage_insertion_aff_seq = round((float(len(total_insertion_affected_in_seq))/total_segment)*100,2)
        percentage_all_aff_seq = round((float(len(total_affected_sequence_for_all_error))/total_segment)*100,2)

        degrade_details = {}

        degrade_details['total_errors'] = total_deletion + total_mutation + total_insertion
        degrade_details['total_insertion'] = total_insertion
        degrade_details['total_deletion'] = total_deletion
        degrade_details['total_mutation'] = total_mutation
        degrade_details['total_segment_deletion'] = total_segment_deletion
        degrade_details['insertion_percentage'] = self.insertion
        degrade_details['mutation_percentage'] = self.mutation
        degrade_details['deletion_percentage'] = self.deletion
        degrade_details['segment_deletion_percentage'] = self.segment_deletion
        degrade_details['start_end_con'] = self.start_end_con
        degrade_details['total_mutation_affected_in_seq'] = len(total_mutation_affected_in_seq)
        degrade_details['total_deletion_affected_in_seq'] = len(total_deletion_affected_in_seq)
        degrade_details['total_insertion_affected_in_seq'] = len(total_insertion_affected_in_seq)
        degrade_details['percentage_mutation_aff_seq'] = percentage_mutation_aff_seq
        degrade_details['percentage_deletion_aff_seq'] = percentage_deletion_aff_seq
        degrade_details['percentage_insertion_aff_seq'] = percentage_insertion_aff_seq
        degrade_details['percentage_all_aff_seq'] = percentage_all_aff_seq
        degrade_details['total_affected_sequence_for_all_error'] = len(total_affected_sequence_for_all_error)

        return degrade_details
