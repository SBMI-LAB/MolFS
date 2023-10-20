#!/bin/bash

if (( $# < 2 ))
then
  echo 'Usage: encode_script <file_in> <num_segments>'
  exit 2
fi
# num_segment 471
# size 28
python decode.py -f $1 -n $2 -p 0 --delta 0.001 --c_dist 0.025 --rs1 3 --out $1-out.png --map original_map.txt --size 28


