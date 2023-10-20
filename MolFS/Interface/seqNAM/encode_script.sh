#!/bin/bash

if (( $# < 2 ))
then
  echo 'Usage: encode_script <file_in> <plate_cells>'
  exit 2
fi

python encode.py -f $1 -l 28 --delta 0.001 --c_dist 0.025 --rs1 3  --alpha 0.1 --out $1-$2.csv --map original_map.txt --plate_cells $2


