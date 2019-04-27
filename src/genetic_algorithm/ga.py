import random
import time

import solution
from src.genetic_algorithm.ga_helpers import cross

from data import Data


def search(search_time, initial_population, population_size, mutation_probability, verbose=False):
    """

    :param search_time:
    :param initial_population:
    :param population_size:
    :param mutation_probability:
    :param verbose:
    :return: best_solution: The best Solution found
    """

    assert population_size % 2 == 0, "population size must be even"

    best_solution = min(initial_population)
    current_population = initial_population
    stop_time = time.time() + search_time

    dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    usable_machines_matrix = Data.usable_machines_matrix

    # variables used for benchmarks
    iterations = 0
    num_infeasible_solutions = 0
    # makespans = []
    # minimum_makespan_iteration = 0

    while time.time() < stop_time:
        # compute average fitness of current population for selection criteria
        avg_makespan_of_pop = 0
        for sol in current_population:
            avg_makespan_of_pop += sol.makespan
        avg_makespan_of_pop = avg_makespan_of_pop / population_size

        # split the population and sort one of them
        pop_sorted = sorted(current_population[:int(population_size / 2)])
        pop_unsorted = current_population[int(population_size / 2):]

        # create a list of indices for unselected parents from pop2
        index_list = list(range(int(population_size / 2)))

        i = 0
        while len(index_list) > 0:
            # get next best parent solution from sorted pop (parent1)
            parent1_operation_2d_array = pop_sorted[i].operation_2d_array

            # get random parent from unsorted pop (parent2)
            random_parent2_index = index_list.pop(random.randrange(len(index_list)))
            parent2_operation_2d_array = pop_unsorted[random_parent2_index].operation_2d_array

            # breed the parents to produce child1 (parent1 cross parent2)
            feasible_child = False
            while not feasible_child:
                # the try except block is because sometimes the crossover operation results in a setup of -1
                # which then produces an infeasible solution. This is due to the sequence dependency setup times matrix.
                try:
                    child1 = cross(parent1_operation_2d_array, parent2_operation_2d_array,
                                   mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                    feasible_child = True
                except solution.InfeasibleSolutionException:
                    if verbose:
                        num_infeasible_solutions += 1
                    if time.time() > stop_time:
                        print("iterations =", iterations)
                        return best_solution

            # breed the parents to produce child2 (parent2 cross parent1)
            feasible_child = False
            while not feasible_child:
                try:
                    child2 = cross(parent2_operation_2d_array, parent1_operation_2d_array,
                                   mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                    feasible_child = True
                except solution.InfeasibleSolutionException:
                    if verbose:
                        num_infeasible_solutions += 1
                    if time.time() > stop_time:
                        print("iterations =", iterations)
                        return best_solution

            # add children to next population if they are better than the average makespan of the current population
            if child1.makespan <= avg_makespan_of_pop:
                # print("produced better than avg child1 at iteration", iterations)
                pop_sorted[i] = child1
            elif random.random() < 0.1:
                pop_sorted[i] = child1

            if child2.makespan <= avg_makespan_of_pop:
                # print("produced better than avg child2 at iteration", iterations)
                pop_unsorted[random_parent2_index] = child2
            elif random.random() < 0.1:
                pop_unsorted[random_parent2_index] = child2

            # check for better solution than best_solution
            if child1 < best_solution:
                best_solution = child1

            if child2 < best_solution:
                if verbose:
                    print("found best solution at iteration", iterations)
                best_solution = child2

        iterations += 1
        current_population = pop_sorted + pop_unsorted
        random.shuffle(current_population)

    if verbose:
        print("total iterations =", iterations)
        print("total number of infeasible solutions generated =", num_infeasible_solutions)
    return best_solution
