from dataSet import data


class makeSpanCalculator:

    def iterative_makespan(self, nextOperation, machineRuntimeMemory, jobMemory, machineTasksMemory, debug=False):

        machine = nextOperation.getMachine()    # machine Id for operation
        task = nextOperation.getTask()          # task object
        jobId = task.getJobId()                 # job Id of task
        sequence = task.getSequence()           # sequence number of task
        pieces = task.getPieces()               # pieces of task

        # check if current sequence is less than last sequence processed for job
        if sequence < jobMemory[jobId][0]:
            return -1

        # get setup time given previous & current operation
        setup = data.getSetupTime(machineTasksMemory[machine], nextOperation.getTask())

        # a machine needs to wait if the operation it processes next has not had all of it's predecessors processed
        wait = jobMemory[jobId][1] - machineRuntimeMemory[machine] if \
            jobMemory[jobId][1] > machineRuntimeMemory[machine] else 0

        if debug:
            print("\nProcessing operation = {}, wait = {}, setup = {}".format(nextOperation, wait, setup))

        # return (num of pieces / speed of machine (i.e. runtime on machine), wait, setup)
        return (pieces / data.machineSpeeds[machine], wait, setup)

    def compute_makespan(self, solution, debug=False):
        # memory for machine runtimes
        machineRuntimeMemory = [0] * data.getNumerOfMachines()

        # memory for machine's latest task
        machineTasksMemory = [None] * data.getNumerOfMachines()

        # memory for latest (sequence, end time) for each job
        jobMemory = [(0, 0)] * data.getNumberOfJobs()

        totalWaitTime = 0

        # process first operation in Solution
        operation = solution[0]
        machine = operation.getMachine()        # machine Id for operation
        task = operation.getTask()              # task object
        jobId = task.getJobId()                 # job Id of task
        sequence = task.getSequence()           # sequence number of task
        pieces = task.getPieces()               # pieces of task

        runtime = pieces / data.getMachineSpeed(machine)

        # update memory modules
        machineRuntimeMemory[machine] = runtime
        jobMemory[jobId] = (
            sequence, machineRuntimeMemory[machine])
        machineTasksMemory[machine] = task

        for operation in solution[1:]:

            machine = operation.getMachine()        # machine Id for operation
            task = operation.getTask()              # task object
            jobId = task.getJobId()                 # job Id of task
            sequence = task.getSequence()           # sequence number of task

            # tupleOfTimes = (runtime on machine, wait, setup)
            tupleOfTimes = self.iterative_makespan(operation, machineRuntimeMemory, jobMemory, machineTasksMemory,
                                                   debug)

            # check if solution is infeasible
            if tupleOfTimes == -1:
                return -1

            # compute total added time and update memory, where runtime = (runtime on machine, wait, setup)
            machineRuntimeMemory[machine] += tupleOfTimes[0] + tupleOfTimes[1] + tupleOfTimes[2]
            jobMemory[jobId] = (
                sequence, machineRuntimeMemory[machine])
            machineTasksMemory[machine] = task
            totalWaitTime += tupleOfTimes[1]

        return (machineRuntimeMemory, totalWaitTime)
