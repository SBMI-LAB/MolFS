"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

import operator
from collections import defaultdict
from collections import deque

import numpy as np

from reedsolo import RSCodec, ReedSolomonError
from robust_solition import PRNG
from transpose import codons_to_hex


class Pool:
    """
    This class sets up the main functionality for decoding a dataset based on
    multiple nucleotide sequences. The init method sets up class attributes,
    including the needed random number generators. The main decoding logic is
    in the add_dna(), _update_entry() and _process_singles() methods.

    Args:
        num_segments (int): number of segments the decoded data will have
        mapping (object): the mapping object for converting codons to hex
        args: arguments provided for decoding
        flag_correct (boolean): check error correction code or just parse out
    Returns: None
    """

    def __init__(self, num_segments, mapping, args, flag_correct=True):
        self.num_segments = num_segments
        self.segments = [None] * num_segments
        self.mapping = mapping
        self.seed_size = args.seed_size
        self.bytes_per_seq = args.size
        self.droplets_per_segment = defaultdict(set)
        self.done_segments = set()
        self.droplets_list = defaultdict()
        self.singles_q = deque()

        self.PRNG = PRNG(K=self.num_segments, delta=args.delta, c=args.c_dist)

        self.max_hamming = 0
        self.ec = args.rs
        self.RSCodec = RSCodec(self.ec)
        self.correct = flag_correct
        self.seen_seeds = set()

    def _check_ec(self, data):
        """
        Check the error correction code if available and specified,
        otherwise just remove any possible error correction code bytes
        and return the corrected data without the analyzed code

        Args:
            data (int list): The byte list including the potential
                              error correction code
        Returns:
            data_corrected (int list): The byte list with the error
                              correction code evaluated and/or removed
        """
        if self.ec > 0:
            # there is an error correcting code
            if self.correct:  # we want to evaluate the error correcting code
                try:
                    data_corrected = list(self.RSCodec.decode(data))
                except ReedSolomonError:
                    return -1  # could not correct the code

                # we will encode the data again to evaluate the correctness of the decoding
                data_again = list(self.RSCodec.encode(data_corrected))  # list is to convert byte list to int

                if np.count_nonzero(data != list(data_again)) > self.max_hamming:
                    # measuring hamming distance between raw input and expected raw input
                    # too many errors to correct in decoding
                    return -1
            else:  # we don't want to evaluate the error correcting code (e.g. speed)
                data_corrected = data[0:len(data) - self.ec]  # just parse out the error correcting part
        else:
            # There was no error correction code. So we won't correct anything
            data_corrected = data

        return data_corrected

    def _parse_strand(self, data):
        """
        Split the given byte data into the seed value
        and the data byte list

        Args:
            data (int list): The combined seed and data bytes to split
        Returns:
            seed (int): The recovered seed part of the data
            payload (int list): The recovered byte payload of the data
        """
        seed_array = data[:self.seed_size]
        seed = sum([x * 256 ** i for i, x in enumerate(seed_array[::-1])])
        payload = data[self.seed_size:]
        return seed, payload

    def _add_droplet(self, droplet):
        """
        For each segment index in the given droplet's list,
        add the droplet to the corresponding index in the
        droplets_per_segment dictionary data structure

        Args:
            droplet: The given droplet to add to the dictionary
        Returns: None
        """
        for index in self.droplets_list[droplet]['segments_indexes']:
            self.droplets_per_segment[index].add(droplet)

    def _update_entry(self, seed):
        """
        For a given droplet (referenced by the seed). If the droplet
        contains one segment, calls _process_singles(), else, remove all
        previously recovered segments from the current droplet. If any
        single-segments are produced in the process add them to the global
        queue variable. Finally, process all single-segments in the queue
        before exiting the method.

        Args:
            seed : the value referencing the droplet to be processed
        Returns: None
        """
        droplet = self.droplets_list[seed]
        if droplet['degree'] == 1:
            # self._process_singles(droplet)
            self._process_singles(self.droplets_list.pop(seed))
        else:
            for other_index in set(droplet['segments_indexes']).intersection(self.done_segments):
                droplet['payload'] = list(map(operator.xor, self.segments[other_index], droplet['payload']))
                droplet['segments_indexes'].remove(other_index)
                droplet['degree'] -= 1
                self.droplets_per_segment[other_index].remove(seed)
            if droplet['degree'] == 1:
                self.singles_q.append(seed)

        while len(self.singles_q) > 0:
            # other_droplet = self.droplets_list[self.singles_q.popleft()]
            other_droplet = self.droplets_list.pop(self.singles_q.popleft())
            self._process_singles(other_droplet)

    def _process_singles(self, droplet):
        """
        Processes a droplet with one segment left and propagates the
        recovered segment throughout the other droplets that also contain
        that segment. If other single-segments are created in the process,
        then they are added to the global queue variable.

        Args:
            droplet : The droplet to process
        Returns: None
        """
        next_index = min(droplet['segments_indexes'])
        self.segments[next_index] = droplet['payload']
        self.done_segments.add(next_index)
        for other_seed in self.droplets_per_segment[next_index].copy():
            if other_seed in self.droplets_list:
                other_droplet = self.droplets_list[other_seed]
                if other_droplet['degree'] > 1:
                    other_droplet['payload'] = list(map(operator.xor, other_droplet['payload'], droplet['payload']))
                    other_droplet['segments_indexes'].discard(next_index)
                    other_droplet['degree'] -= 1
                    self.droplets_per_segment[next_index].discard(other_seed)
                    if other_droplet['degree'] == 1:
                        self.singles_q.append(other_seed)

    def add_dna_enc(self, droplet_in):
        """
        """
        seed_in = droplet_in['seed']
        self.droplets_list[seed_in] = {'degree': droplet_in['degree'],
                                       'segments_indexes': droplet_in['indexes'],
                                       'payload': droplet_in['payload']}
        self._add_droplet(seed_in)
        self._update_entry(seed_in)

    def add_dna(self, dna_string):
        """
        Takes the given sequence and parses the seed and payload while
        checking the error correction code. Then uses the seed and a
        PRNG to get the corresponding list of segment indexes.
        Uses that information to create a droplet and process it. (No
        longer using the Droplet class, just add values to a dictionary,
        which can be accessed by the seed value).

        Args:
            dna_string (string): The nucleotide sequence to decode
        Returns:
            seed (int): The corresponding seed value for the given sequence
        """

        data = codons_to_hex(dna_string, self.mapping)
        if data == -1:  # Could not decode string with map
            return -1

        data_corrected = self._check_ec(data)
        if data_corrected == -1:  # Could not recover with RS
            return -1

        seed, payload = self._parse_strand(data_corrected)
        if len(payload) != self.bytes_per_seq:
            # print ("bad payload")
            return -1

        # more error detection (filter seen seeds)
        if seed in self.seen_seeds:
            return -1
        self.seen_seeds.add(seed)

        # create droplet from DNA
        self.PRNG.set_seed(seed)
        _, degree, ix_samples = self.PRNG.get_src_blocks()

        self.droplets_list[seed] = {'degree': degree,
                                    'segments_indexes': set(ix_samples),
                                    'payload': payload}

        self._add_droplet(seed)
        self._update_entry(seed)

        return seed

    def num_seen_seeds(self):
        """
        Getter method for the number of seen seeds

        Args: None
        Returns: Number of seen seeds
        """
        return len(self.seen_seeds)

    def num_done_segments(self):
        """
        Getter method for the number of decoded segments

        Args: None
        Returns: Number of decoded segments
        """
        return len(self.done_segments)

    def get_string(self):
        """
        Return the string representation of the final
        decoded data segments (for writing to output file)

        Args: None
        Returns:
            res (string): The decoded data
        """
        return self.segments

    def is_done(self):
        """
        Checks to see if enough dna strands have been
        decoded to uncover all data segments

        Args: None
        Returns: boolean: True if done, False otherwise
        """
        if self.num_segments > len(self.done_segments):
            return False
        return True
