cimport cython
import numpy as np
cimport numpy as np
from solution import Solution


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef int placement(int[::] operation, int[:, ::] parent):

    cdef int result = -2
    cdef Py_ssize_t row_index
    for row_index in range(parent.shape[0]):

        if operation[0] == parent[row_index, 0]:
            if operation[1] == parent[row_index, 1]:
                return 0
            if result == -2 and operation[2] <= parent[row_index, 2]:
                result = -1
            elif result == -2:
                result = 1

    return result


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
cpdef cross(int[:, ::] parent1, int[:, ::] parent2, int probability_mutate, int[:, ::1] dependency_matrix_index_encoding, int[:, ::1] usable_machines_matrix):

    cdef Py_ssize_t random_x = np.random.randint(0, parent1.shape[0] - 1)
    cdef Py_ssize_t random_y = np.random.randint(random_x, parent1.shape[0])
    cdef int placement_result
    cdef Py_ssize_t end_toplist_index = 0
    cdef Py_ssize_t end_bottomlist_index = 0
    cdef Py_ssize_t random_opeartion_index, i

    cdef int[:, ::] toplist = np.empty([parent1.shape[0] - (random_y - random_x), 5], dtype=np.intc)
    cdef int[:, ::] bottomlist = np.empty([parent1.shape[0] - (random_y - random_x), 5], dtype=np.intc)
    cdef int[:, ::] result

    for row in range(parent2.shape[0]):
        placement_result = placement(parent2[row], parent1[random_x:random_y])
        if placement_result != 0:
            if placement_result < 0:
                toplist[end_toplist_index] = parent2[row]
                end_toplist_index += 1
            else:
                bottomlist[end_bottomlist_index] = parent2[row]
                end_bottomlist_index += 1

    # build up result by concatenating top, middle, and bottom parts
    if end_toplist_index != 0:
        result = np.append(toplist[0:end_toplist_index], parent1[random_x:random_y], axis=0)
    else:
        result = parent1[random_x:random_y]

    if end_bottomlist_index != 0:
        result = np.append(result, bottomlist[0:end_bottomlist_index], axis=0)

    # mutation
    # randomly change operation's machine if probability condition is met
    if np.random.random_sample() < probability_mutate:
        random_opeartion_index = np.random.choice(np.random.randint(0, result.shape[0]))
        i = dependency_matrix_index_encoding[result[random_opeartion_index, 0],
                                             result[random_opeartion_index, 1]]
        result[random_opeartion_index, 3] = np.random.choice(usable_machines_matrix[i])

    return Solution(np.array(result))


