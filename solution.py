import pickle
import random

import cython_files.makespan_compiled as makespan
import numpy as np
import xlsxwriter

from data import Data


class IncompleteSolutionException(Exception):
    pass


class Solution:
    """
    This class represents a solution which is composed of a 2d array of operations,
    a 1d array memory view of machine make span times,
    and the max make span time.
    """

    def __init__(self, operation_2d_array):
        """
        The constructor for this solution checks if the operation list is feasible,
        computes the list of machine make span times, and the max make span time.

        :param operation_2d_array: 2D numpy array encoding a list of operations
        :raise InfeasibleSolutionException if solution is infeasible
        :raise IncompleteSolutionException if solution does not contain
        """

        if operation_2d_array.shape[0] != Data.total_number_of_tasks:
            raise IncompleteSolutionException(f"Incomplete Solution of size {operation_2d_array.shape[0]}. Should be {Data.total_number_of_tasks}")

        self.machine_makespans = makespan.compute_machine_makespans(operation_2d_array)
        self.makespan = max(self.machine_makespans)
        self.operation_2d_array = operation_2d_array

    def __eq__(self, other_solution):
        """
        Returns True if self is equal to other_solution.
        :param other_solution: The solution to compare
        :return: True if self == other_solution
        """
        return self.makespan == other_solution.makespan and np.array_equal(
            self.machine_makespans, other_solution.machine_makespans) and np.array_equal(
            self.operation_2d_array, other_solution.operation_2d_array)

    def __ne__(self, other_solution):
        """
        Returns True if self is not equal to other_solution.
        :param other_solution: The solution to compare
        :return: True if self != other_solution
        """
        return self.makespan != other_solution.makespan or not np.array_equal(
            self.machine_makespans, other_solution.machine_makespans) or not np.array_equal(
            self.operation_2d_array, other_solution.operation_2d_array)

    def __lt__(self, other_solution):
        """
        Returns True if self is "better" than other_solution.
        better is defined as having a lower makespan or machine_makespans if the makespans are equal.
        :param other_solution: The solution to compare
        :return: True if self has a lower makespan than other_solution
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

    def __gt__(self, other_solution):
        """
        Returns True if self is "worse" than other_solution.
        worse is defined as having a greater makespan or machine_makespans if the makespans are equal.
        :param other_solution: The solution to compare
        :return: True if self has a greater makespan than other_solution
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

    def pprint(self):
        """
        Prints this Solution in a pretty way.

        :return: None
        """
        print(f"makespan = {self.makespan}\n"
              f"machine_makespans = {list(self.machine_makespans)}\n"
              f"operation_list =\n"
              f"{self.operation_2d_array}")

    def create_schedule(self, output_dir):
        """
        Creates an excel file called 'Schedule.xlsx' in the output_dir directory that contains the schedule for each machine.
        The machine schedules have the following headers, Job_Task, Start, and End, which correspond to
        the Job_Task being processed, it's start, and it's end time on that machine.

        :param output_dir: The directory to place Schedule.xlsx in
        :return: None
        """
        # get all the necessary data from the static Data class
        machine_speeds = Data.machine_speeds
        sequence_dependency_matrix = Data.sequence_dependency_matrix
        sequence_dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
        num_jobs = sequence_dependency_matrix.shape[0]
        num_machines = machine_speeds.shape[0]

        # create an excel workbook and worksheet in output directory
        workbook = xlsxwriter.Workbook(f'{output_dir}/Schedule.xlsx')
        colored = workbook.add_format({'bg_color': '#E7E6E6'})
        worksheet = workbook.add_worksheet('Schedule')

        col = 0

        # Write headers to excel worksheet and format cells
        for i in range(num_machines):
            worksheet.set_column(col, col, 12)
            worksheet.write(0, col, f'Machine {i}')
            worksheet.write_row(1, col, ["Makespan =", self.machine_makespans[i], "minutes"])
            worksheet.write_row(4, col, ["Job_Task", "Start", "End"])
            worksheet.set_column(col + 3, col + 3, 2, colored)
            col += 4

        worksheet.set_row(4, 16, cell_format=colored)

        # get the operation matrix
        operation_2d_array = self.operation_2d_array

        # all of the row entries (i.e. Job_Task, Start, End) start at row 3 in the excel file
        machine_current_row = [5] * num_machines

        # memory for keeping track of all machine's make span times
        machine_makespan_memory = [0] * num_machines

        # memory for keeping track of total wait time on a machine
        machine_waitime_memory = [0] * num_machines

        # memory for keeping track of total setup time on a machine
        machine_setup_time_memory = [0] * num_machines

        # memory for keeping track of all machine's latest (job, task) that was processed
        machine_jobs_memory = [(-1, -1)] * num_machines

        # memory for keeping track of all job's latest task's sequence that was processed
        job_seq_memory = [0] * num_jobs

        # memory for keeping track of all job's previous sequence end time (used for calculating wait times)
        prev_job_seq_end_memory = [0] * num_jobs

        # memory for keeping track of all job's latest end time (used for updating prev_job_seq_end_memory)
        job_end_memory = [0] * num_jobs

        for row in range(operation_2d_array.shape[0]):

            job_id = operation_2d_array[row, 0]
            task_id = operation_2d_array[row, 1]
            sequence = operation_2d_array[row, 2]
            machine = operation_2d_array[row, 3]
            pieces = operation_2d_array[row, 4]

            # get the setup time for the current operation
            if machine_jobs_memory[machine] != (-1, -1):
                cur_task_index = sequence_dependency_matrix_index_encoding[job_id, task_id]
                prev_task_index = sequence_dependency_matrix_index_encoding[machine_jobs_memory[machine]]
                setup = sequence_dependency_matrix[cur_task_index, prev_task_index]
            else:
                setup = 0

            # update previous job sequence end t if a new sequence if
            if job_seq_memory[job_id] < sequence:
                prev_job_seq_end_memory[job_id] = job_end_memory[job_id]

            if prev_job_seq_end_memory[job_id] <= machine_makespan_memory[machine]:
                wait = 0
            else:
                wait = prev_job_seq_end_memory[job_id] - machine_makespan_memory[machine]

            # write Job_Task setup
            worksheet.write_row(machine_current_row[machine], machine * 4, [f"{job_id}_{task_id} setup",
                                                                            machine_makespan_memory[machine] + wait,
                                                                            machine_makespan_memory[
                                                                                machine] + wait + setup])

            # write Job_Task run
            worksheet.write_row(machine_current_row[machine] + 1, machine * 4, [f"{job_id}_{task_id} run",
                                                                                machine_makespan_memory[
                                                                                    machine] + wait + setup,
                                                                                machine_makespan_memory[
                                                                                    machine] + wait + setup + pieces /
                                                                                machine_speeds[machine]])

            # compute total added time and update memory modules
            machine_makespan_memory[machine] += pieces / machine_speeds[machine] + wait + setup
            machine_waitime_memory[machine] += wait
            machine_setup_time_memory[machine] += setup
            job_end_memory[job_id] = max(machine_makespan_memory[machine], job_end_memory[job_id])
            job_seq_memory[job_id] = sequence
            machine_jobs_memory[machine] = (job_id, task_id)

            # increment current row for machine by 2
            machine_current_row[machine] += 2

        col = 0
        for i in range(num_machines):
            worksheet.write_row(2, col, ["Total Wait =", machine_waitime_memory[i], "minutes"])
            worksheet.write_row(3, col, ["Total Setup =", machine_setup_time_memory[i], "minutes"])
            col += 4

        workbook.close()

    def pickle_to_file(self, file_name):
        """
        Serializes self to a binary file using pickle.
    
        :param self: Solution to serialize
        :param file_name: File name to serialize to
        :return: None
        """
        self.machine_makespans = np.asarray(self.machine_makespans)  # need to convert memory view to np array
        with open(file_name, 'wb') as file:
            pickle.dump(self, file, protocol=-1)


def generate_feasible_solution():
    """
    Generates a random feasible solution.

    :return: a random feasible solution
    """

    operation_list = []
    last_task_scheduled_on_machine = [0] * len(Data.machine_speeds)
    available = {job.get_job_id(): [task for task in job.get_tasks() if task.get_sequence() == 0] for job in
                 Data.jobs}

    while 0 < len(available):
        get_unstuck = 0
        rand_job_id = random.choice(list(available.keys()))
        rand_task = random.choice(available[rand_job_id])
        rand_machine = np.random.choice(rand_task.get_usable_machines())

        # this loop prevents scheduling a task on a machine with sequence # > last task scheduled - 1 if the tasks are apart of the same job.
        # Without this loop Infeasible solutions may be generated. The get_unstuck variable ensures that this loop doesn't run forever.
        while last_task_scheduled_on_machine[rand_machine] != 0 and \
                last_task_scheduled_on_machine[rand_machine].get_job_id() == rand_job_id and \
                last_task_scheduled_on_machine[rand_machine].get_sequence() + 1 < rand_task.get_sequence():

            rand_job_id = random.choice(list(available.keys()))
            rand_task = random.choice(available[rand_job_id])
            rand_machine = np.random.choice(rand_task.get_usable_machines())
            get_unstuck += 1
            if get_unstuck > 50:
                return generate_feasible_solution()

        available[rand_job_id].remove(rand_task)

        if len(available[rand_job_id]) == 0:
            if rand_task.get_sequence() == Data.get_job(rand_job_id).get_max_sequence():
                del available[rand_job_id]
            else:
                available[rand_job_id] = [task for task in Data.get_job(rand_job_id).get_tasks() if
                                          task.get_sequence() == rand_task.get_sequence() + 1]

        last_task_scheduled_on_machine[rand_machine] = rand_task
        operation_list.append(
            [rand_job_id, rand_task.get_task_id(), rand_task.get_sequence(), rand_machine, rand_task.get_pieces()])
    return Solution(np.array(operation_list, dtype=np.intc))
