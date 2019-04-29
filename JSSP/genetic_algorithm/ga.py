import random
import time

from JSSP import solution
from JSSP.data import Data
from .ga_helpers import cross


def search(search_time, population, mutation_probability, verbose=False):
    """
    This function performs a Genetic Algorithm for a given duration starting with an initial population.

    :param search_time: The duration that the GA search will run in seconds.
    :param population: The initial population to start the GA from.
    :param mutation_probability: The probability of mutating chromosome (i.e change an operations machine).
    :param verbose: If True, extra information such as total number of iterations is printed.
    :return: best_solution: The best Solution found
    """
    group_size = 5

    best_solution = min(population)
    stop_time = time.time() + search_time

    dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    usable_machines_matrix = Data.usable_machines_matrix

    # variables used for verbose mode
    iterations = 0
    num_infeasible_solutions = 0

    while time.time() < stop_time:

        # tournament style selection
        selection_group = [random.randrange(len(population)) for _ in range(group_size)]

        # sort the selection_group
        # TODO make selection_group sort more efficient
        is_sorted = True
        while is_sorted:
            is_sorted = False
            for i in range(group_size - 1):
                if population[selection_group[i]] > population[selection_group[i + 1]]:
                    tmp = selection_group[i]
                    selection_group[i] = selection_group[i + 1]
                    selection_group[i + 1] = tmp
                    is_sorted = True

        # choose two best solutions from selection_group for breeding
        parent1_operation_2d_array = population[selection_group[0]].operation_2d_array
        parent2_operation_2d_array = population[selection_group[1]].operation_2d_array

        # breed the parents to produce child1 (parent1 cross parent2)
        feasible_child = False
        while not feasible_child:
            # the try except block is because sometimes the crossover operation results in a setup of -1
            # which then produces an infeasible solution. This is due to the sequence dependency setup times matrix.
            try:
                child1 = cross(parent1_operation_2d_array, parent2_operation_2d_array,
                               mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                # children.append(child1)
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
                # children.append(child2)
                feasible_child = True
            except solution.InfeasibleSolutionException:
                if verbose:
                    num_infeasible_solutions += 1
                if time.time() > stop_time:
                    print("iterations =", iterations)
                    return best_solution

        population[selection_group[-1]] = child1
        population[selection_group[-2]] = child2

        # check for better solution than best_solution
        if child1 < best_solution:
            if verbose:
                print("found best solution at iteration", iterations)
            best_solution = child1

        if child2 < best_solution:
            if verbose:
                print("found best solution at iteration", iterations)
            best_solution = child2

        iterations += 1

    if verbose:
        print("total iterations =", iterations)
        print("total number of infeasible solutions generated =", num_infeasible_solutions)
    return best_solution
