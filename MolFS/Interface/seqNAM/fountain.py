"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

import operator
from robust_solition import PRNG
from lfsr import lfsr, lfsr32p, lfsr32s
from droplet import Droplet


class DNAFountain:
    """
    This class sets up the main functionality for encoding data. The init
    method sets up class attributes, including the needed random number
    generators. The main functionality is in the make_droplet() method.
    The rest are mostly helper methods.

    Args:
        data_in (2D list of ints): list of segments, bytes represented by ints
        mapping (object): the mapping object for converting hex to codons
        args (object): Arguments for this encoding/decoding
    Returns: None
    """

    def __init__(self, data_in, mapping, args):

        self.data_in = data_in
        self.mapping = mapping
        self.num_segments = len(data_in)
        self.alpha = args.alpha
        self.stop = args.stop
        self.final = self._calc_stop()
        self.final_redundancy = self._calc_redundancy()

        # starting an lfsr with a certain state and a polynomial for 32bits
        self.lfsr = lfsr(lfsr32s(), lfsr32p())
        # creating the solition distribution object
        self.PRNG = PRNG(K=self.num_segments, delta=args.delta, c=args.c_dist)

        # self.ec = args.rs #the number of error correction bytes to add
        self.tries = 0  # number of times we tried to create a droplet
        self.good = 0  # droplets that were screened successfully
        self.redundancy = 0  # good droplets after decoding possible

        self.args = args
        self.plate_info = args.plate_info
        self.plate_cells = args.plate_cells
        self.strand_name = args.strand_name
        self.fwd_primer = args.fwd_primer
        self.bwd_primer = args.bwd_primer
        self.maximum_gc = args.maximum_gc
        self.minimum_gc = args.minimum_gc

        self.segment_counts = [0] * self.num_segments

    def _calc_stop(self):
        """
        Calculates the final number of droplets needed
        based off of user input stop or alpha (redundancy)

        Args: None
        Returns:
            stop (int): The number of droplets to create
        """

        if self.stop is not None:
            return self.stop

        stop = int(self.num_segments * (1 + self.alpha)) + 1
        return stop

    def _calc_redundancy(self):
        """
        """
        if self.stop is not None:
            return self.stop

        stop = int(self.num_segments * self.alpha) + 1
        return stop

    def _update_seed(self):
        """
        Creates a fresh seed for the droplet and primes
        the solition inverse cdf sampler

        Args: None
        Returns:
            new_seed (int): the new seed
        """

        new_seed = next(self.lfsr)  # deploy one round of lfsr, and read the register
        self.PRNG.set_seed(new_seed)  # update the seed with the register value
        return new_seed

    def make_droplet(self):
        """
        Creates a new droplet object by getting a new seed,
        getting a list of random indexes, getting the associated
        segments and xor-ing them for the droplet payload

        Args: None
        Returns:
            droplet object: the newly created droplet
        """

        new_data = None
        new_seed = self._update_seed()
        _, d, segments_indexes = self.PRNG.get_src_blocks()

        for index in segments_indexes:
            self.segment_counts[index] += 1
            if new_data is None:  # first round, data payload is empty
                new_data = self.data_in[index]  # just copy the segment to the payload
            else:  # more rounds, xor the new segments with the payload
                new_data = list(map(operator.xor, new_data, self.data_in[index]))

        self.tries += 1

        return Droplet(map_obj=self.mapping, seed=new_seed, payload=new_data,
                       segments_indexes=segments_indexes,
                       degree=d, args=self.args)

    def is_valid(self, droplet):
        """
        Checks to see if the given droplet has a valid sequence.
        If so it counts the total number of acceptable droplets
        and returns one, otherwise returns 0.

        Args: droplet : the object to check
        Returns:
            int : 1 for a acceptable sequence, 0 otherwise
        """

        if droplet.is_valid() == 1:
            self.good += 1
            return 1
        return 0

    def is_done(self):
        """
        Determines if the encoding process is done

        Args: None
        Returns: boolean representing if the needed
                 number of droplets have been generated
        """

        return self.good >= self.final

    def count_redundancy(self):
        """
        """
        self.redundancy += 1

    def is_done_redundancy(self):
        """
        """
        return self.redundancy >= self.final_redundancy
