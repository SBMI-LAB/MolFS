#!/bin/bash

if (( $# < 1 ))
then
  printf "Usage: mc_simulations.sh <number of runs>\n"
  exit 2
fi

GOOD=0
BAD=0

for i in $(eval echo {1..$1})
do

  printf "\n\n Iteration $i\n\n"

  FILESIZE=$"$((10240+RANDOM%(20240-10240)))" #Between 10 and 20 KB
#  FILESIZE=$"$((512000+RANDOM%(819200-512000)))" #Between 500 and 800 KB
#  FILESIZE=$"$(shuf -i 1048576-2097152 -n 1)" #Between 1 and 2 MB
  CDIST=$"0.0$((21+RANDOM%(30-20)))" #Between 0.02 and 0.03
#  ALPHA=$"0.$((1+RANDOM%(3)))" #Between 0.1 and 0.3
  ALPHA=0.1
  INSERT=$"0.$((25+RANDOM%(50-25)))" #Between 0.25 and 0.50
  DELETE=$"0.$((25+RANDOM%(50-25)))" #Between 0.25 and 0.50
  MUTATE=$"0.$((25+RANDOM%(50-25)))" #Between 0.25 and 0.50

  printf " Generating binary file ...\n"
  dd if=/dev/urandom of=randBinFile count=$FILESIZE bs=1

  printf "\n Running encoding ...\n"
  printf "python encode.py -f randBinFile -l 32 --delta 0.001 --c_dist $CDIST --rs 2 --map original_map.txt --alpha $ALPHA --out randBinFile.dna --config_file\n"
  python encode.py -f randBinFile -l 32 --delta 0.001 --c_dist $CDIST --rs 2 --map original_map.txt --alpha $ALPHA --out randBinFile.dna --config_file

  printf "\n Running degradation ...\n"
  printf "\npython degrade.py -f randBinFile.dna -i $INSERT -d $DELETE -m $MUTATE -o randBinFile.dna.deg -c\n"
  python degrade.py -f randBinFile.dna -i $INSERT -d $DELETE -m $MUTATE -o randBinFile.dna.deg -c

  printf "\n Running decoding ...\n"
  printf "python decode.py -f randBinFile.dna.deg --out randBinFile.dna.out --config_file\n"
  python decode.py -f randBinFile.dna.deg --out randBinFile.dna.out --config_file

  printf "\n Comparing files ...\n"
  printf "diff randBinFile randBinFile.dna.out\n"
  DIFF=$(diff randBinFile randBinFile.dna.out)

#  if [[ !  -z  $DIFF  ]]
  if [ $? -ne 0 ]
  then
    printf "Test Incorrect\n"
    ((BAD++))
  else
    printf "Test Correct\n"
    ((GOOD++))
  fi

  printf "\n\tCorrect tests: $GOOD\n\tIncorrect tests: $BAD\n"

  rm randBinFile*

done


