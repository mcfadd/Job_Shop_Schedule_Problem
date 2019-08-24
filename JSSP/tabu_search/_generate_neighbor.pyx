from JSSP.solution import Solution
cimport cython
import numpy as np
cimport numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef generate_neighbor(solution, double probability_change_machine, int[:, ::1] dependency_matrix_index_encoding, int[:, ::1] usable_machines_matrix):
    """
    Generates a Solution instance that is a neighbor of the solution parameter.

    :type solution: Solution
    :param solution: solution to generate a neighbor of
    
    :type probability_change_machine: float
    :param probability_change_machine: probability of changing a chosen operation's machine in the neighbor
    
    :type dependency_matrix_index_encoding: nparray
    :param dependency_matrix_index_encoding: dependency matrix index encoding from static Data
    
    :type usable_machines_matrix: nparray
    :param usable_machines_matrix: usable machines matrix from static Data
    
    :rtype: Solution
    :returns: neighbor of the solution parameter
    """
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

    # randomly change operation's machine if probability condition is met
    if np.random.random_sample() < probability_change_machine:
        i = dependency_matrix_index_encoding[operation[0], operation[1]]
        operation[3] = np.random.choice(usable_machines_matrix[i])

    return Solution(np.insert(result_operation_2d_array, placement_index, operation, axis=0))
