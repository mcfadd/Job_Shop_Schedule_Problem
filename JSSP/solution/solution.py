import datetime
import heapq
import pickle
import random

import numpy as np

from JSSP.data import Data
from ._makespan import compute_machine_makespans
from ._schedule_creator import create_schedule_xlsx_file, create_gantt_chart


class InfeasibleSolutionException(Exception):
    pass


class IncompleteSolutionException(Exception):
    pass


class Solution:
    """
    Solution class which is composed of a 2d nparray of operations where
    an operation is a 1d nparray in the form [job_id, task_id, sequence, machine],
    a 1d nparray memory view of machine makespan times,
    and the makespan time.
    """

    def __init__(self, operation_2d_array):
        """
        Initializes an instance of Solution.

        First it checks if the operation_2d_array parameter is feasible,
        then it computes the nparray of machine makespan times and the makespan time of the Solution.

        :type operation_2d_array 2d nparray
        :param operation_2d_array: 2d nparray of operations

        :raise: InfeasibleSolutionException if solution is infeasible
        :raise: IncompleteSolutionException if solution is incomplete
        """

        if operation_2d_array.shape[0] != Data.total_number_of_tasks:
            raise IncompleteSolutionException(f"Incomplete Solution of size {operation_2d_array.shape[0]}. "
                                              f"Should be {Data.total_number_of_tasks}")

        self.machine_makespans = compute_machine_makespans(operation_2d_array,
                                                           Data.task_processing_times_matrix,
                                                           Data.sequence_dependency_matrix,
                                                           Data.job_task_index_matrix)
        self.makespan = max(self.machine_makespans)
        self.operation_2d_array = operation_2d_array

    def __eq__(self, other_solution):
        return self.makespan == other_solution.makespan and np.array_equal(
            self.machine_makespans, other_solution.machine_makespans) and np.array_equal(
            self.operation_2d_array, other_solution.operation_2d_array)

    def __ne__(self, other_solution):
        return not self == other_solution

    def __lt__(self, other_solution):
        """
        Returns true if self is "better" than other_solution.
        Better is defined as having a lower makespan or machine_makespans if the makespans are equal.

        :type other_solution: Solution
        :param other_solution: The solution to compare

        :rtype: bool
        :returns: True if self is "better" than other_solution
        """
        if self.makespan < other_solution.makespan:
            return True
        else:
            self_machine_makespans_sorted = sorted(list(self.machine_makespans), reverse=True)
            other_machine_makespans_sorted = sorted(list(other_solution.machine_makespans), reverse=True)
            for i in range(len(self_machine_makespans_sorted)):
                if self_machine_makespans_sorted[i] < other_machine_makespans_sorted[i]:
                    return True
                elif self_machine_makespans_sorted[i] > other_machine_makespans_sorted[i]:
                    return False

        return False

    def __le__(self, other_solution):
        return not self > other_solution

    def __gt__(self, other_solution):
        """
        Returns true if self is "worse" than other_solution.
        Worse is defined as having a greater makespan or machine_makespans if the makespans are equal.

        :type other_solution: Solution
        :param other_solution: The solution to compare

        :rtype: bool
        :returns: True if self is "worse" than other_solution
        """
        if self.makespan > other_solution.makespan:
            return True
        else:
            self_machine_makespans_sorted = sorted(list(self.machine_makespans), reverse=True)
            other_machine_makespans_sorted = sorted(list(other_solution.machine_makespans), reverse=True)
            for i in range(len(self_machine_makespans_sorted)):
                if self_machine_makespans_sorted[i] > other_machine_makespans_sorted[i]:
                    return True
                elif self_machine_makespans_sorted[i] < other_machine_makespans_sorted[i]:
                    return False

        return False

    def __ge__(self, other_solution):
        return not self < other_solution

    def __str__(self):
        return f"makespan = {self.makespan}\n" \
            f"machine_makespans = {list(self.machine_makespans)}\n" \
            f"operation_list =\n" \
            f"{self.operation_2d_array}"

    def create_schedule_xlsx_file(self, output_dir, start_time=datetime.time(hour=8, minute=0),
                                  end_time=datetime.time(hour=20, minute=0), filename='Schedule', continuous=False):
        """
        Creates an excel file in the output_dir directory that contains the schedule for each machine of this Solution.

        :type output_dir: str
        :param output_dir: The directory to place the excel file into

        :type start_time: datetime.time
        :param start_time: Start time of the work day

        :type end_time: datetime.time
        :param end_time: End time of the work day

        :type filename: str
        :param filename: The name of the excel file

        :type continuous: bool
        :param continuous: If true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """
        create_schedule_xlsx_file(self, output_dir, start_time=start_time, end_time=end_time, filename=filename,
                                  continuous=continuous)

    def iplot_gantt_chart(self,
                          title='Gantt Chart',
                          start_date=datetime.datetime.now(),
                          start_time=datetime.time(hour=8, minute=0),
                          end_time=datetime.time(hour=20, minute=0),
                          continuous=False):
        """
        Plots a gantt chart of this Solution in an ipyton notebook.

        :type title: str
        :param title: The name of the gantt chart

        :type start_date: datetime.datetime
        :param start_date: Datetime to start the schedule from

        :type start_time: datetime.time
        :param start_time: Start time of the work day

        :type end_time: datetime.time
        :param end_time: End time of the work day

        :type continuous: bool
        :param continuous: If true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """

        create_gantt_chart(self, "", title=title, start_date=start_date, start_time=start_time,
                           end_time=end_time, filename="", iplot_bool=True, auto_open=False,
                           continuous=continuous)

    def create_gantt_chart_html_file(self, output_dir, title='Gantt Chart', start_date=datetime.datetime.now(),
                                     start_time=datetime.time(hour=8, minute=0), end_time=datetime.time(hour=20, minute=0),
                                     filename='Gantt_Chart.html', auto_open=False, continuous=False):
        """
        Creates a gantt chart html file of the solution parameters in the output_dir directory.

        :type output_dir: str
        :param output_dir: The directory to place the excel file into

        :type title: str
        :param title: The name of the gantt chart

        :type start_date: datetime.time
        :param start_date: Datetime to start the schedule from

        :type start_time: datetime.time
        :param start_time: Start time of the work day

        :type end_time: datetime.time
        :param end_time: End time of the work day

        :type filename: str
        :param filename: The name of the excel file

        :type auto_open: bool
        :param auto_open: If true the gantt chart html file is automatically opened in a browser

        :type continuous: bool
        :param continuous: If true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """
        create_gantt_chart(self, output_dir, title=title, start_date=start_date, start_time=start_time,
                           end_time=end_time, filename=filename, iplot_bool=False, auto_open=auto_open,
                           continuous=continuous)

    def pickle_to_file(self, file_path):
        """
        Serializes this Solution to a binary file using pickle.

        :type file_path: str
        :param file_path: Path of file to serialize to

        :returns: None
        """
        self.machine_makespans = np.asarray(self.machine_makespans)  # need to convert memory view to np array
        with open(file_path, 'wb') as file:
            pickle.dump(self, file, protocol=-1)


class SolutionFactory:
    """
    Factory class for generating Solution instances.
    """

    @staticmethod
    def get_n_solutions(n):
        """
        Gets n random Solution instances.

        :type n: int
        :param n: The number of Solutions to get

        :rtype: list
        :returns: n random Solution instances
        """
        return [SolutionFactory.get_solution() for _ in range(n)]

    @staticmethod
    def get_solution():
        """
        Gets a random Solution instance.

        :rtype: Solution
        :returns: A random Solution instance
        """
        return SolutionFactory._generate_solution()

    @staticmethod
    def get_n_longest_process_time_first_solution(n):
        """
        Gets n random Solution instances that are generated using longest processing time first criteria.

        :type n: int
        :param n: The number of Solutions to get

        :rtype: list
        :returns: n random Solution instances
        """
        return [SolutionFactory._generate_solution_w_processing_time_criteria(lpt=True) for _ in range(n)]

    @staticmethod
    def get_longest_process_time_first_solution():
        """
        Gets a random Solution instance that is generated using longest processing time first criteria.

        :rtype: Solution
        :returns: A random Solution instance
        """
        return SolutionFactory._generate_solution_w_processing_time_criteria(lpt=True)

    @staticmethod
    def get_n_shortest_process_time_first_solution(n):
        """
        Gets n random Solution instances that are generated using shortest processing time first criteria.

        :type n: int
        :param n: The number of Solutions to get

        :rtype: list
        :returns: n random Solution instances
        """
        return [SolutionFactory._generate_solution_w_processing_time_criteria(lpt=False) for _ in range(n)]

    @staticmethod
    def get_shortest_process_time_first_solution():
        """
        Gets a random Solution instance that is generated using shortest processing time first criteria.

        :rtype: Solution
        :returns: A random Solution instance
        """
        return SolutionFactory._generate_solution_w_processing_time_criteria(lpt=False)

    @staticmethod
    def _generate_solution():
        """
        Generates a random Solution instance.

        :rtype: Solution
        :returns: A random Solution instance
        """

        operation_list = []
        last_task_scheduled_on_machine = [None] * Data.total_number_of_machines
        available = {job.get_job_id(): [task for task in job.get_tasks() if task.get_sequence() == 0] for job in
                     Data.jobs}

        while 0 < len(available):
            get_unstuck = 0
            rand_job_id = random.choice(list(available.keys()))
            rand_task = random.choice(available[rand_job_id])
            rand_machine = np.random.choice(rand_task.get_usable_machines())

            # this loop prevents scheduling a task on a machine with sequence # > last task scheduled - 1 if the tasks are apart of the same job.
            # Without this loop Infeasible solutions may be generated. The get_unstuck variable ensures that this loop doesn't run forever.
            while not Data.fjs_instance \
                    and last_task_scheduled_on_machine[rand_machine] is not None \
                    and last_task_scheduled_on_machine[rand_machine].get_job_id() == rand_job_id \
                    and last_task_scheduled_on_machine[rand_machine].get_sequence() + 1 < rand_task.get_sequence():

                rand_job_id = random.choice(list(available.keys()))
                rand_task = random.choice(available[rand_job_id])
                rand_machine = np.random.choice(rand_task.get_usable_machines())
                get_unstuck += 1
                if get_unstuck > 50:
                    return SolutionFactory.get_solution()  # this is not the best way to do this...

            available[rand_job_id].remove(rand_task)
            if len(available[rand_job_id]) == 0:
                if rand_task.get_sequence() == Data.jobs[rand_job_id].get_max_sequence():
                    # all of the tasks in the job have been scheduled
                    del available[rand_job_id]
                else:
                    # add all the tasks in the same job with the next sequence number
                    available[rand_job_id] = [t for t in Data.jobs[rand_job_id].get_tasks() if
                                              t.get_sequence() == rand_task.get_sequence() + 1]

            last_task_scheduled_on_machine[rand_machine] = rand_task
            operation_list.append([rand_job_id, rand_task.get_task_id(), rand_task.get_sequence(), rand_machine])

        return Solution(np.array(operation_list, dtype=np.intc))

    @staticmethod
    def _generate_solution_w_processing_time_criteria(lpt):
        """
        Generates a random Solution instance with either shortest or longest processing time first criteria.

        :rtype: Solution
        :returns: A random Solution instance
        """

        operation_list = []
        last_task_scheduled_on_machine = [None] * Data.total_number_of_machines
        available_heap = SolutionFactory._JobTaskHeap(maxheap=lpt)

        while 0 < len(available_heap):
            get_unstuck = 0
            rand_task = available_heap.pop_task()
            rand_job_id = rand_task.get_job_id()
            rand_machine = np.random.choice(rand_task.get_usable_machines())

            # this loop prevents scheduling a task on a machine with sequence # > last task scheduled - 1 if the tasks are apart of the same job.
            # Without this loop Infeasible solutions may be generated. The get_unstuck variable ensures that this loop doesn't run forever.
            tmp_task_list = []
            # TODO the heap (i.e. list) is depleted in this while loop which causes an index out of bound exception
            # This shouldn't happen if the sequence dependency matrix is correct and accounts for wait time
            while not Data.fjs_instance \
                    and last_task_scheduled_on_machine[rand_machine] is not None \
                    and last_task_scheduled_on_machine[rand_machine].get_job_id() == rand_job_id \
                    and last_task_scheduled_on_machine[rand_machine].get_sequence() + 1 < rand_task.get_sequence():

                # save the task that was removed but cannot be scheduled
                tmp_task_list.append(rand_task)

                rand_task = available_heap.pop_task()
                rand_job_id = rand_task.get_job_id()
                rand_machine = np.random.choice(rand_task.get_usable_machines())
                get_unstuck += 1

                if get_unstuck > 50:
                    return SolutionFactory.get_solution()

            # add the tasks that were removed back if any
            for task in tmp_task_list:
                available_heap.push_task(task)

            if len(available_heap.dict[rand_job_id]) == 0:
                if rand_task.get_sequence() == Data.jobs[rand_job_id].get_max_sequence():
                    # all of the tasks in the job have been scheduled
                    del available_heap.dict[rand_job_id]
                else:
                    # add all the tasks in the same job with the next sequence number
                    for t in Data.jobs[rand_job_id].get_tasks():
                        if t.get_sequence() == rand_task.get_sequence() + 1:
                            # available_heap.dict[rand_job_id].append(t)
                            available_heap.push_task(t)

            last_task_scheduled_on_machine[rand_machine] = rand_task
            operation_list.append([rand_job_id, rand_task.get_task_id(), rand_task.get_sequence(), rand_machine])

        return Solution(np.array(operation_list, dtype=np.intc))

    class _JobTaskHeap:
        def __init__(self, maxheap=True):
            self.maxheap = maxheap
            self.heap = []
            self.dict = {job.get_job_id(): [task for task in job.get_tasks() if task.get_sequence() == 0] for job in
                         Data.jobs}
            for job in Data.jobs:
                for task in job.get_tasks():
                    if task.get_sequence() == 0:
                        heapq.heappush(self.heap, SolutionFactory._MaxHeapObj(task) if self.maxheap else SolutionFactory._MinHeapObj(task))

        def push_task(self, task):
            heapq.heappush(self.heap, SolutionFactory._MaxHeapObj(task) if self.maxheap else SolutionFactory._MinHeapObj(task))
            self.dict[task.get_job_id()].append(task)

        def pop_task(self):
            task = heapq.heappop(self.heap).val
            self.dict[task.get_job_id()].remove(task)
            return task

        def __len__(self):
            return len(self.heap)

    class _MaxHeapObj(object):
        def __init__(self, val):
            self.val = val

        def __lt__(self, other):
            self_index = Data.job_task_index_matrix[self.val.get_job_id(), self.val.get_task_id()]
            other_index = Data.job_task_index_matrix[other.val.get_job_id(), other.val.get_task_id()]

            self_processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[self_index] if
                                     processing_time != -1]
            other_processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[other_index]
                                      if
                                      processing_time != -1]

            self_avg_processing_time = sum(self_processing_times) / len(self_processing_times)
            other_avg_processing_time = sum(other_processing_times) / len(other_processing_times)

            return self_avg_processing_time > other_avg_processing_time

        def __eq__(self, other):
            return self.val == other.val

    class _MinHeapObj(_MaxHeapObj):
        def __lt__(self, other):
            self_index = Data.job_task_index_matrix[self.val.get_job_id(), self.val.get_task_id()]
            other_index = Data.job_task_index_matrix[other.val.get_job_id(), other.val.get_task_id()]

            self_processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[self_index] if
                                     processing_time != -1]
            other_processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[other_index]
                                      if
                                      processing_time != -1]

            self_avg_processing_time = sum(self_processing_times) / len(self_processing_times)
            other_avg_processing_time = sum(other_processing_times) / len(other_processing_times)

            return self_avg_processing_time < other_avg_processing_time
