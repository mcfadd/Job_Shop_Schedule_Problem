from data_set import Data
from functools import reduce


class Solution:
    """
    This class represents a solution which is composed of a list of operations, a list of machine make span times,
    the max make span time, and a total wait time.
    """

    def __init__(self, operation_list):
        """
        The constructor for this solution checks if the operation list is feasible and computes the list of machine make span times,
        the max make span time, and a total wait time.

        :param operation_list: The list of operations of this Solution.
        """

        runtimes_and_wait = compute_machine_makespans_and_total_wait(operation_list)

        if runtimes_and_wait == -1:
            raise Exception("Infeasible operation_list")

        self.operation_list = operation_list
        self.machine_runtimes = runtimes_and_wait[0]
        self.makespan = max(runtimes_and_wait[0])
        self.wait_time = runtimes_and_wait[1]

    def __eq__(self, other_solution):
        return  self.makespan == other_solution.makespan and self.wait_time == other_solution.wait_time\
                and self.operation_list == other_solution.operation_list

    def pprint(self):
        """
        Prints this Solution in a pretty way.

        :return: None
        """
        print(f"makespan = {self.makespan}\n"
              f"wait_time = {self.wait_time}\n"
              f"operation_list =")
        for op in self.operation_list:
            op.pprint()

    # def create_schedule(self):
    # TODO complete this function


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
    """
    machine = operation.get_machine()  # machine Id for operation
    task = operation.get_task()  # task object
    job_id = task.get_job_id()  # job Id of task
    sequence = task.get_sequence()  # sequence number of task
    pieces = task.get_pieces()  # pieces of task

    # check if current sequence is less than last sequence processed for job
    if sequence < job_memory[job_id][0]:
        return -1

    # get setup time given previous & current operation
    setup = Data.get_setup_time(machine_tasks_memory[machine], operation.get_task())

    # a machine needs to wait if the operation it processes next has not had all of it's predecessors processed
    wait = job_memory[job_id][1] - machine_makespan_memory[machine] if \
        job_memory[job_id][1] > machine_makespan_memory[machine] else 0

    # return [num of pieces / speed of machine (i.e. runtime on machine), wait, setup]
    return [pieces / Data.machine_speeds[machine], wait, setup]


def compute_machine_makespans_and_total_wait(operation_list):
    """
    Computes a list of all machine's make span times, and the total wait time of a list of operations.

    :param operation_list: The list of operations to compute the make spans and total wait time for.
    :return: a list in the form [machine make spans, total wait time] where "machine make spans"
    is a list that has length = number of machines and contains a make span for machine i at index i.

    Note: to get the actual make span of the operation list take the max of the list of machine make spans
    """
    # memory for keeping track of all machine's make span time
    # (i.e. how much time they have been processing pieces + waiting)
    machine_makespan_memory = [0] * Data.get_number_of_machines()

    # memory for keeping track of all machine's latest task
    machine_tasks_memory = [None] * Data.get_number_of_machines()

    # memory for keeping track of all job's latest (task sequence, end time) that was processed
    job_memory = [(0, 0)] * Data.get_number_of_jobs()

    total_wait_time = 0

    # process first operation in Solution
    operation = operation_list[0]
    machine = operation.get_machine()  # machine Id for operation
    task = operation.get_task()  # task object
    job_id = task.get_job_id()  # job Id of task
    sequence = task.get_sequence()  # sequence number of task
    pieces = task.get_pieces()  # pieces of task

    runtime = pieces / Data.get_machine_speed(machine)

    # update memory modules
    # Note: wait time and set up time memory does not need to be updated
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

        # check if solution is infeasible
        if runtime_wait_setup == -1:
            return -1

        # compute total added time and update memory, where runtime = (runtime on machine, wait, setup)
        machine_makespan_memory[machine] += reduce((lambda x, y: x + y), runtime_wait_setup)
        job_memory[job_id] = (
            sequence, machine_makespan_memory[machine])
        machine_tasks_memory[machine] = task
        total_wait_time += runtime_wait_setup[1]

    return [machine_makespan_memory, total_wait_time]


def compute_makespan(operation_list):
    """
    Computes the make span time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the make span of.
    :return: The make span or completion time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    return max(compute_machine_makespans_and_total_wait(operation_list)[0])


def compute_wait_time(operation_list):
    """
    Computes the total wait time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the total wait time of.
    :return: The total wait time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    return compute_machine_makespans_and_total_wait(operation_list)[1]
