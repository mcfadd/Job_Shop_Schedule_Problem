import cython
import numpy as np
cimport numpy as np
from libc.stdlib cimport rand, RAND_MAX
from solution import Solution
from data import Data

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def generate_neighbor(solution, int probability_change_machine):
    """
    This function generates a feasible solution that is a neighbor of the solution parameter.

    :param solution: The solution to generate a neighbor of.
    :param probability_change_machine: The probability of changing a chosen operation's machine.
    :return: A neighbor of the solution parameter.
    """
    cdef int[:, ::1] dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    cdef int[:, ::1] usable_machines_matrix = Data.usable_machines_matrix
    cdef int[:, ::1] result_operation_2d_array = np.copy(solution.operation_2d_array)
    cdef int[::1] operation, usable_machines
    cdef Py_ssize_t random_index, lower_index, upper_index, placement_index, min_machine_makespan, i
    cdef int job_id, sequence
    cdef double[::1] makespans
    lower_index = 0
    upper_index = 0

    # this is to ensure we are not inserting the randomly removed operation into the same place
    while lower_index >= upper_index:

        random_index = np.random.randint(0, result_operation_2d_array.shape[0])
        operation = result_operation_2d_array[random_index]
        job_id = operation[0]
        sequence = operation[2]

        # find a lower bound for possible placement of the operation
        lower_index = random_index - 1
        while lower_index >= 0 and not (
                result_operation_2d_array[lower_index, 0] == job_id and result_operation_2d_array[lower_index, 2] == sequence - 1):
            lower_index -= 1

        lower_index = 0 if lower_index < 0 else lower_index + 1

        # find an upper bound for possible placement of the operation
        upper_index = random_index + 1
        while upper_index < result_operation_2d_array.shape[0] and not (
                result_operation_2d_array[upper_index, 0] == job_id and result_operation_2d_array[upper_index, 2] == sequence + 1):
            upper_index += 1

        if upper_index >= result_operation_2d_array.shape[0] - 1:
            upper_index = upper_index - 2
        else:
            upper_index = upper_index - 1

    result_operation_2d_array = np.delete(result_operation_2d_array, random_index, axis=0)

    # get a random placement index that is in between lower and upper index (bounds) and not equal to the random index
    placement_index = random_index
    while placement_index == random_index:
        placement_index = np.random.randint(lower_index, upper_index + 1)

    if np.random.randint(0, 100) < probability_change_machine:

        i = dependency_matrix_index_encoding[operation[0], operation[1]]
        usable_machines = usable_machines_matrix[i]
        min_machine_makespan = usable_machines[0]

        makespans = solution.machine_makespans
        i = 0
        for i in range(usable_machines.shape[0]):
            if makespans[usable_machines[i]] < makespans[min_machine_makespan]:
                min_machine_makespan = usable_machines[i]

        operation[3] = min_machine_makespan

    #print("rand", random_index)
    #print("place", placement_index)
    #print(lower_index, upper_index)

    return Solution(np.insert(result_operation_2d_array, placement_index, operation, axis=0))
