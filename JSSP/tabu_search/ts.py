import os
import pickle
import random
import time

import numpy as np

from JSSP.data import Data
from JSSP.solution import InfeasibleSolutionException
from .generate_neighbor import generate_neighbor


# TODO generate_neighbor() should not generate infeasible neighbors, but it does in some cases.
#  The try except block catches these cases.
def generate_neighborhood(size, wait, seed_solution, probability_change_machine):
    """
    This function generates a neighborhood of feasible solutions that are neighbors of the seed solution parameter.

    :param size: The size of the neighborhood to generate.
    :param wait: The maximum time spent to generate a neighborhood.
    :param seed_solution: The solution to generate a neighborhood of.
    :param probability_change_machine: The probability of changing a chosen operations machine while generating a neighbor.
    :return: SolutionSet of neighboring solutions.
    """
    dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    usable_machines_matrix = Data.usable_machines_matrix
    stop_time = time.time() + wait
    result = SolutionSet()
    while result.size < size and time.time() < stop_time:
        # the generate_neighbor function is a c-extension that was compiled with cython. see cython_files directory
        try:
            result.add(generate_neighbor(seed_solution, probability_change_machine,
                                         dependency_matrix_index_encoding, usable_machines_matrix))
        except InfeasibleSolutionException:
            pass
    return result


def search(process_id, initial_solution, runtime, tabu_list_size, neighborhood_size, neighborhood_wait,
           probability_change_machine, benchmark=False):
    """
    This function performs Tabu Search for a given duration starting with an initial solution.
    The best solution found is pickled to a file called 'solution_<process_id>' in a temporary directory for TabuSearchManager.

    :param process_id: An integer id of the tabu_search search process (used by tabu_search.manager).
    :param initial_solution: The initial solution to start the Tabu search from.
    :param runtime: The duration that Tabu search will run in seconds.
    :param tabu_list_size: The size of the Tabu list.
    :param neighborhood_size: The size of neighborhoods to generate during Tabu search.
    :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :param benchmark: If true benchmark data is gathered (e.g. # of iterations, makespans, etc.)
    :return None.
    """
    seed_solution = initial_solution
    best_solution = initial_solution
    tabu_list = TabuList(initial_solution)
    stop_time = time.time() + runtime

    # if the seed solution is not improved after reset_threshold iterations a move to a worse solution is made to try to get out of local minima
    lacking_solution = seed_solution
    counter = 0
    reset_threshold = 100

    # variables used for benchmarks
    iterations = 0
    neighborhood_sizes = []
    tabu_list_sizes = []
    makespans = []
    minimum_makespan_iteration = 0

    while time.time() < stop_time:
        neighborhood = generate_neighborhood(neighborhood_size, neighborhood_wait, seed_solution,
                                             probability_change_machine)
        sorted_neighborhood = sorted(neighborhood.solutions.items())
        break_boolean = False

        # Complexity of sorted() = O(n log n)
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
            best_solution = seed_solution
            if benchmark:
                minimum_makespan_iteration = iterations

        # if solution is not being improved after a number of iterations, force a move to a worse one
        counter += 1
        if counter > reset_threshold:
            if not lacking_solution > seed_solution:
                # add the seed solution to the tabu list
                tabu_list.enqueue(seed_solution)
                if tabu_list.solutions.size > tabu_list_size:
                    tabu_list.dequeue()
                # choose a worse solution
                seed_solution = sorted_neighborhood[random.randint(5, 15)][1][0]

            counter = 0
            lacking_solution = seed_solution

        if benchmark:
            iterations += 1
            neighborhood_sizes.append(neighborhood.size)
            makespans.append(seed_solution.makespan)
            tabu_list_sizes.append(tabu_list.solutions.size)

    # pickle results to file in tmp directory
    best_solution.machine_makespans = np.asarray(
        best_solution.machine_makespans)  # need to convert memory view to np array
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/tmp/solution_{process_id}", 'wb') as file:
        if benchmark:
            pickle.dump([best_solution, iterations, neighborhood_sizes, makespans, tabu_list_sizes,
                         (minimum_makespan_iteration, best_solution.makespan)], file, protocol=-1)
        else:
            pickle.dump(best_solution, file, protocol=-1)


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

        :param solution: The solution to add.
        :return: None
        """

        self.solutions.add(solution)
        new_node = Node(data_val=solution)
        self.tail.next_node = new_node
        self.tail = new_node

    def dequeue(self):
        """
        Removes the solution at the beginning of this TabuList

        :return: Solution that was dequeued
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
        Adds a solution and increments size if the solution is not already in this SolutionSet.

        :param solution: The solution to add.
        :return: True if solution was added.
        """
        if solution.makespan not in self.solutions:
            self.solutions[solution.makespan] = [solution]
        else:
            self.solutions[solution.makespan].append(solution)

        self.size += 1

    def remove(self, solution):
        """
        Removes a solution and decrements size if the solution is in this SolutionSet.

        :param solution: The solution to remove.
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

        :param solution: The solution to look for.
        :return: True if the solution is in this SolutionSet.
        """
        return solution.makespan in self.solutions and solution in self.solutions[solution.makespan]

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
        for lst in self.solutions.values():
            for sol in lst:
                sol.pprint()
