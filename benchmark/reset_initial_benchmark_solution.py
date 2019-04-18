import pickle
import solution
from data import Data

Data.initialize_data("../data/data_set2/sequenceDependencyMatrix.csv",
                     "../data/data_set2/machineRunSpeed.csv",
                     "../data/data_set2/jobTasks.csv")

with open('./initial_benchmark_solution.pkl', 'rb') as fin:
    sol = pickle.load(fin)

sol = solution.Solution(sol.operation_2d_array)
# sol = solution.generate_feasible_solution()

print(sol.makespan)
solution.pickle_to_file(sol, './initial_benchmark_solution.pkl')
