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

    def __init__(self, operation_list_view):
        """
        The constructor for this solution checks if the operation list is feasible,
        computes the list of machine make span times, and the max make span time.

        :param operation_list_view: The memory view of a 2D numpy array
        :raise InfeasibleSolutionException if solution is infeasible
        :raise IncompleteSolutionException if solution does not contain
        """

        if operation_list_view.shape[0] != Data.get_number_of_tasks():
            raise IncompleteSolutionException("Incomplete operation list")

        self.machine_makespans = makespan.compute_machine_makespans(operation_list_view)
        self.makespan = max(self.machine_makespans)
        self.operation_list_view = operation_list_view

    def __eq__(self, other_solution):
        return self.makespan == other_solution.makespan and np.array_equal(
            self.machine_makespans, other_solution.machine_makespans) and np.array_equal(
            self.operation_list_view, other_solution.operation_list_view)

    def pprint(self):
        """
        Prints this Solution in a pretty way. Mainly used for testing purposes

        :return: None
        """
        array = np.asarray(self.operation_list_view)
        print(f"makespan = {self.makespan}\n"
              f"operation_list =\n"
              f"{array}")

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_list and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate schedule class that takes an operation_list as argument.
