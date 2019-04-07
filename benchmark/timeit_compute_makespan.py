# import pyximport; pyximport.install()
import pickle
import statistics
import time

import cython_files.makespan_compiled as makespan

from data import Data

Data.initialize_data("../../data/data_set2/sequenceDependencyMatrix.csv",
                     "../../data/data_set2/machineRunSpeed.csv",
                     "../../data/data_set2/jobTasks.csv")

outer_iters = 10
inner_iters = 1000

print("outer_iterations =", outer_iters)
print("inner iterations =", inner_iters)

times = []
with open('./initial_benchmark_solution.pkl', 'rb') as fin:
    solution = pickle.load(fin)

for i in range(outer_iters):

    start_time = time.time()
    for j in range(inner_iters):
        makespan.compute_machine_makespans(solution.operation_2d_array)

    times.append(time.time() - start_time)

print("avg time =", statistics.mean(times))

