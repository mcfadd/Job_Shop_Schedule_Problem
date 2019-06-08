from JSSP.data import Data
from JSSP.solver import Solver

Data.initialize_data_from_csv('../data/given_data/sequenceDependencyMatrix.csv',
                              '../data/given_data/machineRunSpeed.csv',
                              '../data/given_data/jobTasks.csv')

# parameters
runtime = 5
num_processes = 2
tabu_list_size = 50
neighborhood_size = 200
neighborhood_wait = 0.1
probability_change_machine = 0.8
solver = Solver()

solver.tabu_search_iter(runtime,
                        num_processes,
                        tabu_list_size,
                        neighborhood_size,
                        neighborhood_wait,
                        probability_change_machine,
                        benchmark=True,
                        verbose=True)

solver.ts_best_solution.pprint()
solver.output_benchmark_results('/home/mcfadd/tmp_jssp_out', auto_open=True)
