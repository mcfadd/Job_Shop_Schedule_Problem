import datetime

import numpy as np

from ._makespan import compute_machine_makespans
from ._schedule_creator import create_schedule_xlsx_file, create_gantt_chart
from ..data import Data
from ..exception import IncompleteSolutionException


class Operation:
    def __init__(self, job_id, task_id, machine, wait, setup, runtime, start_time):
        self.job_id = job_id
        self.task_id = task_id
        self.machine = machine
        self.wait = wait
        self.setup = setup
        self.runtime = runtime
        self.setup_start_time = start_time
        self.setup_end_time = self.setup_start_time + datetime.timedelta(minutes=setup)
        self.runtime_end_time = self.setup_end_time + datetime.timedelta(minutes=runtime)

    def __repr__(self):
        return f"job_id={self.job_id}, task_id={self.task_id}, machine={self.machine}, " \
               f"wait={self.wait}, setup={self.setup}, runtime={self.runtime}\n"


class Solution:
    """
    Solution class which is composed of a 2d nparray of operations where
    an operation is a 1d nparray in the form [job_id, task_id, sequence, machine],
    a 1d nparray memory view of machine makespan times,
    and the makespan time.

    :type data: Data
    :param data: JSSP instance data

    :type operation_2d_array: nparray
    :param operation_2d_array: 2d nparray of operations
    """

    def __init__(self, data, operation_2d_array):
        """
        Initializes an instance of Solution.

        First it checks if the operation_2d_array parameter is feasible,
        then it computes the nparray of machine makespan times and the makespan time of the Solution.

        :raise: InfeasibleSolutionException if solution is infeasible
        :raise: IncompleteSolutionException if solution is incomplete

        See help(Solution)
        """
        if operation_2d_array.shape[0] != data.total_number_of_tasks:
            raise IncompleteSolutionException(f"Incomplete Solution of size {operation_2d_array.shape[0]}. "
                                              f"Should be {data.total_number_of_tasks}")

        self.machine_makespans = compute_machine_makespans(operation_2d_array,
                                                           data.task_processing_times_matrix,
                                                           data.sequence_dependency_matrix,
                                                           data.job_task_index_matrix)
        self.makespan = max(self.machine_makespans)
        self.operation_2d_array = operation_2d_array
        self.data = data

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
                'makespan': self.makespan,
                'data': self.data}

    def __setstate__(self, state):
        self.operation_2d_array = state['operation_2d_array']
        self.machine_makespans = state['machine_makespans']
        self.makespan = state['makespan']
        self.data = state['data']

    def create_schedule_xlsx_file(self, output_path, start_date=datetime.date.today(), start_time=datetime.time(hour=8, minute=0),
                                  end_time=datetime.time(hour=20, minute=0), continuous=False):
        """
        Creates an excel file that contains the schedule for each machine of this Solution.

        :type output_path: str
        :param output_path: path to the excel file to create

        :type start_date: datetime.date
        :param start_time: start date of the schedule

        :type start_time: datetime.time
        :param start_time: start time of the work day

        :type end_time: datetime.time
        :param end_time: end time of the work day

        :type continuous: bool
        :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :returns: None
        """
        create_schedule_xlsx_file(self, output_path, start_date=start_date, start_time=start_time, end_time=end_time, continuous=continuous)

    def iplot_gantt_chart(self, title='Gantt Chart', start_date=datetime.date.today(),
                          start_time=datetime.time(hour=8, minute=0), end_time=datetime.time(hour=20, minute=0),
                          continuous=False):
        """
        Plots a gantt chart of this Solution in an ipython notebook.

        :type title: str
        :param title: name of the gantt chart

        :type start_date: datetime.date
        :param start_date: date to start the schedule from

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

    def create_gantt_chart_html_file(self, output_path, title='Gantt Chart', start_date=datetime.date.today(),
                                     start_time=datetime.time(hour=8, minute=0),
                                     end_time=datetime.time(hour=20, minute=0), auto_open=False, continuous=False):
        """
        Creates a gantt chart html file of the solution.

        :type output_path: str
        :param output_path: path to the gantt chart html file to create

        :type title: str
        :param title: name of the gantt chart

        :type start_date: datetime.date
        :param start_date: date to start the schedule from

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

    def get_operation_list_for_machine(self, start_date=datetime.date.today(), start_time=datetime.time(hour=8),
                                       end_time=datetime.time(hour=20), continuous=False, machines=None):
        """
        Gets a list of Operations for a machine or set of machines.

        :type start_date: datetime.date
        :param start_date: date to start the schedule from

        :type start_time: datetime.time
        :param start_time: start time of the work day

        :type end_time: datetime.time
        :param end_time: end time of the work day

        :type continuous: bool
        :param continuous: if true a continuous schedule is created. (i.e. start_time and end_time are not used)

        :type machines: [int]
        :param machines: list of machine ids, or None

        :rtype: [Operation]
        :returns: list of Operations
        """
        result = []
        num_jobs = self.data.total_number_of_jobs
        num_machines = self.data.total_number_of_machines
        start_datetime = datetime.datetime(year=start_date.year, month=start_date.month, day=start_date.day,
                                           hour=start_time.hour, minute=start_time.minute, second=start_time.second)
        machine_datetime_dict = {machine_id: start_datetime for machine_id in range(num_machines)}

        # memory for keeping track of all machine's make span times
        machine_makespan_memory = [0] * num_machines

        # memory for keeping track of all machine's latest (job, task) that was processed
        machine_jobs_memory = [(-1, -1)] * num_machines

        # memory for keeping track of all job's latest task's sequence that was processed
        job_seq_memory = [0] * num_jobs

        # memory for keeping track of all job's previous sequence end time (used for calculating wait times)
        prev_job_seq_end_memory = [0] * num_jobs

        # memory for keeping track of all job's latest end time (used for updating prev_job_seq_end_memory)
        job_end_memory = [0] * num_jobs

        for row in range(self.operation_2d_array.shape[0]):

            job_id = self.operation_2d_array[row, 0]
            task_id = self.operation_2d_array[row, 1]
            sequence = self.operation_2d_array[row, 2]
            machine = self.operation_2d_array[row, 3]

            setup = self.data.get_setup_time(job_id, task_id, machine_jobs_memory[machine][0], machine_jobs_memory[machine][1])

            if job_seq_memory[job_id] < sequence:
                prev_job_seq_end_memory[job_id] = job_end_memory[job_id]

            if prev_job_seq_end_memory[job_id] <= machine_makespan_memory[machine]:
                wait = 0
            else:
                wait = prev_job_seq_end_memory[job_id] - machine_makespan_memory[machine]

            runtime = self.data.get_runtime(job_id, task_id, machine)

            tmp_dt = machine_datetime_dict[machine] + datetime.timedelta(minutes=wait)
            if not continuous and (tmp_dt.time() > end_time or tmp_dt.day != machine_datetime_dict[machine].day):
                machine_datetime_dict[machine] += datetime.timedelta(days=1)
                machine_datetime_dict[machine].replace(hour=start_time.hour, minute=start_time.minute,
                                                       second=start_time.second)
            else:
                machine_datetime_dict[machine] += datetime.timedelta(minutes=wait)

            tmp_dt = machine_datetime_dict[machine] + datetime.timedelta(minutes=setup + runtime)
            if not continuous and (tmp_dt.time() > end_time or tmp_dt.day != machine_datetime_dict[machine].day):
                machine_datetime_dict[machine] += datetime.timedelta(days=1)
                machine_datetime_dict[machine].replace(hour=start_time.hour, minute=start_time.minute,
                                                       second=start_time.second)
                setup = 0

            if machines is None or machine in machines:
                result.append(Operation(job_id,
                                        task_id,
                                        machine,
                                        float(wait),
                                        float(setup),
                                        float(runtime),
                                        machine_datetime_dict[machine]))  # start time

            machine_datetime_dict[machine] += datetime.timedelta(minutes=setup + runtime)

            # compute total added time and update memory modules
            machine_makespan_memory[machine] += runtime + wait + setup
            job_end_memory[job_id] = max(machine_makespan_memory[machine], job_end_memory[job_id])
            job_seq_memory[job_id] = sequence
            machine_jobs_memory[machine] = (job_id, task_id)

        return result
