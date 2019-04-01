from data_set import Data
import cython_files.makespan_compiled as makespan


class IncompleteSolutionException(Exception):
    pass


class Solution:
    """
    This class represents a solution which is composed of a list of operations, a list of machine make span times,
    and the max make span time.
    """

    def __init__(self, operation_list):
        """
        The constructor for this solution checks if the operation list is feasible,
        computes the list of machine make span times, and the max make span time.

        :param operation_list: The list of operations of this Solution.
        :raise InfeasibleSolutionException if solution is infeasible
        :raise IncompleteSolutionException if solution does not contain
        """

        if operation_list.shape[0] != Data.get_number_of_tasks():
            raise IncompleteSolutionException("Incomplete operation list")

        self.machine_makespans = makespan.compute_machine_makespans(operation_list)
        self.makespan = max(self.machine_makespans)
        self.operation_list = operation_list

    def __eq__(self, other_solution):
        return self.makespan == other_solution.makespan and self.operation_list == other_solution.operation_list

    def pprint(self):
        """
        Prints this Solution in a pretty way.

        :return: None
        """
        print(f"makespan = {self.makespan}\n"
              f"operation_list =")
        print(self.operation_list)

    # def create_schedule(self):
    # TODO complete this function.
    #  Need to iterate over self.operation_list and create a schedule for each machine.
    #  The setup time, start time, end time, and wait time are needed for each operation.
    #  We may want to create a separate schedule class that takes an operation_list as argument.
