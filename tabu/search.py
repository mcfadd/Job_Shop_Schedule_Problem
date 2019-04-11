import time

import cython_files.generate_neighbor_compiled as neighbor_generator
from cython_files.makespan_compiled import InfeasibleSolutionException

from tabu import SolutionSet, TabuList


# TODO generate_neighbor() should not generate infeasible neighbors, but it does in some cases.
#  The try except block catches these cases.
def generate_neighborhood(size, wait, solution, probability_change_machine):
    """
    This function generates a neighborhood of feasible solutions that are neighbors of the solution parameter.

    :param size: The size of the neighborhood to generate.
    :param wait: The maximum time spent to generate a neighborhood.
    :param solution: The solution to generate a neighborhood for.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :return: SolutionSet of neighboring solutions.
    """
    stop_time = time.time() + wait
    result = SolutionSet()
    while result.size < size and time.time() < stop_time:
        # the generate_neighbor function is a c-extension that was compiled with cython. see cython_files directory
        try:
            result.add(neighbor_generator.generate_neighbor(solution, probability_change_machine))
        except InfeasibleSolutionException:
            pass
    return result


def search(initial_solution, search_time, tabu_size, neighborhood_size, neighborhood_wait, probability_change_machine=0,
           benchmark=False):
    """
    This function performs Tabu search for a number of iterations given an initial feasible solution.

    :param initial_solution: The initial solution to start the Tabu search from.
    :param search_time: The time that Tabu search will run in seconds.
    :param tabu_size: The size of the Tabu list.
    :param neighborhood_size: The size of neighborhoods to generate during Tabu search.
    :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds.
    :param probability_change_machine: The probability of changing a chosen operations machine.
    :return best_solution: The best solution found while performing Tabu search.
    """
    solution = initial_solution
    best_solution = initial_solution
    tabu_list = TabuList(solution)
    stop_time = time.time() + search_time

    # variables used for benchmarks
    iterations = 0
    neighborhood_sizes = []
    tabu_list_sizes = []
    makespans = []

    while time.time() < stop_time:
        neighborhood = generate_neighborhood(neighborhood_size, neighborhood_wait, solution, probability_change_machine)
        update = False

        # Complexity of sorted() = O(n log n)
        for makespan, lst in sorted(neighborhood.solutions.items()):  # sort neighbors in increasing order by makespan
            for neighbor in sorted(lst):  # sort subset of neighbors in increasing order by machine_makespans
                if not tabu_list.solutions.contains(neighbor):
                    update = True
                    solution = neighbor
                    break
                # aspiration criteria
                elif neighbor < best_solution:  # comparison function compares machine_makespans
                    update = True
                    solution = neighbor
                    break
            if update:
                break

        if update:
            if solution < best_solution:
                best_solution = solution

            # update tabu list with seed solution
            tabu_list.enqueue(solution)
            if tabu_list.solutions.size > tabu_size:
                tabu_list.dequeue()

        if benchmark:
            iterations += 1
            neighborhood_sizes.append(neighborhood.size)
            makespans.append(solution.makespan)
            tabu_list_sizes.append(tabu_list.solutions.size)

    if benchmark:
        return best_solution, iterations, neighborhood_sizes, makespans, tabu_list_sizes
    else:
        return best_solution
