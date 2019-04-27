#!/usr/bin/env bash

scriptPath=`readlink -f $0`
scriptPath=`dirname $scriptPath` # path to bin
scriptPath=`dirname $scriptPath` # path to jsp

# build solution/makespan.pyx
cd $scriptPath/src/solution
/usr/bin/env python ./setup.py build_ext --inplace

# build tabu/generate_neighbor.pyx
cd ../tabu
/usr/bin/env python ./setup.py build_ext --inplace

# build genetic_algorithm/ga_helpers.pyx
cd ../genetic_algorithm
/usr/bin/env python ./setup.py build_ext --inplace
