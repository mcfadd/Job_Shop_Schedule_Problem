#!/usr/bin/env bash

# This bash script runs JSSP with the specified command line arguments.
# Note you do not have to have JSSP installed.

scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath`
scriptPath=`dirname $scriptPath`

output=$scriptPath/benchmark_results
data=$scriptPath/data/data_set2

# run benchmark
#/usr/bin/env python $scriptPath/JSSP -pb -b na -np 4 -rt 10 -ts 50 -ns 300 -p 0.8 -nw 0.1 -o $output $data

# run main
/usr/bin/env python $scriptPath/JSSP -pb -np 4 -rt 30 -ts 25 -ns 200 -p 0.8 -nw 0.1 $data
