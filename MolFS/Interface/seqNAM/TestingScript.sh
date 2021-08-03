#!/bin/bash

python3 encode.py -f testfile.jpg -l 32 --delta 0.001 --c_dist 0.025 --rs 2 --map original_map.txt --alpha 0.1 --out testfile.dna --output_format sequence_only  --ensure_decode_ability 

#python3 convert_Format.py  testfile.dna testfile.fastq

echo "Decoding..."
python3 decode.py -f testfile.dna -n 412 -l 32 --delta 0.001 --c_dist 0.025 --rs 2 --map original_map.txt --out testfile_out.jpg --file_format csv --primer_length 20




