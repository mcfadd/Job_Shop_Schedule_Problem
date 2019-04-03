from data_set import Data
import cython_files.makespan_compiled as makespan
import numpy as np


class IncompleteSolutionException(Exception):
    pass


class Solution:
    """
    This class represents a solution which is composed of a list of operations, a list of machine make span times,
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

        if operation_2d_array.shape[0] != Data.get_number_of_tasks():
            raise IncompleteSolutionException("Incomplete operation list")

        self.machine_makespans = makespan.compute_machine_makespans(operation_2d_array)
        self.makespan = max(self.machine_makespans)
        self.operation_2d_array = operation_2d_array

    def __eq__(self, other_solution):
        return self.makespan == other_solution.makespan and np.array_equal(
            self.machine_makespans, other_solution.machine_makespans) and np.array_equal(
            self.operation_2d_array, other_solution.operation_2d_array)

    def pprint(self):
        """
        Prints this Solution in a pretty way. Mainly used for testing purposes

        :return: None
        """
        print(f"makespan = {self.makespan}\n"
              f"operation_list =\n"
              f"{self.operation_2d_array}")

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_list and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate schedule class that takes an operation_list as argument.
