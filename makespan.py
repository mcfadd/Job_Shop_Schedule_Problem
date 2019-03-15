from data_set import Data, Solution


class makespanCalculator:

    @staticmethod
    def iterative_makespan_wait_setup(nextOperation, machineRuntimeMemory, jobMemory, machineTasksMemory):

        machine = nextOperation.getMachine()    # machine Id for operation
        task = nextOperation.getTask()          # task object
        jobId = task.getJobId()                 # job Id of task
        sequence = task.getSequence()           # sequence number of task
        pieces = task.getPieces()               # pieces of task

        # check if current sequence is less than last sequence processed for job
        if sequence < jobMemory[jobId][0]:
            return -1

        # get setup time given previous & current operation
        setup = Data.getSetupTime(machineTasksMemory[machine], nextOperation.getTask())

        # a machine needs to wait if the operation it processes next has not had all of it's predecessors processed
        wait = jobMemory[jobId][1] - machineRuntimeMemory[machine] if \
            jobMemory[jobId][1] > machineRuntimeMemory[machine] else 0

        # return (num of pieces / speed of machine (i.e. runtime on machine), wait, setup)
        return (pieces / Data.machineSpeeds[machine], wait, setup)

    @staticmethod
    def compute_makespan_and_wait(operationsList):

        if isinstance(operationsList, Solution):
            operationsList = operationsList.getOperationsList()

        # memory for machine runtimes
        machineRuntimeMemory = [0] * Data.getNumerOfMachines()

        # memory for machine's latest task
        machineTasksMemory = [None] * Data.getNumerOfMachines()

        # memory for latest (sequence, end time) for each job
        jobMemory = [(0, 0)] * Data.getNumberOfJobs()

        totalWaitTime = 0

        # process first operation in Solution
        operation = operationsList[0]
        machine = operation.getMachine()        # machine Id for operation
        task = operation.getTask()              # task object
        jobId = task.getJobId()                 # job Id of task
        sequence = task.getSequence()           # sequence number of task
        pieces = task.getPieces()               # pieces of task

        runtime = pieces / Data.getMachineSpeed(machine)

        # update memory modules
        machineRuntimeMemory[machine] = runtime
        jobMemory[jobId] = (sequence, machineRuntimeMemory[machine])
        machineTasksMemory[machine] = task

        for operation in operationsList[1:]:

            machine = operation.getMachine()        # machine Id for operation
            task = operation.getTask()              # task object
            jobId = task.getJobId()                 # job Id of task
            sequence = task.getSequence()           # sequence number of task

            # tupleOfTimes = (runtime on machine, wait, setup)
            runtime_wait_setup = makespanCalculator.iterative_makespan_wait_setup(operation, machineRuntimeMemory, jobMemory, machineTasksMemory)

            # check if solution is infeasible
            if runtime_wait_setup == -1:
                return -1

            # compute total added time and update memory, where runtime = (runtime on machine, wait, setup)
            machineRuntimeMemory[machine] += runtime_wait_setup[0] + runtime_wait_setup[1] + runtime_wait_setup[2]
            jobMemory[jobId] = (
                sequence, machineRuntimeMemory[machine])
            machineTasksMemory[machine] = task
            totalWaitTime += runtime_wait_setup[1]

        return (machineRuntimeMemory, totalWaitTime)

    @staticmethod
    def compute_makespan(operationsList):
        return max(makespanCalculator.compute_makespan_and_wait(operationsList)[0])

    @staticmethod
    def compute_wait_time(operationsList):
        return makespanCalculator.compute_makespan_and_wait(operationsList)[1]
