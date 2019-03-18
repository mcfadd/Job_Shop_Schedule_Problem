
from data_set import Data, Operation
from makespan import *

Data.read_data_from_files('data/sequenceDependencyMatrix.csv', 'data/machineRunSpeed.csv', 'data/jobTasks.csv')

op1 = Operation(task=Data.get_job(0).get_task(0), machine=0)
op2 = Operation(task=Data.get_job(0).get_task(0), machine=0)

print(op1 == op2)

# create an initial feasible solution
operations_list1 = [
    Operation(task=Data.get_job(0).get_task(0), machine=0),
    Operation(task=Data.get_job(0).get_task(1), machine=1),
    Operation(task=Data.get_job(1).get_task(0), machine=1),
    Operation(task=Data.get_job(2).get_task(0), machine=0),
    Operation(task=Data.get_job(1).get_task(1), machine=0),
]

# alternative to get makespan and wait time in one function call
# makespan_and_wait = makespanCalculator.compute_makespan_and_wait(initialSolution)
# makespan_cost = makespan_and_wait[0]
# wait_timeime = makespan_and_wait[1]

makespan_cost = compute_makespan(operations_list1)
wait_time = compute_wait_time(operations_list1)

sol1 = Solution(operations_list1, makespan_cost, wait_time)

# create an initial feasible solution
operations_list2 = [
    Operation(task=Data.get_job(0).get_task(0), machine=0),
    Operation(task=Data.get_job(0).get_task(1), machine=1),
    Operation(task=Data.get_job(1).get_task(0), machine=1),
    Operation(task=Data.get_job(2).get_task(0), machine=0),
    Operation(task=Data.get_job(1).get_task(1), machine=0),
]

sol2 = Solution(operations_list2, makespan_cost, wait_time)

print(sol1 == sol2)
