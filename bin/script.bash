#!/usr/bin/env bash

# get path to bin
scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath` # path to bin
scriptPath=`dirname $scriptPath` # path to jsp

# set arguments
benchmarkSolution=$scriptPath/benchmark/initial_benchmark_solution.pkl
output=$scriptPath/benchmark
data=$scriptPath/data/data_set2

# run a benchmark solution
/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 5 -rt 60 -ts 100 -ns 500 -p 0.8 -nw 0.2 -o $output $data
