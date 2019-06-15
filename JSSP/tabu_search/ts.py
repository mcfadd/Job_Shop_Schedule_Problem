import pickle
import random
import time

import numpy as np

from JSSP.data import Data
from JSSP.solution import InfeasibleSolutionException
from .generate_neighbor import generate_neighbor


def generate_neighborhood(solution, size, wait, probability_change_machine, dependency_matrix_index_encoding,
                          usable_machines_matrix):
    """
    This function generates a neighborhood of feasible solutions that are neighbors of the seed solution parameter.

    :param solution: The solution to generate a neighborhood of
    :param size: The size of the neighborhood to generate
    :param wait: The maximum time spent to generate a neighborhood
    :param probability_change_machine: The probability of changing a chosen operations machine while generating a neighbor
    :param dependency_matrix_index_encoding: Dependency matrix index encoding from static Data
    :param usable_machines_matrix: Usable machines matrix from static Data
    :return: SolutionSet of neighboring solutions
    """
    stop_time = time.time() + wait
    result = SolutionSet()
    while result.size < size and time.time() < stop_time:
        try:
            neighbor = generate_neighbor(solution, probability_change_machine, dependency_matrix_index_encoding,
                                         usable_machines_matrix)

            if not result.contains(neighbor):
                result.add(neighbor)

        except InfeasibleSolutionException:
            # this should not happen
            # if it does don't add the infeasible solution to the neighborhood
            pass
    return result


def search(child_results_queue, initial_solution, stopping_condition, time_condition, tabu_list_size, neighborhood_size,
           neighborhood_wait, probability_change_machine, reset_threshold, benchmark):
    """
    This function performs Tabu Search for a given duration starting with an initial solution.
    The best solution found is pickled to a file called 'solution<process_id>' in a temporary directory.

    :param child_results_queue: A multiprocessing.Queue object that stores the results for the parent process
    :param initial_solution: The initial solution to start the tabu search from
    :param stopping_condition: Integer indicating either the duration in seconds or the number of iterations to search
    :param time_condition: If true search is ran for 'stopping_condition' number of seconds else it is ran for 'stopping_condition' number of iterations
    :param tabu_list_size: The size of the Tabu list
    :param neighborhood_size: The size of neighborhoods to generate during Tabu search
    :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds
    :param probability_change_machine: The probability of changing a chosen operations machine
    :param reset_threshold: The number of iteration to potentially force a worse move after if the best solution is not improved
    :param benchmark: If true benchmark data is gathered (e.g. # of iterations, makespans, etc.)
    :return None.
    """

    # get static data
    dependency_matrix_index_encoding = Data.job_task_index_matrix
    usable_machines_matrix = Data.usable_machines_matrix

    # ts variables
    seed_solution = initial_solution
    best_solution = initial_solution
    tabu_list = TabuList(initial_solution)

    # variables used for restarts
    lacking_solution = seed_solution
    counter = 0

    iterations = 0

    # variables used for benchmarks
    neighborhood_sizes = []
    tabu_list_sizes = []
    makespans = []
    best_solution_iteration = 0

    # create stopping condition function
    if time_condition:
        stop_time = time.time() + stopping_condition

        def stop_condition():
            return time.time() >= stop_time
    else:
        def stop_condition():
            return iterations >= stopping_condition

    while not stop_condition():
        neighborhood = generate_neighborhood(seed_solution, neighborhood_size, neighborhood_wait,
                                             probability_change_machine, dependency_matrix_index_encoding,
                                             usable_machines_matrix)
        sorted_neighborhood = sorted(neighborhood.solutions.items())
        break_boolean = False

        for makespan, lst in sorted_neighborhood:  # sort neighbors in increasing order by makespan
            for neighbor in sorted(lst):  # sort subset of neighbors with the same makespans
                if not tabu_list.solutions.contains(neighbor):
                    # if new seed solution is not better than current seed solution add it to the tabu list
                    if neighbor.makespan >= seed_solution.makespan:
                        tabu_list.enqueue(seed_solution)
                        if tabu_list.solutions.size > tabu_list_size:
                            tabu_list.dequeue()

                    seed_solution = neighbor
                    break_boolean = True
                    break

            if break_boolean:
                break

        if seed_solution < best_solution:
            best_solution = seed_solution  # update best solution
            if benchmark:
                best_solution_iteration = iterations

        # if solution is not being improved after a number of iterations, force a move to a worse one
        counter += 1
        if counter > reset_threshold:
            if not lacking_solution > seed_solution and len(sorted_neighborhood) > 10:
                # add the seed solution to the tabu list
                tabu_list.enqueue(seed_solution)
                if tabu_list.solutions.size > tabu_list_size:
                    tabu_list.dequeue()
                # choose a worse solution from the neighborhood
                seed_solution = sorted_neighborhood[random.randint(1, int(0.2 * len(sorted_neighborhood)))][1][0]

            counter = 0
            lacking_solution = seed_solution

        if benchmark:
            iterations += 1
            neighborhood_sizes.append(neighborhood.size)
            makespans.append(seed_solution.makespan)
            tabu_list_sizes.append(tabu_list.solutions.size)
        elif not time_condition:
            iterations += 1

    # pickle results and add to Queue
    # need to convert memory view to np array
    best_solution.machine_makespans = np.asarray(best_solution.machine_makespans)
    if benchmark:
        child_results_queue.put(pickle.dumps([best_solution, iterations, neighborhood_sizes, makespans, tabu_list_sizes,
                                              (best_solution_iteration, best_solution.makespan)], protocol=-1))
    else:
        child_results_queue.put(pickle.dumps(best_solution, protocol=-1))


''' Below are the data structures used by Tabu Search '''


class Node:
    def __init__(self, data_val=None):
        self.data_val = data_val
        self.next_node = None


class TabuList:
    """
    This class is a set ADT that provides enqueue and dequeue behaviors.
    """

    def __init__(self, initial_solution):
        self.head = self.tail = Node(data_val=initial_solution)  # use linked list to keep FIFO property
        self.solutions = SolutionSet()
        self.solutions.add(initial_solution)

    def enqueue(self, solution):
        """
        Adds a solution to the end of this TabuList.

        :param solution: The solution to add
        :return: None
        """

        self.solutions.add(solution)
        new_node = Node(data_val=solution)
        self.tail.next_node = new_node
        self.tail = new_node

    def dequeue(self):
        """
        Removes the solution at the beginning of this TabuList

        :return: Solution that was removed
        """

        head_node = self.head
        self.head = self.head.next_node
        self.solutions.remove(head_node.data_val)
        return head_node.data_val


class SolutionSet:
    """
    This class is a simple set ADT for containing Solution objects.
    """

    def __init__(self):
        self.size = 0
        self.solutions = {}

    def add(self, solution):
        """
        Adds a solution and increments size.

        :param solution: The solution to add
        :return: None
        """
        if solution.makespan not in self.solutions:
            self.solutions[solution.makespan] = [solution]
        else:
            self.solutions[solution.makespan].append(solution)

        self.size += 1

    def remove(self, solution):
        """
        Removes a solution and decrements size.

        :param solution: The solution to remove
        :return: None
        """
        if len(self.solutions[solution.makespan]) == 1:
            del self.solutions[solution.makespan]
        else:
            self.solutions[solution.makespan].remove(solution)

        self.size -= 1

    def contains(self, solution):
        """
        Returns True if the solution is in this SolutionSet.

        :param solution: The solution to look for
        :return: True if the solution is in this SolutionSet
        """
        return solution.makespan in self.solutions and solution in self.solutions[solution.makespan]
