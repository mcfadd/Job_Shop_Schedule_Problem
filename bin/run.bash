#!/usr/bin/env bash

# This bash script runs JSSP with the specified command line arguments.

scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath`
scriptPath=`dirname $scriptPath`

# set arguments
benchmarkSolution=$scriptPath/benchmark/initial_benchmark_solution.pkl
output=$scriptPath/benchmark_results
data=$scriptPath/data/data_set2

# run benchmark with progress bar
/usr/bin/env python $scriptPath/JSSP -pb -b na -np 4 -rt 10 -ts 100 -ns 400 -p 0.8 -nw 0.25 -o $output $data

# run main without progress bar
#/usr/bin/env python $scriptPath/JSSP -pb -np 4 -rt 10 -ts 100 -ns 200 -p 0.8 -nw 0.1 $data
