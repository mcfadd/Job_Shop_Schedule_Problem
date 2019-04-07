#!/usr/bin/env bash

# set arguments
benchmarkSolution="~/Job_Shop_Schedule_Problem/benchmark/initial_benchmark_solution.pkl"
output="~/Job_Shop_Schedule_Problem/benchmark"
data="~/Job_Shop_Schedule_Problem/data/data_set2"

# get path to bin
scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath`

# run a benchmark solution
/usr/bin/env python $scriptPath/../main.py -pb -b $benchmarkSolution 2 -rt 10 -ts 500 -ns 300 -p 0.8 -nw 0.1 -o $output $data
