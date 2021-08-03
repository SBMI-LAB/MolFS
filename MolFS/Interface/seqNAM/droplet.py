"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

import struct
from reedsolo import RSCodec
from transpose import hex_to_codons


class Droplet:
    """
    This class contains the information needed for a Droplet object. The droplet
    represents a seed, a payload, and a possible error correction code. The payload
    is represented by multiple data segments xor-ed together. The droplet object does
    not keep track of individual segments, instead it keeps a list of index values
    corresponding to each segment. During the encoding stage, a droplet can be
    represented by bytes and by a nucleotide sequence. (This class is no longer used
    during the decoding stage).

    Args:
        map_obj (object): the mapping object for converting hex to codons
        seed (int): seed value associated with generating segments_indexes and d
        payload (int list): integer representation of bytes in data (multiple segments xor-ed)
        segments_indexes (int list): list of indexes associated with segments in the droplet
        degree (int): the number of segments xor-ed in the payload
        args (object) : Arguments for this encoding/decoding
    Returns: None
    """

    def __init__(self, map_obj, seed, payload, segments_indexes=None, degree=None, args=None):
        self.map_obj = map_obj
        self.seed = seed
        self.payload = payload
        self.segments_indexes = segments_indexes
        self.degree = degree
        self.ec = args.rs
        self.maximum_gc = args.maximum_gc
        self.minimum_gc = args.minimum_gc
        self.ec_obj = RSCodec(self.ec)  # initializing an reed solomon object
        self.valid = 0
        self.bytes = self._package()
        self.DNA = self._to_DNA_strand()
        self.backtrack = self.get_backtrack()

    def _to_DNA_strand(self):
        """
        Converts the droplet data (seed, payload, EC)
        from the integer representation of bytes into
        a sequence of nucleotides

        Args: None
        Returns:
            string: nucleotide sequence representation of
                    the data in this droplet
        """

        self.DNA, self.backtrack = hex_to_codons(self, self.map_obj)
        self.valid = 0 if self.DNA == -1 else 1
        return self.DNA

    def _package(self):
        """
        Converts the seed to a list of 4bytes HARD CODED!!!
        Concatenates the seed to the payload then computes and
        concatenates a Reed Solomon code on the seed and payload

        Args: None
        Returns:
            message (int list): bytes representing the seed, payload,
                                 and EC as the integer representation
        """

        seed_ord = [c for c in struct.pack("!I", self.seed)]
        # converting the seed into exactly four bytes.

        message = seed_ord + self.payload

        if self.ec > 0:
            message = self.ec_obj.encode(message)  # adding RS symbols to the message

        return message

    def get_byte_strand(self):
        """
        Getter method for the data (seed, payload, EC) in
        this droplet as bytes (represented by a list of integers)

        Args: None
        Returns: Byte list of integers
        """

        return self.bytes

    def get_DNA_strand(self):
        """
        Getter method for the data (seed, payload, EC) in
        this droplet as a sequence of nucleotide symbols

        Args: None
        Returns: String representing the nucleotide sequence
        """

        return self.DNA

    def is_valid(self):
        """
        Getter method for the valid variable. This represents
        whether or not the droplet produced a valid sequence.

        Args: None
        Returns: int representing a valid sequence or not
        """
        return self.valid

    def get_backtrack(self):
        """
        Getter method for the backtrack. This will return
        total number of backtrack that were needed to convert
        this droplet into DNA sequence.

        :parameter: None

        :return: int representation of total backtrack
        """
        return self.backtrack
