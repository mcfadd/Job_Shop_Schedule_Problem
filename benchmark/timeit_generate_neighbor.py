# import pyximport; pyximport.install()
import pickle
import statistics
import time

import cython_files.generate_neighbor_compiled as neighbor_generator
from cython_files.makespan_compiled import InfeasibleSolutionException
from data import Data

Data.initialize_data("../data/data_set2/sequenceDependencyMatrix.csv",
                     "../data/data_set2/machineRunSpeed.csv",
                     "../data/data_set2/jobTasks.csv")

outer_iters = 10
inner_iters = 1000

print("outer_iterations =", outer_iters)
print("inner iterations =", inner_iters)

times = []
with open('./initial_benchmark_solution.pkl', 'rb') as fin:
    solution = pickle.load(fin)

n_cnt = 0
for i in range(outer_iters):

    start_time = time.time()
    for j in range(inner_iters):
        try:
            neighbor_generator.generate_neighbor(solution, 1)
            n_cnt += 1
        except InfeasibleSolutionException:
            pass

    times.append(time.time() - start_time)

print("avg time =", statistics.mean(times))
print("number of infeasible neighbors =", outer_iters * inner_iters - n_cnt)
