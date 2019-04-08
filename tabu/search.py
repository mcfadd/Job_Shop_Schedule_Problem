import time

import cython_files.generate_neighbor_compiled as neighbor_generator

from tabu import SolutionSet, TabuList
from cython_files.makespan_compiled import InfeasibleSolutionException


# TODO need a better way of detecting/preventing creating infeasible neighbors. the try except block is not a proper solution.
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
    tabu_list = TabuList(solution)  # TODO right now we are making solutions tabu, but we should be making moves to solutions tabu.
    stop_time = time.time() + search_time
    iterations = 0
    neighborhood_sizes = []
    makespans = []

    while time.time() < stop_time:
        neighborhood = generate_neighborhood(neighborhood_size, neighborhood_wait, solution, probability_change_machine)
        update = False

        # TODO may want to make sorting the makespans (i.e. keys) more efficient - I'm not sure what the complexity of sorted() is.
        #  Alternatively we can modify SolutionSet to maintain sorted order when adding.
        for makespan, lst in sorted(neighborhood.solutions.items()):
            for neighbor in lst:
                if not tabu_list.solutions.contains(neighbor):
                    update = True
                    solution = neighbor
                    break
                elif makespan < solution.makespan:
                    update = True
                    solution = neighbor
                    break
            if update:
                break

        if update:
            if solution.makespan < best_solution.makespan:
                best_solution = solution

            tabu_list.enqueue(solution)
            if tabu_list.solutions.size > tabu_size:
                tabu_list.dequeue()

        if benchmark:
            iterations += 1
            neighborhood_sizes.append(neighborhood.size)
            makespans.append(solution.makespan)

    if benchmark:
        return best_solution, iterations, neighborhood_sizes, makespans
    else:
        return best_solution
