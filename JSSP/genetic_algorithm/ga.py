import random
import statistics
import time

from JSSP import solution
from JSSP.data import Data
from .ga_helpers import crossover


def search(runtime, population, mutation_probability, selection_size, benchmark):
    """
    This function performs a genetic algorithm for a given duration starting with an initial population.

    :param runtime: The duration that the GA search will run in seconds
    :param population: The initial population to start the GA from
    :param mutation_probability: The probability of mutating a chromosome (i.e change an operation's machine)
    :param selection_size: The size of the selection group for tournament style selection
    :param benchmark: If true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)
    :return: best_solution: The best Solution found
    """

    best_solution = min(population)
    stop_time = time.time() + runtime

    dependency_matrix_index_encoding = Data.dependency_matrix_index_encoding
    usable_machines_matrix = Data.usable_machines_matrix

    # variables used for benchmarks
    iterations = 0
    best_makespans = []
    avg_population_makespan = [statistics.mean([sol.makespan for sol in population])]
    minimum_makespan_iteration = 0

    while time.time() < stop_time:

        # tournament style selection
        selection_group = [random.randrange(len(population)) for _ in range(selection_size)]

        # sort the selection_group
        # TODO make selection_group sort more efficient
        is_sorted = True
        while is_sorted:
            is_sorted = False
            for i in range(selection_size - 1):
                if population[selection_group[i]] > population[selection_group[i + 1]]:
                    tmp = selection_group[i]
                    selection_group[i] = selection_group[i + 1]
                    selection_group[i + 1] = tmp
                    is_sorted = True

        # choose two best solutions from selection_group for breeding
        parent1_operation_2d_array = population[selection_group[0]].operation_2d_array
        parent2_operation_2d_array = population[selection_group[1]].operation_2d_array

        # breed the parents to produce child1 (parent1 cross parent2)
        # Note mutation happens in crossover function
        feasible_child = False
        while not feasible_child:
            # the try except block is because sometimes the crossover operation results in a setup of -1
            # which then produces an infeasible solution. This is due to the sequence dependency setup times matrix.
            try:
                child1 = crossover(parent1_operation_2d_array, parent2_operation_2d_array,
                                   mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                feasible_child = True
            except solution.InfeasibleSolutionException:
                if time.time() > stop_time:
                    return best_solution

        # breed the parents to produce child2 (parent2 cross parent1)
        feasible_child = False
        while not feasible_child:
            try:
                child2 = crossover(parent2_operation_2d_array, parent1_operation_2d_array,
                                   mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                feasible_child = True
            except solution.InfeasibleSolutionException:
                if time.time() > stop_time:
                    return best_solution

        # replace worse solutions in selection with children
        population[selection_group[-1]] = child1
        population[selection_group[-2]] = child2

        # check for better solution than best_solution
        if min(child1, child2) < best_solution:
            best_solution = min(child1, child2)
            if benchmark:
                minimum_makespan_iteration = iterations

        if benchmark:
            iterations += 1
            best_makespans.append(best_solution.makespan)
            avg_population_makespan.append(statistics.mean([sol.makespan for sol in population]))

    if benchmark:
        return [best_solution, iterations, best_makespans, avg_population_makespan, (minimum_makespan_iteration, best_solution.makespan)]
    else:
        return best_solution
