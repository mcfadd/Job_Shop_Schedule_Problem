import os
import pickle
import random
import time

import cython_files.generate_neighbor_compiled as neighbor_generator
import numpy as np
from cython_files.makespan_compiled import InfeasibleSolutionException

from tabu.structures import SolutionSet, TabuList


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
    stop_time = time.time() + wait
    result = SolutionSet()
    while result.size < size and time.time() < stop_time:
        # the generate_neighbor function is a c-extension that was compiled with cython. see cython_files directory
        try:
            result.add(neighbor_generator.generate_neighbor(seed_solution, probability_change_machine))
        except InfeasibleSolutionException:
            pass
    return result


def search(process_id, initial_solution, search_time, tabu_size, neighborhood_size, neighborhood_wait, probability_change_machine,
           benchmark=False):
    """
    This function performs Tabu search for a given duration starting with an initial solution.
    The best solution found is pickled to a file called 'solution_<process_id>' in a temporary directory for TabuSearchManager.

    :param process_id: An integer id of the tabu search process (used by tabu.manager).
    :param initial_solution: The initial solution to start the Tabu search from.
    :param search_time: The time that Tabu search will run in seconds.
    :param tabu_size: The size of the Tabu list.
    :param neighborhood_size: The size of neighborhoods to generate during Tabu search.
    :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :param benchmark: If true benchmark data is gathered (e.g. # of iterations, makespans, etc.)
    :return None.
    """
    seed_solution = initial_solution
    best_solution = initial_solution
    tabu_list = TabuList(initial_solution)
    stop_time = time.time() + search_time

    # if the seed solution is not improved after reset_threshold iterations a move to a worse solution is made to try to get out of local minima
    lacking_solution = seed_solution
    counter = 0
    reset_threshold = 50

    # variables used for benchmarks
    iterations = 0
    neighborhood_sizes = []
    tabu_list_sizes = []
    makespans = []
    minimum_makespan_iteration = 0

    while time.time() < stop_time:
        neighborhood = generate_neighborhood(neighborhood_size, neighborhood_wait, seed_solution, probability_change_machine)
        sorted_neighborhood = sorted(neighborhood.solutions.items())
        break_boolean = False

        # Complexity of sorted() = O(n log n)
        for makespan, lst in sorted_neighborhood:  # sort neighbors in increasing order by makespan
            for neighbor in sorted(lst):  # sort subset of neighbors with the same makespans by machine_makespans
                if not tabu_list.solutions.contains(neighbor):
                    # if new seed solution is not better than current seed solution add it to the tabu list
                    if not neighbor < seed_solution:
                        tabu_list.enqueue(seed_solution)
                        if tabu_list.solutions.size > tabu_size:
                            tabu_list.dequeue()

                    seed_solution = neighbor
                    break_boolean = True
                    break
                # aspiration criteria
                # elif neighbor < best_solution:  # comparison function compares machine_makespans
                #     if new seed solution is not better than current seed solution add it to the tabu list
                    # if not neighbor < seed_solution:
                    #     tabu_list.enqueue(seed_solution)
                    #     if tabu_list.solutions.size > tabu_size:
                    #         tabu_list.dequeue()
                    #
                    # seed_solution = neighbor
                    # update = True
                    # break
            if break_boolean:
                break

        if seed_solution < best_solution:
            best_solution = seed_solution
            if benchmark:
                minimum_makespan_iteration = iterations

        # if solution is not being improved after a number of iterations, force a move to a worse one
        counter += 1
        if counter > reset_threshold:
            counter = 0
            if not lacking_solution > seed_solution:
                seed_solution = random.choice(sorted_neighborhood[random.randint(10, 25)][1])

            lacking_solution = seed_solution

        if benchmark:
            iterations += 1
            neighborhood_sizes.append(neighborhood.size)
            makespans.append(seed_solution.makespan)
            tabu_list_sizes.append(tabu_list.solutions.size)

    # pickle results to file in tmp directory
    best_solution.machine_makespans = np.asarray(best_solution.machine_makespans)  # need to convert memory view to np array
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/tmp/solution_{process_id}", 'wb') as file:
        if benchmark:
            pickle.dump([best_solution, iterations, neighborhood_sizes, makespans, tabu_list_sizes, (minimum_makespan_iteration, best_solution.makespan)], file, protocol=-1)
        else:
            pickle.dump(best_solution, file, protocol=-1)
