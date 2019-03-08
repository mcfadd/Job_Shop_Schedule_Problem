
from tabuSearch import tabuSearch
from dataSet import data, operation
import makespan

# read csv files and update data class
# Note: make sure your relative paths are correct

data.readsequenceDependencyMatrixFile('data/sequenceDependencyMatrix.csv')
data.readmachineSpeedsFile('data/machineRunSpeed.csv')
data.readjobTasksFile(3, 'data/jobTasks.csv')

# uncomment to print data
# data.printData()

Solution = [
    operation(data.getJob(0).getTask(0), 0),
    operation(data.getJob(0).getTask(1), 1),
    operation(data.getJob(1).getTask(0), 1),
    operation(data.getJob(2).getTask(0), 0),
    operation(data.getJob(1).getTask(1), 0),
]

print("Current Solution:")
for operation in Solution:
    print(operation.getString())

make = makespan.makeSpanCalculator()

# Note: result = ([list of machine runtimes], total wait time)
result = make.compute_makespan(Solution)

print("\nMakespan results:")
print("(makespan, waitTime)\n")
print("({}, {})\n".format(max(result[0]), result[1]))

print("generate neighborhood results:")
print("(makespan, waitTime) [ neighbor ]\n")
tabuSearch(make).generate_neighborhood(8, Solution).pprint()



