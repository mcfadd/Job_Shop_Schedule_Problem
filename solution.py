import pickle
import random

import cython_files.makespan_compiled as makespan
import numpy as np

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

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_2d_array and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate class for producing the schedules.


def pickle_to_file(solution, file_name):
    """
    Serializes a solution to a binary file using pickle.

    :param solution: Solution to serialize
    :param file_name: File name to serialize to
    :return: None
    """
    solution.machine_makespans = np.asarray(solution.machine_makespans)  # need to convert memory view to np array
    with open(file_name, 'wb') as file:
        pickle.dump(solution, file, protocol=-1)


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
