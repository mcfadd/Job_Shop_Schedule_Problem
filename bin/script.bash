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
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 30 -ts 100 -ns 200 -p 0.8 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 300 -ts 100 -ns 400 -p 0.8 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 300 -ts 100 -ns 400 -p 0.5 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 300 -ts 100 -ns 300 -p 0.8 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 300 -ts 100 -ns 300 -p 0.5 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 300 -ts 100 -ns 200 -p 0.8 -nw 0.1 -o $output $data
#/usr/bin/env python $scriptPath/main.py -pb -b $benchmarkSolution 2 -rt 3 -ts 100 -ns 350 -p 0.8 -nw 0.1 -o $output $data

# run main without progress bar
/usr/bin/env python $scriptPath/main.py -rt 5 -ts 100 -ns 200 -p 0.8 -nw 0.1 -o $output $data
