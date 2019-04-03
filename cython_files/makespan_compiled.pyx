from data_set import Data
import cython
import numpy as np
cimport numpy as np
from libc.stdlib cimport abort, malloc, free


class InfeasibleSolutionException(Exception):
    pass

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef double[::1] compute_machine_makespans(int[:, ::1] operation_list):
    """
    Computes a list of all machine's make span times given a list of operations, where an operation
    is a list of integers in the form [job_id, task_id, sequence, machine, pieces].

    :param operation_list: The list of operations to compute the make spans and total wait time for.
    :return: a list of machine make span times, where makespan[i] = make span of machine i
    :raise: InfeasibleSolutionException if the solution (operation list) is infeasible.

    Note: to get the actual make span of the operation list take the max of the list of machine make spans
    """
    cdef const double[::1] machine_speeds = Data.machine_speeds
    cdef const int[:, ::1] sequence_dependency_matrix = Data.sequence_dependency_matrix
    cdef const int[:, ::1] sequence_dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    cdef int num_jobs = sequence_dependency_matrix.shape[0]
    cdef int num_machines = machine_speeds.shape[0]

    # memory for keeping track of all machine's make span time
    cdef double[::1] machine_makespan_memory = np.zeros(num_machines)

    # memory for keeping track of all machine's latest job that was processed
    cdef int * machine_jobs_memory = <int *> malloc(sizeof(int) * num_machines)

    # memory for keeping track of all machine's latest task that was processed
    cdef int * machine_tasks_memory = <int *> malloc(sizeof(int) * num_machines)

    # memory for keeping track of all job's latest task's sequence that was processed
    cdef int * job_seq_memory = <int *> malloc(sizeof(int) * num_jobs)

    # memory for keeping track of all job's latest end time that was processed
    cdef double * job_end_memory = <double *> malloc(sizeof(double) * num_jobs)

    cdef Py_ssize_t row, i
    cdef int job_id, task_id, sequence, machine, pieces, setup, cur_task_index, prev_task_index
    cdef double wait

    for i in range(num_machines):
        machine_jobs_memory[i] = -1
        machine_tasks_memory[i] = -1

    i = 0
    for i in range(num_jobs):
        job_seq_memory[i] = 0
        job_end_memory[i] = 0.0

    for row in range(operation_list.shape[0]):

        job_id = operation_list[row, 0]
        task_id = operation_list[row, 1]
        sequence = operation_list[row, 2]
        machine = operation_list[row, 3]
        pieces = operation_list[row, 4]

        if sequence < job_seq_memory[job_id]:
            raise InfeasibleSolutionException("Infeasible operation_list")

        if machine_jobs_memory[machine] != -1:
            cur_task_index = sequence_dependency_matrix_index_encoding[job_id, task_id]
            prev_task_index = sequence_dependency_matrix_index_encoding[machine_jobs_memory[machine], machine_tasks_memory[machine]]
            setup = sequence_dependency_matrix[cur_task_index, prev_task_index]
        else:
            setup = 0

        wait = job_end_memory[job_id] - machine_makespan_memory[machine] if job_end_memory[job_id] > machine_makespan_memory[machine] else 0

        # compute total added time and update memory
        machine_makespan_memory[machine] += pieces / machine_speeds[machine] + wait + setup
        job_seq_memory[job_id] = sequence
        job_end_memory[job_id] = machine_makespan_memory[machine]
        machine_jobs_memory[machine] = job_id
        machine_tasks_memory[machine] = task_id

    return machine_makespan_memory
