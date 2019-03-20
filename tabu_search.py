from random import randint
from makespan import Solution


class Node:
    def __init__(self, data_val=None):
        self.data_val = data_val
        self.next_node = None


class TabuList:
    """
    This class is a set ADT that provides enqueue and dequeue behaviors.
    """

    def __init__(self):
        self.head = self.tail = None        # use SLinkedList to keep LIFO property
        self.solutions = SolutionSet()      # use SolutionSet for more efficient search

    def enqueue(self, solution):
        """
        Adds a solution to the end of this TabuList.

        :param solution: The solution to add.
        :return: True if the solution was added.
        """

        if self.solutions.add(solution):
            new_node = Node(data_val=solution)
            if self.head is None:
                self.head = self.tail = new_node
            else:
                self.tail.next_node = new_node
                self.tail = new_node
            return True

        return False

    def dequeue(self):
        """
        Removes the solution at the beginning of this TabuList

        :return: True if a solution was dequeued.
        """

        if self.solutions.size > 0:
            head_node = self.head
            self.head = self.head.next_node
            self.solutions.remove(head_node.data_val)
            return True

        return False


class SolutionSet:
    """
    This class is a simple set ADT for containing Solution objects.
    """

    def __init__(self):
        self.size = 0
        self.solutions = {}

    def add(self, solution):
        """
        Adds a solution and increments size if the solution is not already in this SolutionSet.

        :param solution: The solution to add.
        :return: True if solution was added.
        """
        if solution.makespan not in self.solutions.keys():
            self.solutions[solution.makespan] = [solution]
            self.size += 1
            return True
        elif solution not in self.solutions[solution.makespan]:
            self.solutions[solution.makespan].append(solution)
            self.size += 1
            return True

        return False

    def remove(self, solution):
        """
        Removes a solution and decrements size if the solution is in this SolutionSet.

        :param solution: The solution to remove.
        :return: True if the solution was removed.
        """
        if solution.makespan in self.solutions.keys():
            self.solutions[solution.makespan].remove(solution)
            self.size -= 1
            return True

        return False

    def contains(self, solution):
        """
        Returns True if the solution is in this SolutionSet.

        :param solution: The solution to look for.
        :return: True if the solution is in this SolutionSet.
        """

        return solution.makespan in self.solutions.keys() and solution in self.solutions[solution.makespan]

    def pprint_makespans(self):
        """
        Prints a list of make spans for the solutions in this SolutionSet.

        :return: None
        """
        print([sol.makespan for sol in self.solutions])

    def pprint(self):
        """
        Prints all of the solutions in this SolutionSet in a pretty way.

        :return: None
        """
        for key in self.solutions.keys():
            for sol in self.solutions[key]:
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
    result = SolutionSet()
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
    tabu_list = TabuList()

    for i in range(iters):
        neighborhood = generate_neighborhood(neighborhood_size, solution)

        # only look through neighbors that have a makespan < solution.makespan
        for makespan in neighborhood.solutions.keys():
            if makespan < solution.makespan:
                for neighbor in neighborhood.solutions[makespan]:
                    if not tabu_list.solutions.contains(neighbor):
                        solution = neighbor

        if best_solution.makespan > solution.makespan:
            best_solution = solution

        tabu_list.enqueue(solution)
        if tabu_list.solutions.size >= tabu_size:
            tabu_list.dequeue()

    return best_solution
