from random import randint
from makespan import Solution


# TODO: make this class more efficient (e.g. use a different implementation than a list)
class Neighborhood:
    """
    This class is a simple ADT for containing feasible solutions (neighbors).
    """

    def __init__(self):
        self.size = 0
        self.solutions = []

    def add(self, solution):
        """
        Adds a solution and increments size if the solution is not already in this Neighborhood.

        :param solution: The solution to add.
        :return: None
        """
        if solution not in self.solutions:
            self.solutions.append(solution)
            self.size += 1

    def pprint_makespans(self):
        """
        Prints a list of make spans for the solutions in this Neighborhood.

        :return: None
        """
        print([sol.makespan for sol in self.solutions])

    def pprint(self):
        """
        Prints all of the solutions in this Neighborhood in a pretty way.

        :return: None
        """
        for sol in self.solutions:
            sol.pprint()


# TODO: we may want to modify this function to produce a neighbor by sometimes changing an operation's machine
#  instead of changing the placement of an operation.
def generate_neighbor(solution):
    """
    This function generates a feasible solution that is a neighbor of the solution parameter.

    :param solution: The solution to generate a neighbor of.
    :return: A feasible solution that is a neighbor of the solution parameter.
    """
    operation_list = solution.operation_list    # get the operation list of the solution
    result_operation_list = operation = None    # this is so compiler doesn't complain about uninitialized local variables
    random_index = lower_index = upper_index = 0

    # this is to ensure we are not inserting the randomly removed operation into the same place
    while lower_index == upper_index:

        result_operation_list = operation_list[:]   # make a copy so we don't mess up the original operation list
        random_index = randint(0, len(operation_list) - 1)  # remove a random operation
        operation = result_operation_list.pop(random_index)
        job_id = operation.get_task().get_job_id()  # the job id of the operation that was removed
        sequence = operation.get_task().get_sequence()  # the sequence number of the operation that was removed

        # find a lower bound for possible placement of the operation
        lower_index = min(random_index, len(result_operation_list) - 1)
        while lower_index >= 0 and not (
                result_operation_list[lower_index].get_task().get_job_id() == job_id and result_operation_list[
            lower_index].get_task().get_sequence() == sequence - 1):
            lower_index -= 1

        lower_index = 0 if lower_index < 0 else lower_index + 1     # add 1 because we shrunk the operation list by 1

        # find an upper bound for possible placement of the operation
        upper_index = min(random_index, len(result_operation_list) - 1)
        while upper_index < len(result_operation_list) and not (
                result_operation_list[upper_index].get_task().get_job_id() == job_id and result_operation_list[
            upper_index].get_task().get_sequence() == sequence + 1):
            upper_index += 1

        upper_index = upper_index - 1 if upper_index > len(result_operation_list) else upper_index

    # get a random placement index that is in between lower and upper index (bounds) and not equal to the random index
    placement_index = random_index
    while placement_index == random_index:
        placement_index = randint(lower_index, upper_index)

    # insert the operation into the result operation list at the placement index
    result_operation_list.insert(placement_index, operation)

    # create and return a neighboring solution
    return Solution(result_operation_list)


# TODO: we may want to find a more efficient way of detecting/preventing duplicate neighbors
#  or we may want to change the stopping criteria so it is not dependent on the size of the neighborhood,
#  for that could cause some potential problems if there aren't a number of neighboring solutions = size.
def generate_neighborhood(size, solution):
    """
    This function generates a neighborhood of feasible solutions that are neighbors of the solution parameter.

    :param size: The size of the neighborhood to generate.
    :param solution: The solution to generate a neighborhood for.
    :return: Neighborhood of feasible solutions.
    """
    result = Neighborhood()
    while result.size < size:
        result.add(generate_neighbor(solution))

    return result


# TODO: we probably want to make the stopping condition time based instead of a number of iterations.
def search(initial_solution, iters, tabu_size, neighborhood_size):
    """
    This function performs Tabu search for a number of iterations given an initial feasible solution.

    :param initial_solution: The initial solution to start the Tabu search from.
    :param iters: The number of iterations that Tabu search will execute.
    :param tabu_size: The size of the Tabu list.
    :param neighborhood_size: The size of Neighborhoods to generate during Tabu search.
    :return best_solution: The best solution found while performing Tabu search.
    """
    solution = initial_solution
    best_solution = initial_solution
    tabu_list = list()  # TODO we probably want to make searching this better than linear search which is O(n)

    for i in range(iters):

        for neighbor in generate_neighborhood(neighborhood_size, solution).solutions:
            if neighbor not in tabu_list and neighbor.makespan < solution.makespan:
                solution = neighbor

        if best_solution.makespan > solution.makespan:
            best_solution = solution

        tabu_list.append(solution)
        if len(tabu_list) >= tabu_size:
            tabu_list.pop(0)

    return best_solution
