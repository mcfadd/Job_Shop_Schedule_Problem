from data_set import Data
import cython
import numpy as np
cimport numpy as np


class InfeasibleSolutionException(Exception):
    pass

#@cython.boundscheck(False)
#@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def compute_machine_makespans(int[:, :] operation_list):
    """
    Computes a list of all machine's make span times given a list of operations, where an operation
    is a list of integers in the form [job_id, task_id, sequence, machine, pieces].

    :param operation_list: The list of operations to compute the make spans and total wait time for.
    :return: a list of machine make span times, where makespan[i] = make span of machine i
    :raise: InfeasibleSolutionException if the solution (operation list) is infeasible.

    Note: to get the actual make span of the operation list take the max of the list of machine make spans
    """
    cdef double[::1] machine_speeds = Data.machine_speeds
    cdef int[:, ::1] sequence_dependency_matrix = Data.sequence_dependency_matrix
    cdef Py_ssize_t rows = operation_list.shape[0]
    cdef int num_jobs = sequence_dependency_matrix.shape[0]
    cdef int num_machines = machine_speeds.shape[0]

    # memory for keeping track of all machine's make span time
    cdef double[::1] machine_makespan_memory = np.zeros(num_machines)

    # memory for keeping track of all machine's latest job that was processed
    cdef int[::1] machine_jobs_memory = np.full(num_machines, -1, dtype=np.intc)

    # memory for keeping track of all machine's latest task that was processed
    cdef int[::1] machine_tasks_memory = np.full(num_machines, -1, dtype=np.intc)

    # memory for keeping track of all job's latest task's sequence that was processed
    cdef int[::1] job_seq_memory = np.zeros(num_jobs, dtype=np.intc)

    # memory for keeping track of all job's latest end time that was processed
    cdef double[::1] job_end_memory = np.zeros(num_jobs)

    cdef Py_ssize_t row
    cdef int job_id, task_id, sequence, machine, pieces, setup, cur_task_index, prev_task_index
    cdef double wait
    for row in range(rows):

        job_id = operation_list[row, 0]
        task_id = operation_list[row, 1]
        sequence = operation_list[row, 2]
        machine = operation_list[row, 3]
        pieces = operation_list[row, 4]

        if sequence < job_seq_memory[job_id]:
            raise InfeasibleSolutionException("Infeasible operation_list")

        if machine_jobs_memory[machine] != -1:
            cur_task_index = Data.dependency_matrix_index_encoding[(job_id, task_id)]
            prev_task_index = Data.dependency_matrix_index_encoding[(machine_jobs_memory[machine], machine_tasks_memory[machine])]
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

    return np.array(machine_makespan_memory)
