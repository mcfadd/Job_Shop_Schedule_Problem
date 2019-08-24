cimport cython
import numpy as np
cimport numpy as np
from libc.stdlib cimport abort, malloc, free

import JSSP.solution as solution

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cpdef double[::1] compute_machine_makespans(int[:, ::1] operation_2d_array,
                                            const double[:, ::1] task_processing_times_matrix,
                                            const int[:, ::1] sequence_dependency_matrix,
                                            const int[:, ::1] job_task_index_matrix):
    """
    Computes a 1d nparray of all the machine's makespan times given a 2d nparray of operations, where an operation
    is a 1d nparray of integers in the form [job_id, task_id, sequence, machine].

    :type operation_2d_array: nparray
    :param operation_2d_array: nparray of operations to compute the machine makespans for
    
    :type task_processing_times_matrix: nparray
    :param task_processing_times_matrix: task processing times matrix from static Data
    
    :type sequence_dependency_matrix: nparray
    :param sequence_dependency_matrix: sequence dependency matrix from static Data
    
    :type job_task_index_matrix: nparray
    :param job_task_index_matrix: job task index matrix from static Data
    
    :rtype: nparray
    :returns: memory view of a 1d nparray of machine make span times, where makespan[i] = makespan of machine i
    :raise: InfeasibleSolutionException if the solution is infeasible
    """
    cdef int num_jobs = sequence_dependency_matrix.shape[0]
    cdef int num_machines = task_processing_times_matrix.shape[1]

    # memory for keeping track of all machine's make span time
    cdef double[::1] machine_makespan_memory = np.zeros(num_machines)

    # memory for keeping track of all machine's latest job that was processed
    cdef int * machine_jobs_memory = <int *> malloc(sizeof(int) * num_machines)

    # memory for keeping track of all machine's latest task that was processed
    cdef int * machine_tasks_memory = <int *> malloc(sizeof(int) * num_machines)

    # memory for keeping track of all job's latest task's sequence that was processed
    cdef int * job_seq_memory = <int *> malloc(sizeof(int) * num_jobs)

    # memory for keeping track of all job's latest end time that was processed
    cdef double * prev_job_end_memory = <double *> malloc(sizeof(double) * num_jobs)

    # memory for keeping track of all job's latest end time that was processed
    cdef double * job_end_memory = <double *> malloc(sizeof(double) * num_jobs)

    if machine_jobs_memory == NULL or machine_tasks_memory == NULL or job_seq_memory == NULL or job_end_memory == NULL:
        abort()

    cdef Py_ssize_t row, i
    cdef int job_id, task_id, sequence, machine, setup, cur_task_index, prev_task_index
    cdef double wait

    for i in range(num_machines):
        machine_jobs_memory[i] = -1
        machine_tasks_memory[i] = -1

    i = 0
    for i in range(num_jobs):
        job_seq_memory[i] = 0
        job_end_memory[i] = 0.0
        prev_job_end_memory[i] = 0.0

    for row in range(operation_2d_array.shape[0]):

        job_id = operation_2d_array[row, 0]
        task_id = operation_2d_array[row, 1]
        sequence = operation_2d_array[row, 2]
        machine = operation_2d_array[row, 3]

        if machine_jobs_memory[machine] != -1:
            cur_task_index = job_task_index_matrix[job_id, task_id]
            prev_task_index = job_task_index_matrix[machine_jobs_memory[machine], machine_tasks_memory[machine]]
            setup = sequence_dependency_matrix[cur_task_index, prev_task_index]
        else:
            setup = 0

        if setup < 0 or sequence < job_seq_memory[job_id]:
            raise solution.InfeasibleSolutionException()

        if job_seq_memory[job_id] < sequence:
            prev_job_end_memory[job_id] = job_end_memory[job_id]

        if prev_job_end_memory[job_id] <= machine_makespan_memory[machine]:
            wait = 0
        else:
            wait = prev_job_end_memory[job_id] - machine_makespan_memory[machine]

        runtime = task_processing_times_matrix[job_task_index_matrix[job_id, task_id], machine]

        # compute total added time and update memory modules
        machine_makespan_memory[machine] += runtime + wait + setup
        job_end_memory[job_id] = max(machine_makespan_memory[machine], job_end_memory[job_id])
        job_seq_memory[job_id] = sequence
        machine_jobs_memory[machine] = job_id
        machine_tasks_memory[machine] = task_id

    # free the memory modules
    free(machine_jobs_memory)
    free(machine_tasks_memory)
    free(job_seq_memory)
    free(job_end_memory)
    free(prev_job_end_memory)

    return machine_makespan_memory
