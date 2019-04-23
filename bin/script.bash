#!/usr/bin/env bash

# get path to bin
scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath` # path to bin
scriptPath=`dirname $scriptPath` # path to jsp

# set arguments
benchmarkSolution=$scriptPath/benchmark/initial_benchmark_solution.pkl
output=$scriptPath/benchmark_results
data=$scriptPath/data/data_set2

# run benchmark with progress bar
#/usr/bin/env python $scriptPath/src -pb -b na -np 6 -rt 240 -ts 100 -ns 250 -p 0.8 -nw 0.2 -o $output $data

# run main without progress bar
/usr/bin/env python $scriptPath/src -v -np 4 -rt 300 -ts 100 -ns 200 -p 0.8 -nw 0.1 $data
