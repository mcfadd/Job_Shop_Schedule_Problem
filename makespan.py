from data_set import Data


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
        print(self.operation_list)

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_list and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate schedule class that takes an operation_list as argument.


# TODO: we may want to implement a way of detecting duplicate operations if it doesn't add too much complexity.
def compute_machine_makespans(operation_list):
    """
    Computes a list of all machine's make span times given a list of operations, where an operation
    is a list of integers in the form [job_id, task_id, sequence, machine, pieces].

    :param operation_list: The list of operations to compute the make spans and total wait time for.
    :return: a list of machine make span times, where makespan[i] = make span of machine i
    :raise: InfeasibleSolutionException if the solution (operation list) is infeasible.

    Note: to get the actual make span of the operation list take the max of the list of machine make spans
    """
    # memory for keeping track of all machine's make span time
    machine_makespan_memory = [0] * Data.get_number_of_machines()

    # memory for keeping track of all machine's latest job that was processed
    machine_jobs_memory = [-1] * Data.get_number_of_machines()

    # memory for keeping track of all machine's latest task that was processed
    machine_tasks_memory = [-1] * Data.get_number_of_machines()

    # memory for keeping track of all job's latest task's sequence that was processed
    job_seq_memory = [0] * Data.get_number_of_jobs()

    # memory for keeping track of all job's latest end time that was processed
    job_end_memory = [0] * Data.get_number_of_jobs()

    for operation in operation_list:

        job_id = operation[0]
        task_id = operation[1]
        sequence = operation[2]
        machine = operation[3]
        pieces = operation[4]

        if sequence < job_seq_memory[job_id]:
            raise InfeasibleSolutionException("Infeasible operation_list")

        setup = Data.get_setup_time((machine_jobs_memory[machine], machine_tasks_memory[machine]), (job_id, task_id))

        wait = job_end_memory[job_id] - machine_makespan_memory[machine] if job_end_memory[job_id] > machine_makespan_memory[machine] else 0

        # compute total added time and update memory
        machine_makespan_memory[machine] += pieces / Data.machine_speeds[machine] + wait + setup
        job_seq_memory[job_id] = sequence
        job_end_memory[job_id] = machine_makespan_memory[machine]
        machine_jobs_memory[machine] = job_id
        machine_tasks_memory[machine] = task_id

    return machine_makespan_memory


def compute_makespan(operation_list):
    """
    Computes the make span time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the make span of.
    :return: The make span or completion time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    return max(compute_machine_makespans(operation_list))


def compute_total_wait_time(operation_list):
    """
    Computes the total wait time in minutes of a list of Operations.

    :param operation_list: The list of Operations to compute the total wait time of.
    :return: The total wait time in minutes to execute all of the operations
    in the order they appear in operation_list.
    """
    # TODO we were calculating the total wait time wrong before.
    #  We were double counting. Need to find a way to not doubly count wait times on machines.
