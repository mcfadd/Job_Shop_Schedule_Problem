#!/usr/bin/env bash

# get path to bin
scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath` # path to bin
scriptPath=`dirname $scriptPath` # path to jsp

# set arguments
benchmarkSolution=$scriptPath/benchmark/initial_benchmark_solution.pkl
output=$scriptPath/benchmark
data=$scriptPath/data/data_set2

# run benchmark with progress bar
#/usr/bin/env python $scriptPath/main.py -pb -b na -np 8 -rt 120 -ts 50 -ns 225 -p 0.8 -nw 0.1 -o $output $data

# run main without progress bar
/usr/bin/env python $scriptPath/main.py -v -np 4 -rt 10 -ts 100 -ns 200 -p 0.8 -nw 0.1 $data
