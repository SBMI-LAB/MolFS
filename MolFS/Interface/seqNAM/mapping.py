"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""

from collections import defaultdict


class MapObject:
    """
    This class provides the ability to read a map from a given file and produce
    dictionaries from it to be used during the transpose stage of converting binary
    to nucleotides. Currently the map expects to convert hexadecimal values to codons,
    or sequences of three nucleotides and the dictionaries will exclude the ability
    to produce any of the illegal_codons hardcoded in the list. Also, each codon is
    represented by a list of three strings because it is easier for the transpose
    methods to handle.

    Args:
        map_file (string): the name of the file to read that contains the mapping
    Returns: None
    """

    def __init__(self, map_file):

        self.valid_codons = ["CAA", "GAA", "TAA", "AAC", "GAC", "TAC", "AAG", "GAG", "TAG",
                             "ACC", "GCC", "TCC", "ACG", "CCG", "GCG", "TCG", "ACT", "CCT",
                             "GCT", "TCT", "AGA", "CGA", "GGA", "AGC", "CGC", "GGC", "AGG",
                             "CGG", "AGT", "CGT", "GGT", "CTA", "GTA", "TTA", "ATC", "CTC",
                             "GTC", "GTT", "TTC"]
        self.illegal_codons = ["ATG", "CAT", "ATA", "TAT", "ATT", "AAT", "GTG", "CAC",
                               "TTG", "CTT", "CTG", "CAG", "AAA", "CCC", "GGG", "TTT"]

        self.config_file = map_file
        self.short_map = self._read_file(self.config_file)
        self.full_map = self._create_map(self.short_map)
        self.reverse_map = self._reverse_map(self.short_map)

    @staticmethod
    def _read_file(map_file):
        """
        Reads in a given file with a specific mapping and
        creates a dictionary object from the mapping. The
        file is expected to have the format "x : t" for each
        line, where x represents the hex character and t
        represents a list of codons separated by commas.

        Args:
            map_file (string): name of file to be parsed
        Returns:
            short (dict): The dictionary representation of mapping
        """
        short = defaultdict()
        with open(map_file, 'r') as f:
            for line in f:
                split_one = line.split(":")
                split_two = split_one[1].split(",")
                codon_list = []
                for codon in split_two:
                    char_list = []
                    for char in codon.strip():
                        char_list.append(char.upper())
                    codon_list.append(char_list)
                short[split_one[0].strip()] = codon_list
        return short

    def _create_map(self, short_map):
        """
        Uses the dictionary created by the given mapping to create
        a larger map that includes previous codons. The larger map
        also examines the illegal codons list to only put valid codons
        in the dictionary for a given previous codons.

        Args:
            short_map (dict): The original dictionary from the mapping
        Returns:
            full (dict): Newly created dictionary with previous codon logic
        """
        full = defaultdict()
        for prev_codon in self.valid_codons:
            prev_codon_dict = defaultdict()
            for key, value in short_map.items():
                next_codon_list = []
                for next_codon in value:
                    test_string = prev_codon + ''.join(next_codon)
                    if not any(bad in test_string for bad in self.illegal_codons):
                        char_list = []
                        for char in next_codon:
                            char_list.append(char)
                        next_codon_list.append(char_list)
                prev_codon_dict[key] = next_codon_list
            full[prev_codon] = prev_codon_dict
        return full

    @staticmethod
    def _reverse_map(short_map):
        """
        Uses the dictionary created by the given mapping to create
        a reverse map that can be used for decoding. This dictionary
        instead has the codons as keys and hex characters as values.

        Args:
            short_map (dict): The original dictionary from the mapping
        Returns:
           reverse (dict): Newly created reversed dictionary
        """
        reverse = defaultdict()
        for key, value in short_map.items():
            for codon in value:
                reverse[''.join(codon)] = key
        return reverse

    def get_codon_first(self, hex_val):
        """
        Retrieves the list of codons corresponding to the given
        hex value in the mapping dictionary. (No previous codon
        required for first value).

        Args:
            hex_val (string): The given hex value to look up
        Returns:
            list : The list of corresponding codon options
        """

        return self.short_map[hex_val]

    def get_codon(self, prev_codon, hex_val):
        """
        Retrieves the list of codons corresponding to the given
        hex value and previous codon in the mapping dictionary.
        Note: the previous codon excludes the chance that the
        next codon will include any illegal codons.

        Args:
            prev_codon (list): Previously chosen codon
            hex_val (string): The given hex value to look up
        Returns:
            list : The list of corresponding codon options
        """
        codon = ''.join(prev_codon)
        return self.full_map[codon][hex_val]

    def get_hex(self, codon):
        """
        Retrieves the hex value corresponding to the
        given codon in the reverse mapping dictionary.

        Args:
            codon (list): The given codon
        Returns:
            key (hex): The associated hex value
        """
        if codon not in self.reverse_map:
            return -1
        return self.reverse_map[codon]
