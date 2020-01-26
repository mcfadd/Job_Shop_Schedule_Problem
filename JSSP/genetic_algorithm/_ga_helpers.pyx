from ..solution import Solution
cimport cython
import numpy as np
cimport numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef int _check_placement(int[::1] operation, int[:, ::1] parent_operation_block):
    """
    Checks if an operation is already in or belongs above/below a parent's selected block of operations.
    
    :type operation: 1d nparray
    :param operation: operation to check placement for
    
    :type parent_operation_block: 2d nparray
    :param parent_operation_block: block of operations from the parent solution
    
    :rtype: int
    :returns: negative int if operation belongs above, 0 if operation is in, or positive int if operation belongs below parent block of operations
    """
    cdef int result = -2
    cdef Py_ssize_t row_index
    for row_index in range(parent_operation_block.shape[0]):

        if operation[0] == parent_operation_block[row_index, 0]:
            if operation[1] == parent_operation_block[row_index, 1]:
                return 0
            if result == -2 and operation[2] <= parent_operation_block[row_index, 2]:
                result = -1
            elif result == -2:
                result = 1

    return result


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef crossover(parent1, parent2, double probability_mutate, int[:, ::1] dependency_matrix_index_encoding, int[:, ::1] usable_machines_matrix):
    """
    Crossover operation for GA.
    
    Randomly chooses a contiguous block of operations from parent1, 
    fills the remaining operations from parent2 around the block to produce a child solution,
    then mutates the child solution if the mutation criteria is met.
    
    See https://en.wikipedia.org/wiki/Crossover_(genetic_algorithm) for more info on crossover
    See https://en.wikipedia.org/wiki/Mutation_(genetic_algorithm) for more info on mutation
    
    :type parent1: Solution
    :param parent1: parent to pick a block of operations from
    
    :type parent2: Solution
    :param parent2: parent to iterate over
    
    :type probability_mutate: float
    :param probability_mutate: probability of mutating a chromosome (i.e change an operation's machine)
    
    :type dependency_matrix_index_encoding: nparray
    :param dependency_matrix_index_encoding: dependency matrix index encoding from static Data
    
    :type usable_machines_matrix: nparray
    :param usable_machines_matrix: usable machines matrix from static Data
    
    :rtype: Solution
    :returns: child Solution
    """
    cdef int[:, ::1] p1_operation_array = np.copy(parent1.operation_2d_array)
    cdef int[:, ::1] p2_operation_array = np.copy(parent2.operation_2d_array)

    cdef Py_ssize_t random_x = np.random.randint(0, p1_operation_array.shape[0] - 1)
    cdef Py_ssize_t random_y = np.random.randint(random_x, p1_operation_array.shape[0])
    cdef int placement
    cdef Py_ssize_t end_toplist_index = 0
    cdef Py_ssize_t end_bottomlist_index = 0
    cdef Py_ssize_t random_operation_index, i

    cdef int[:, ::1] toplist = np.empty([p1_operation_array.shape[0] - (random_y - random_x), 4], dtype=np.intc)
    cdef int[:, ::1] bottomlist = np.empty([p1_operation_array.shape[0] - (random_y - random_x), 4], dtype=np.intc)
    cdef int[:, ::1] result

    for row in range(p2_operation_array.shape[0]):
        placement = _check_placement(p2_operation_array[row], p1_operation_array[random_x:random_y])
        if placement < 0:
            toplist[end_toplist_index] = p2_operation_array[row]
            end_toplist_index += 1
        elif placement > 0:
            bottomlist[end_bottomlist_index] = p2_operation_array[row]
            end_bottomlist_index += 1

    # build up result by concatenating top, middle, and bottom parts
    if end_toplist_index != 0:
        result = np.append(toplist[0:end_toplist_index], p1_operation_array[random_x:random_y], axis=0)
    else:
        result = p1_operation_array[random_x:random_y]

    if end_bottomlist_index != 0:
        result = np.append(result, bottomlist[0:end_bottomlist_index], axis=0)

    # mutation
    # randomly change operation's machine if probability condition is met
    if np.random.random_sample() < probability_mutate:
        random_operation_index = np.random.randint(0, result.shape[0])
        i = dependency_matrix_index_encoding[result[random_operation_index, 0],
                                             result[random_operation_index, 1]]
        result[random_operation_index, 3] = np.random.choice(usable_machines_matrix[i])

    return Solution(parent1.data, np.array(result))
