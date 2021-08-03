"""
Copyright (C) 2018 Kelsey Suyehira
License: GPLv3-or-later. See COPYING file for details.
"""
import math
from collections import defaultdict

"""
 transpose.py

This file contains methods for converting bytes (int) to
nucleotide sequences and back again based on a certain 
mapping. The expected mapping scheme converts between 
hexadecimal values and codons, or sequences of three 
nucleotides. This mapping is provided by the user in a 
given file and is encapsulated in the map_obj parameter. 
The encoding method also avoids repeating sequences and 
uneven GC content.

"""


def hex_to_codons(droplet, map_obj):
    """
    Converts a list of integer representation of
    bytes to a sequence of nucleotides based on
    the hexadecimal to codons mapping object

    Args:
        droplet (int list): The byte data to convert
        map_obj (object): the mapping object for converting hex_ to codons
    Returns:
        dna_string (string): The corresponding nucleotide sequence
    """
    a = droplet.get_byte_strand()
    hex_sequence = []
    prev_choices = defaultdict(int)
    codon_l = 3
    maximum_gc = droplet.maximum_gc
    minimum_gc = droplet.minimum_gc
    num_backtrack = 0
    tot_allowed_back = 500
    i = 0

    # Convert bytes to a list of hexadecimal chars
    # hex_index = 0
    for byte in a:
        for hex_ in '{0:02x}'.format(byte):
            hex_sequence.append(hex_)
            # hex_index += 1
    nt_sequence = [None] * (len(hex_sequence) * codon_l)

    # Start by converting first hex_ char
    char = hex_sequence[i]
    options = map_obj.get_codon_first(char)
    next_codon = options[prev_choices[i]]
    nt_sequence = _append_codon(nt_sequence, next_codon, i)
    prev_choices[i] += 1
    prev_codon = next_codon
    tot_gc = nt_sequence.count("G") + nt_sequence.count("C") + 0.0
    i += 1

    # Main loop for converting hex_ at each index i
    while i < len(hex_sequence):

        if num_backtrack > tot_allowed_back or i == 0:
            # taking too long for backtracking
            return -1, -1

        char = hex_sequence[i]
        options = map_obj.get_codon(prev_codon, char)

        if prev_choices[i] == len(options):
            # no options available at current index
            backtrack = True
        else:
            backtrack = False
            next_codon = options[prev_choices[i]]
            prev_choices[i] += 1
            if i < 5:  # for first 5 codons, don't check for long repeats
                nt_sequence = _append_codon(nt_sequence, next_codon, i)
                prev_codon = next_codon
                tot_gc += next_codon.count("G") + next_codon.count("C")
                i += 1
            else:  # check for longer repeats for rest
                nt_sequence = _append_codon(nt_sequence, next_codon, i)
                next_gc = next_codon.count("G") + next_codon.count("C")
                tot_gc += next_gc
                gc_min_range = minimum_gc * (i / (len(hex_sequence) + 0.0))
                gc_max_range = 1 - (1 - maximum_gc) * (i / (len(hex_sequence) + 0.0))
                gc_check = tot_gc / (i * codon_l + 0.0)
                if (gc_check >= gc_min_range) and (gc_check <= gc_max_range):
                    # GC in range
                    text = ''.join(nt_sequence[:((i - 2) * codon_l)])
                    pattern = ''.join(nt_sequence[((i - 2) * codon_l):((i + 1) * codon_l)])
                    if pattern not in text:
                        # no repeating sequences, move on to next index
                        prev_codon = next_codon
                        i += 1
                    else:
                        # found repeating sequence, try again
                        tot_gc -= next_gc
                        if prev_choices[i] == len(options):
                            backtrack = True
                else:  # GC out of range, try again
                    tot_gc -= next_gc
                    if prev_choices[i] == len(options):
                        backtrack = True

        if backtrack:
            # all options have been tried at current index, go back one index
            tot_gc -= prev_codon.count("G") + prev_codon.count("C")
            num_backtrack += 1
            prev_choices[i] = 0
            i -= 1
            prev_codon = nt_sequence[((i * codon_l) - 3):(i * codon_l)]

    # success! return full sequence
    return ''.join(nt_sequence), num_backtrack


def _append_codon(nt_sequence, codon, i):
    """
    Add the values from the codon to the nt_sequence
    at the given index value i.

    Args:
        nt_sequence (list): the list of nts to add to
        codon (list): the list of nts to copy from (length 3)
        i (int): the index value to add at
    Returns:
        nt_sequence (list): the updated list with the new codon values
    """

    for index in [0, 1, 2]:
        nt_sequence[(i * 3) + index] = codon[index]
    return nt_sequence


def codons_to_hex(dna_str, map_obj):
    """
    Converts a sequence of nucleotides to a list
    of the integer representation of bytes based on
    the hexadecimal to codons mapping

    Args:
        dna_str (string): The sequence to convert
        map_obj (object): the mapping object for codons to hex
    Returns:
        data (int list): The corresponding byte data
    """
    dna_size = len(dna_str)
    hex_size = math.ceil(dna_size / 3)
    hex_string: str = ''
    for i in range(0, dna_size, 3):
        codon = dna_str[i:i + 3]
        char = map_obj.get_hex(codon)
        if char == -1:
            return -1
        hex_string += char
    data = [int(hex_string[t:t + 2], 16) for t in range(0, hex_size, 2)]
    return data
