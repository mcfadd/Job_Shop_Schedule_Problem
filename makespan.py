from data_set import Data
from functools import reduce


class InfeasibleSolutionException(Exception):
    pass


class IncompleteSolutionException(Exception):
    pass


class Solution:
    """
    This class represents a solution which is composed of a list of operations, a list of machine make span times,
    and the max make span time.
    """

    def __init__(self, operation_list):
        """
        The constructor for this solution checks if the operation list is feasible,
        computes the list of machine make span times, and the max make span time.

        :param operation_list: The list of operations of this Solution.
        :raise InfeasibleSolutionException if solution is infeasible
        :raise IncompleteSolutionException if solution does not contain
        """

        if len(operation_list) != Data.get_number_of_tasks():
            raise IncompleteSolutionException("Incomplete operation list")

        self.machine_makespans = compute_machine_makespans(operation_list)
        self.makespan = max(self.machine_makespans)
        self.operation_list = operation_list

    def __eq__(self, other_solution):
        return self.makespan == other_solution.makespan and self.operation_list == other_solution.operation_list

    def pprint(self):
        """
        Prints this Solution in a pretty way.

        :return: None
        """
        print(f"makespan = {self.makespan}\n"
              f"operation_list =")
        for op in self.operation_list:
            op.pprint()

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_list and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate schedule class that takes an operation_list as argument.


def iterative_makespan_wait_setup(operation, machine_makespan_memory, job_memory, machine_tasks_memory):
    """
    Computes the make span, wait time, and set up time to add when param:operation is processed next.
    The results are returned in a list where the list = [added make span, added wait time, added set up time]

    Note : this function is called iteratively in compute compute_machine_makespans_and_total_wait()

    :param operation: The operation that is next in the list of operations
    :param machine_makespan_memory:  Memory for keeping track of all machine's make span time
    :param job_memory: Memory for keeping track of all job's latest (task sequence, end time) that was processed
    :param machine_tasks_memory: Memory for keeping track of all job's latest task sequence, end time that was processed
    :return: a list of times where the list = [make span time, wait time, set up time]
    :raise: InfeasibleSolutionException if adding the operation would create an infeasible solution (operation list)
    """
    machine = operation.get_machine()  # machine Id for operation
    task = operation.get_task()  # task object
    job_id = task.get_job_id()  # job Id of task
    sequence = task.get_sequence()  # sequence number of task
    pieces = task.get_pieces()  # pieces of task

    # check if current sequence is less than last sequence processed for job
    if sequence < job_memory[job_id][0]:
        raise InfeasibleSolutionException("Infeasible operation_list")

    # get setup time given previous & current operation
    setup = Data.get_setup_time(machine_tasks_memory[machine], operation.get_task())

    # a machine needs to wait if the operation it processes next has not had all of it's predecessors processed
    wait = job_memory[job_id][1] - machine_makespan_memory[machine] if \
        job_memory[job_id][1] > machine_makespan_memory[machine] else 0

    return pieces / Data.machine_speeds[machine], wait, setup


# TODO: we may want to implement a way of detecting duplicate operations if it doesn't add too much complexity.
def compute_machine_makespans(operation_list):
    """
    Computes a list of all machine's make span times, and the total wait time of a list of operations.

    :param operation_list: The list of operations to compute the make spans and total wait time for.
    :return: a list in the form [machine make spans, total wait time] where "machine make spans"
    is a list that has length = number of machines and contains a make span for machine i at index i.
    :raise: InfeasibleSolutionException if the solution (operation list) is infeasible.


    Note: to get the actual make span of the operation list take the max of the list of machine make spans
    """
    # memory for keeping track of all machine's make span time
    # (i.e. how much time they have been processing pieces + waiting)
    machine_makespan_memory = [0] * Data.get_number_of_machines()

    # memory for keeping track of all machine's latest task
    machine_tasks_memory = [None] * Data.get_number_of_machines()

    # memory for keeping track of all job's latest (task sequence, end time) that was processed
    job_memory = [(0, 0)] * Data.get_number_of_jobs()

    # process first operation in Solution
    operation = operation_list[0]
    machine = operation.get_machine()  # machine Id for operation
    task = operation.get_task()  # task object
    job_id = task.get_job_id()  # job Id of task
    sequence = task.get_sequence()  # sequence number of task
    pieces = task.get_pieces()  # pieces of task

    runtime = pieces / Data.get_machine_speed(machine)

    # update memory modules
    # Note: wait time and set up time memory do not need to be updated
    machine_makespan_memory[machine] = runtime
    job_memory[job_id] = (sequence, machine_makespan_memory[machine])
    machine_tasks_memory[machine] = task

    for operation in operation_list[1:]:

        machine = operation.get_machine()  # machine Id for operation
        task = operation.get_task()  # task object
        job_id = task.get_job_id()  # job Id of task
        sequence = task.get_sequence()  # sequence number of task

        # tupleOfTimes = (runtime on machine, wait, setup)
        runtime_wait_setup = iterative_makespan_wait_setup(operation, machine_makespan_memory, job_memory,
                                                           machine_tasks_memory)

        # print(runtime_wait_setup)

        # compute total added time and update memory
        machine_makespan_memory[machine] += reduce((lambda x, y: x + y), runtime_wait_setup)

        # print(f"machine {machine} : {machine_makespan_memory[machine]}")

        job_memory[job_id] = (sequence, machine_makespan_memory[machine])
        machine_tasks_memory[machine] = task

    return machine_makespan_memory


def compute_makespan(operation_list):
    """
    Computes the make span time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the make span of.
    :return: The make span or completion time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    return max(compute_machine_makespans(operation_list)[0])


def compute_total_wait_time(operation_list):
    """
    Computes the total wait time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the total wait time of.
    :return: The total wait time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    # TODO we were calculating the total wait time wrong before.
    #  We were double counting. Need to find a way to not doubly count wait times on machines.
