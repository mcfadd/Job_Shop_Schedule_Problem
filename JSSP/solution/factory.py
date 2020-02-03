import heapq
import random

import numpy as np

from ..data import Data, CSVData
from .solution import Solution


class SolutionFactory:
    """
    Factory class for generating Solution instances.
    
    :type data: Data
    :param data: JSSP instance data
    """

    def __init__(self, data):
        self.jssp_instance_data = data

    def get_n_solutions(self, n):
        """
        Gets n random Solution instances.

        :type n: int
        :param n: number of Solutions to get

        :rtype: [Solution]
        :returns: n randomly generated Solution instances
        """
        return [self.get_solution() for _ in range(n)]

    def get_solution(self):
        """
        Gets a random Solution instance.

        :rtype: Solution
        :returns: randomly generated Solution instance
        """
        return self._generate_solution()

    def get_n_longest_process_time_first_solution(self, n):
        """
        Gets n random Solution instances that are generated using longest processing time first criteria.

        :type n: int
        :param n: number of Solutions to get

        :rtype: [Solution]
        :returns: n randomly generated Solution instances
        """
        return [self._generate_solution_w_processing_time_criteria(lpt=True) for _ in range(n)]

    def get_longest_process_time_first_solution(self):
        """
        Gets a random Solution instance that is generated using longest processing time first criteria.

        :rtype: Solution
        :returns: randomly generated Solution instance
        """
        return self._generate_solution_w_processing_time_criteria(lpt=True)

    def get_n_shortest_process_time_first_solution(self, n):
        """
        Gets n random Solution instances that are generated using shortest processing time first criteria.

        :type n: int
        :param n: number of Solutions to get

        :rtype: [Solution]
        :returns: n randomly generated Solution instances
        """
        return [self._generate_solution_w_processing_time_criteria(lpt=False) for _ in range(n)]

    def get_shortest_process_time_first_solution(self):
        """
        Gets a random Solution instance that is generated using shortest processing time first criteria.

        :rtype: Solution
        :returns: randomly generated Solution instance
        """
        return self._generate_solution_w_processing_time_criteria(lpt=False)

    def _generate_solution(self):
        """
        Generates a random Solution instance.

        :rtype: Solution
        :returns: randomly generated Solution instance
        """

        operation_list = []
        last_task_scheduled_on_machine = [None] * self.jssp_instance_data.total_number_of_machines
        available = {job.get_job_id(): [task for task in job.get_tasks() if task.get_sequence() == 0] for job in
                     self.jssp_instance_data.jobs}

        while 0 < len(available):
            get_unstuck = 0
            rand_job_id = random.choice(list(available.keys()))
            rand_task = random.choice(available[rand_job_id])
            rand_machine = np.random.choice(rand_task.get_usable_machines())

            # this loop prevents scheduling a task on a machine with sequence # > last task scheduled - 1 if the tasks are apart of the same job.
            # Without this loop Infeasible solutions may be generated. The get_unstuck variable ensures that this loop doesn't run forever.
            if isinstance(self.jssp_instance_data, CSVData):
                while last_task_scheduled_on_machine[rand_machine] is not None \
                        and last_task_scheduled_on_machine[rand_machine].get_job_id() == rand_job_id \
                        and last_task_scheduled_on_machine[rand_machine].get_sequence() + 1 < rand_task.get_sequence():

                    rand_job_id = random.choice(list(available.keys()))
                    rand_task = random.choice(available[rand_job_id])
                    rand_machine = np.random.choice(rand_task.get_usable_machines())
                    get_unstuck += 1
                    if get_unstuck > 50:
                        return self.get_solution()  # TODO this is not the best way to do this...

            available[rand_job_id].remove(rand_task)
            if len(available[rand_job_id]) == 0:
                if rand_task.get_sequence() == self.jssp_instance_data.jobs[rand_job_id].get_max_sequence():
                    # all of the tasks in the job have been scheduled
                    del available[rand_job_id]
                else:
                    # add all the tasks in the same job with the next sequence number
                    available[rand_job_id] = [t for t in self.jssp_instance_data.jobs[rand_job_id].get_tasks() if
                                              t.get_sequence() == rand_task.get_sequence() + 1]

            last_task_scheduled_on_machine[rand_machine] = rand_task
            operation_list.append([rand_job_id, rand_task.get_task_id(), rand_task.get_sequence(), rand_machine])

        return Solution(self.jssp_instance_data, np.array(operation_list, dtype=np.intc))

    def _generate_solution_w_processing_time_criteria(self, lpt):
        """
        Generates a random Solution instance with either shortest or longest processing time first criteria.

        :rtype: Solution
        :returns: randomly generated Solution instance
        """

        operation_list = []
        last_task_scheduled_on_machine = [None] * self.jssp_instance_data.total_number_of_machines
        available_heap = _JobTaskHeap(self.jssp_instance_data, maxheap=lpt)

        while 0 < len(available_heap):
            get_unstuck = 0
            rand_task = available_heap.pop_task()
            rand_job_id = rand_task.get_job_id()
            rand_machine = np.random.choice(rand_task.get_usable_machines())

            # this loop prevents scheduling a task on a machine with sequence # > last task scheduled - 1 if the tasks are apart of the same job.
            # Without this loop Infeasible solutions may be generated. The get_unstuck variable ensures that this loop doesn't run forever.
            tmp_task_list = []
            # TODO the heap (i.e. list) is depleted in this while loop which causes an index out of bound exception.
            #  This shouldn't happen if the sequence dependency matrix is correct and accounts for wait time
            if isinstance(self.jssp_instance_data, CSVData):
                while last_task_scheduled_on_machine[rand_machine] is not None \
                        and last_task_scheduled_on_machine[rand_machine].get_job_id() == rand_job_id \
                        and last_task_scheduled_on_machine[rand_machine].get_sequence() + 1 < rand_task.get_sequence():

                    # save the task that was removed but cannot be scheduled
                    tmp_task_list.append(rand_task)

                    rand_task = available_heap.pop_task()
                    rand_job_id = rand_task.get_job_id()
                    rand_machine = np.random.choice(rand_task.get_usable_machines())
                    get_unstuck += 1

                    if get_unstuck > 50:
                        return self.get_solution()

            # add the tasks that were removed back if any
            for task in tmp_task_list:
                available_heap.push_task(task)

            if len(available_heap.dict[rand_job_id]) == 0:
                if rand_task.get_sequence() == self.jssp_instance_data.jobs[rand_job_id].get_max_sequence():
                    # all of the tasks in the job have been scheduled
                    del available_heap.dict[rand_job_id]
                else:
                    # add all the tasks in the same job with the next sequence number
                    for t in self.jssp_instance_data.jobs[rand_job_id].get_tasks():
                        if t.get_sequence() == rand_task.get_sequence() + 1:
                            # available_heap.dict[rand_job_id].append(t)
                            available_heap.push_task(t)

            last_task_scheduled_on_machine[rand_machine] = rand_task
            operation_list.append([rand_job_id, rand_task.get_task_id(), rand_task.get_sequence(), rand_machine])

        return Solution(self.jssp_instance_data, np.array(operation_list, dtype=np.intc))


"""
Data structures
"""


class _JobTaskHeap:
    def __init__(self, data, maxheap=True):
        self.data = data
        self.maxheap = maxheap
        self.heap = []
        self.dict = {job.get_job_id(): [task for task in job.get_tasks() if task.get_sequence() == 0] for job in
                     self.data.jobs}
        for job in self.data.jobs:
            for task in job.get_tasks():
                if task.get_sequence() == 0:
                    heapq.heappush(self.heap,
                                   _MaxHeapObj(self.data, task) if self.maxheap else _MinHeapObj(self.data, task))

    def push_task(self, task):
        heapq.heappush(self.heap,
                       _MaxHeapObj(self.data, task) if self.maxheap else _MinHeapObj(self.data, task))
        self.dict[task.get_job_id()].append(task)

    def pop_task(self):
        task = heapq.heappop(self.heap).val
        self.dict[task.get_job_id()].remove(task)
        return task

    def __len__(self):
        return len(self.heap)


class _MaxHeapObj:
    def __init__(self, data, val):
        self.data = data
        self.val = val

    def __lt__(self, other):
        self_index = self.data.job_task_index_matrix[self.val.get_job_id(), self.val.get_task_id()]
        other_index = self.data.job_task_index_matrix[other.val.get_job_id(), other.val.get_task_id()]

        self_processing_times = [processing_time for processing_time in
                                 self.data.task_processing_times_matrix[self_index] if
                                 processing_time != -1]
        other_processing_times = [processing_time for processing_time in
                                  self.data.task_processing_times_matrix[other_index]
                                  if
                                  processing_time != -1]

        self_avg_processing_time = sum(self_processing_times) / len(self_processing_times)
        other_avg_processing_time = sum(other_processing_times) / len(other_processing_times)

        return self_avg_processing_time > other_avg_processing_time

    def __eq__(self, other):
        return self.val == other.val


class _MinHeapObj(_MaxHeapObj):
    def __lt__(self, other):
        self_index = self.data.job_task_index_matrix[self.val.get_job_id(), self.val.get_task_id()]
        other_index = self.data.job_task_index_matrix[other.val.get_job_id(), other.val.get_task_id()]

        self_processing_times = [processing_time for processing_time in
                                 self.data.task_processing_times_matrix[self_index] if
                                 processing_time != -1]
        other_processing_times = [processing_time for processing_time in
                                  self.data.task_processing_times_matrix[other_index]
                                  if
                                  processing_time != -1]

        self_avg_processing_time = sum(self_processing_times) / len(self_processing_times)
        other_avg_processing_time = sum(other_processing_times) / len(other_processing_times)

        return self_avg_processing_time < other_avg_processing_time
