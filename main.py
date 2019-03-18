
import tabu_search
from data_set import Operation
from makespan import *
import time

start_time = time.time()

# read csv files and update data class
# make sure the paths are correct!
Data.read_data_from_files('data/sequenceDependencyMatrix.csv', 'data/machineRunSpeed.csv', 'data/jobTasks.csv')

# uncomment to print data that was read in
# Data.print_data()

# create a list of operations
# Note this will be done inside of the feasible solution factory class
operations_list = [
    Operation(task=Data.get_job(0).get_task(0), machine=0),
    Operation(task=Data.get_job(0).get_task(1), machine=1),
    Operation(task=Data.get_job(1).get_task(0), machine=1),
    Operation(task=Data.get_job(2).get_task(0), machine=0),
    Operation(task=Data.get_job(1).get_task(1), machine=0),
]

initial_solution = Solution(operations_list)

print("\nInitial Solution:")
initial_solution.pprint()

print("\nNeighborhood of Initial Solution:")
neighborhood = tabu_search.generate_neighborhood(8, initial_solution).pprint()

print("\nTabu Search Result:")
tabu_search.search(initial_solution, iters=100, tabu_size=10, neighborhood_size=8).pprint()

duration = time.time() - start_time

print(f"\nDuration {duration} seconds")

