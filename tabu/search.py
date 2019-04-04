import time

import cython_files.generate_neighbor_compiled as neighbor_generator

from tabu import SolutionSet, TabuList


# TODO we may want to produce a neighborhood with makespans < solution.makespan
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
            result.add(neighbor_generator.generate_neighbor(solution, probability_change_machine))
    return result


def search(initial_solution, search_time, tabu_size, neighborhood_size, neighborhood_wait, probability_change_machine=0):
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
    tabu_list = TabuList()
    stop_time = time.time() + search_time
    iterations = 0

    tabu_list.enqueue(solution)
    while time.time() < stop_time:
        neighborhood = generate_neighborhood(neighborhood_size, neighborhood_wait, solution, probability_change_machine)

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

        iterations += 1

    return best_solution, iterations
