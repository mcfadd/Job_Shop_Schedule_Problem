# from genetic_algorithm.ga_helpers import cross, placement
# import numpy as np
# from . import solution

import pickle
import statistics

from .data import Data
from .genetic_algorithm import search

Data.initialize_data('../data/data_set2/sequenceDependencyMatrix.csv', '../data/data_set2/machineRunSpeed.csv',
                     '../data/data_set2/jobTasks.csv')

# # test placement()
# p = solution.generate_feasible_solution().operation_2d_array
#
# print(placement(np.array([4, 0, 0, 2], dtype=np.intc), p))
#
# # test cross()
# p1 = solution.generate_feasible_solution().operation_2d_array
#
# p2 = solution.generate_feasible_solution().operation_2d_array
#
# print(p1, p2)
# print(cross(p1, p2))
# print()
# print(cross(p2, p1))
#
#
#

# def check_unique_ops(sol):
#     results = [0] * len(Data.jobs)
#     for row in list(sol.operation_2d_array):
#         results[row[0]] += 1
#
#     for i, result in enumerate(results):
#         if result != Data.jobs[i].get_number_of_tasks():
#             print("fail")
#             exit(1)
#
#
# infeasible_cnt = 0
# for _ in range(100):
#     sol1 = solution.generate_feasible_solution()
#     sol2 = solution.generate_feasible_solution()
#     check_unique_ops(sol1)
#     check_unique_ops(sol2)
#     # print("sol1:")
#     # sol1.pprint()
#     # print("sol2:")
#     # sol2.pprint()
#     # print("sol1 cross sol2:")
#     try:
#         r = cross(sol1.operation_2d_array, sol2.operation_2d_array)
#         check_unique_ops(r)
#     except:
#         infeasible_cnt += 1
#     # r.pprint()
#
# print(infeasible_cnt)

pop_size = 50
# random_population = [solution.generate_feasible_solution() for _ in range(pop_size)]

with open("/home/mcfadd/Job_Shop_Schedule_Problem/JSSP/test_population.pkl", 'rb') as file:
    random_population = pickle.load(file)

best_sol = min(random_population)
print("best sol before:")
best_sol.pprint()

print("avg makespan =", statistics.mean([sol.makespan for sol in random_population]))

result = search(30, random_population, pop_size, 0.5, verbose=True)

print("best sol after:")
result.pprint()
