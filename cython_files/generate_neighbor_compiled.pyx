from libc.stdlib cimport rand, RAND_MAX
from solution import Solution
from data_set import Data
import cython
import numpy as np
cimport numpy as np


#@cython.boundscheck(False)
#@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def generate_neighbor(solution, int probability_change_machine):
    """
    This function generates a feasible solution that is a neighbor of the solution parameter.

    :param solution: The solution to generate a neighbor of.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :return: A feasible solution that is a neighbor of the solution parameter.
    """
    cdef int[:, ::1] operation_list = solution.operation_list
    cdef int[:, ::1] result_operation_list
    cdef int[::1] operation
    cdef Py_ssize_t random_index, lower_index, upper_index, placement_index, min_machine_makespan, machine
    cdef int job_id, sequence
    cdef double[::1] makespans
    lower_index = 0
    upper_index = 0

    # this is to ensure we are not inserting the randomly removed operation into the same place
    while lower_index == upper_index:

        result_operation_list = np.copy(operation_list)   # make a copy so we don't mess up the original operation list
        random_index = np.random.randint(0, operation_list.shape[0])
        operation = result_operation_list[random_index]
        result_operation_list = np.delete(result_operation_list, (random_index), axis=0)
        job_id = operation[0]  # the job id of the operation that was removed
        sequence = operation[2]  # the sequence number of the operation that was removed

        # find a lower bound for possible placement of the operation
        lower_index = min(random_index, result_operation_list.shape[0] - 1)
        while lower_index >= 0 and not (
                result_operation_list[lower_index, 0] == job_id and result_operation_list[lower_index, 2] == sequence - 1):
            lower_index -= 1

        lower_index = 0 if lower_index < 0 else lower_index + 1     # add 1 because we shrunk the operation list by 1

        # find an upper bound for possible placement of the operation
        upper_index = min(random_index, result_operation_list.shape[0] - 1)
        while upper_index < result_operation_list.shape[0] and not (
                result_operation_list[upper_index, 0] == job_id and result_operation_list[upper_index, 2] == sequence + 1):
            upper_index += 1

        upper_index = upper_index - 1 if upper_index > result_operation_list.shape[0] else upper_index

    # get a random placement index that is in between lower and upper index (bounds) and not equal to the random index
    placement_index = random_index
    while placement_index == random_index:
        placement_index = np.random.randint(lower_index, upper_index + 1)

    if int(rand()/(RAND_MAX*100)) < probability_change_machine:
        usable_machines = Data.get_job(operation[0]).get_task(operation[1]).get_usable_machines()
        min_machine_makespan = usable_machines[0]

        makespans = solution.machine_makespans
        for machine in usable_machines:
            if makespans[machine] < makespans[min_machine_makespan]:
                min_machine_makespan = machine

        operation[3] = min_machine_makespan

    # insert the operation into the result operation list at the placement index
    result_operation_list = np.insert(result_operation_list, (placement_index), operation, axis=0)

    # create and return a neighboring solution
    return Solution(result_operation_list)
