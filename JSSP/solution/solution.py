import datetime

import numpy as np

from ._makespan import compute_machine_makespans
from ._schedule_creator import create_schedule_xlsx_file, create_gantt_chart
from ..data import Data
from ..exception import IncompleteSolutionException


class Solution:
    """
    Solution class which is composed of a 2d nparray of operations where
    an operation is a 1d nparray in the form [job_id, task_id, sequence, machine],
    a 1d nparray memory view of machine makespan times,
    and the makespan time.

    :type operation_2d_array: nparray
    :param operation_2d_array: 2d nparray of operations
    """

    def __init__(self, operation_2d_array):
        """
        Initializes an instance of Solution.

        First it checks if the operation_2d_array parameter is feasible,
        then it computes the nparray of machine makespan times and the makespan time of the Solution.

        :raise: InfeasibleSolutionException if solution is infeasible
        :raise: IncompleteSolutionException if solution is incomplete

        See help(Solution)
        """
        if operation_2d_array.shape[0] != Data.sequence_dependency_matrix.shape[0]:
            raise IncompleteSolutionException(f"Incomplete Solution of size {operation_2d_array.shape[0]}. "
                                              f"Should be {Data.sequence_dependency_matrix.shape[0]}")

        self.machine_makespans = compute_machine_makespans(operation_2d_array,
                                                           Data.task_processing_times_matrix,
                                                           Data.sequence_dependency_matrix,
                                                           Data.job_task_index_matrix)
        self.makespan = max(self.machine_makespans)
        self.operation_2d_array = operation_2d_array

    def __eq__(self, other_solution):
        return np.array_equal(self.operation_2d_array, other_solution.operation_2d_array)

    def __ne__(self, other_solution):
        return not self == other_solution

    def __lt__(self, other_solution):
        """
        Returns true if self is "better" than other_solution.
        Better is defined as having a lower makespan or machine_makespans if the makespans are equal.

        :type other_solution: Solution
        :param other_solution: solution to compare

        :rtype: bool
        :returns: true if self is "better" than other_solution
        """
        if self.makespan < other_solution.makespan:
            return True
        elif self.makespan > other_solution.makespan:
            return False
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
        :param other_solution: solution to compare

        :rtype: bool
        :returns: true if self is "worse" than other_solution
        """
        if self.makespan > other_solution.makespan:
            return True
        elif self.makespan < other_solution.makespan:
            return False
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

    def __getstate__(self):
        self.machine_makespans = np.asarray(self.machine_makespans)  # need to convert memory view to np array
        return {'operation_2d_array': self.operation_2d_array,
                'machine_makespans': self.machine_makespans,
                'makespan': self.makespan}

    def __setstate__(self, state):
        self.operation_2d_array = state['operation_2d_array']
        self.machine_makespans = state['machine_makespans']
        self.makespan = state['makespan']

    def create_schedule_xlsx_file(self, output_path, start_time=datetime.time(hour=8, minute=0),
                                  end_time=datetime.time(hour=20, minute=0), continuous=False):
        """
        Creates an excel file in the output_dir directory that contains the schedule for each machine of this Solution.

        :type output_path: str
        :param output_path: path to the excel file to create

        :type start_time: datetime.time
        :param start_time: start time of the work day

        :type end_time: datetime.time
        :param end_time: end time of the work day

        :type continuous: bool
        :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """
        create_schedule_xlsx_file(self, output_path, start_time=start_time, end_time=end_time, continuous=continuous)

    def iplot_gantt_chart(self, title='Gantt Chart', start_date=datetime.datetime.now(),
                          start_time=datetime.time(hour=8, minute=0), end_time=datetime.time(hour=20, minute=0),
                          continuous=False):
        """
        Plots a gantt chart of this Solution in an ipyton notebook.

        :type title: str
        :param title: name of the gantt chart

        :type start_date: datetime.datetime
        :param start_date: datetime to start the schedule from

        :type start_time: datetime.time
        :param start_time: start time of the work day

        :type end_time: datetime.time
        :param end_time: end time of the work day

        :type continuous: bool
        :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """

        create_gantt_chart(self, "", title=title, start_date=start_date, start_time=start_time,
                           end_time=end_time, iplot_bool=True, continuous=continuous)

    def create_gantt_chart_html_file(self, output_path, title='Gantt Chart', start_date=datetime.datetime.now(),
                                     start_time=datetime.time(hour=8, minute=0),
                                     end_time=datetime.time(hour=20, minute=0), auto_open=False, continuous=False):
        """
        Creates a gantt chart html file of the solution parameters in the output_dir directory.

        :type output_path: str
        :param output_path: path to the directory to place the excel file into

        :type title: str
        :param title: name of the gantt chart

        :type start_date: datetime.datetime
        :param start_date: datetime to start the schedule from

        :type start_time: datetime.time
        :param start_time: start time of the work day

        :type end_time: datetime.time
        :param end_time: end time of the work day

        :type auto_open: bool
        :param auto_open: if true the gantt chart html file is automatically opened in a browser

        :type continuous: bool
        :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """
        create_gantt_chart(self, output_path, title=title, start_date=start_date, start_time=start_time,
                           end_time=end_time, iplot_bool=False, auto_open=auto_open,
                           continuous=continuous)
