#!/usr/bin/env bash

# This bash script runs JSSP with the specified command line arguments.

scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath`
scriptPath=`dirname $scriptPath`

# set arguments
benchmarkSolution=$scriptPath/benchmark/initial_benchmark_solution.pkl
output=$scriptPath/benchmark_results
data=$scriptPath/data/data_set3

# run benchmark
#/usr/bin/env python $scriptPath/JSSP -pb -b na -np 4 -rt 60 -ts 50 -ns 300 -p 0.8 -nw 0.1 -o $output $data

# run main
/usr/bin/env python $scriptPath/JSSP -pb -np  -rt 30 -ts 25 -ns 200 -p 0.8 -nw 0.1 $data
