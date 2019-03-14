
from tabuSearch import tabuSearch
from dataSet import data, operation
import makespan
import time

start_time = time.time()

# read csv files and update data class
# Note: make sure your relative paths are correct

data.readDataFromFiles('data/sequenceDependencyMatrix.csv', 'data/machineRunSpeed.csv', 'data/jobTasks.csv')

# uncomment to print data
# data.printData()

Solution = [
    operation(task=data.getJob(0).getTask(0), machine=0),
    operation(task=data.getJob(0).getTask(1), machine=1),
    operation(task=data.getJob(1).getTask(0), machine=1),
    operation(task=data.getJob(2).getTask(0), machine=0),
    operation(task=data.getJob(1).getTask(1), machine=0),
]

print("Initial Solution:")
for operation in Solution:
    print(operation.getString())

make = makespan.makeSpanCalculator()

# Note: result = ([list of machine runtimes], total wait time)
result = make.compute_makespan(Solution)

print("\nMakespan results:")
print("(makespan, waitTime)\n")
print(f"({ max(result[0]) }, { result[1] })\n")

print("generate neighborhood results:")
print("(makespan, waitTime) [ neighbor ]\n")
tabuSearch(make).generate_neighborhood(8, Solution).pprint()

duration = time.time() - start_time

print(f"Duration {duration} seconds")

