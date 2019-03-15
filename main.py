
from tabu_search import TabuSearch
from data_set import Data, Operation, Solution
from makespan import *
import time

start_time = time.time()

# read csv files and update data class
# Note: make sure your paths are correct
Data.readDataFromFiles('data/sequenceDependencyMatrix.csv', 'data/machineRunSpeed.csv', 'data/jobTasks.csv')

# uncomment to print data that was read in
# Data.printData()

# create an initial feasible solution
initialSolution = Solution([
    Operation(task=Data.getJob(0).getTask(0), machine=0),
    Operation(task=Data.getJob(0).getTask(1), machine=1),
    Operation(task=Data.getJob(1).getTask(0), machine=1),
    Operation(task=Data.getJob(2).getTask(0), machine=0),
    Operation(task=Data.getJob(1).getTask(1), machine=0),
])

print("Initial Solution:")
initialSolution.print()

makespan = makespanCalculator.compute_makespan(initialSolution.getOperationsList())
waitTime = makespanCalculator.compute_wait_time(initialSolution.getOperationsList())

# alternative to get makespan and wait time in one function call
# makespan_and_wait = makespanCalculator.compute_makespan_and_wait(initialSolution)
# makespan = max(makespan_and_wait[0])
# waitTime = makespan_and_wait[1]

print("\nMakespan results:")
print("(makespan, total wait time)\n")
print(f"({ makespan }, { waitTime })\n")

print("generate neighborhood results:")
print("(makespan, total wait time) [ neighbor ]\n")
neighborhood = TabuSearch().generate_neighborhood(8, initialSolution.getOperationsList())
neighborhood.pprint()

duration = time.time() - start_time

print("")
print(f"Duration {duration} seconds")

