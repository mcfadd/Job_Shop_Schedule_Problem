import random
import statistics
import time

from JSSP import solution
from JSSP.data import Data
from .ga_helpers import crossover


def search(stopping_condition, time_condition, population, mutation_probability, selection_size, benchmark):
    """
    This function performs a genetic algorithm for a given duration starting with an initial population.

    :param stopping_condition: Integer indicating either the duration in seconds or the number of iterations to search
    :param time_condition: If true search is ran for 'stopping_condition' number of seconds else it is ran for 'stopping_condition' number of iterations
    :param population: The initial population to start the GA from
    :param mutation_probability: The probability of mutating a chromosome (i.e change an operation's machine)
    :param selection_size: The size of the selection group for tournament style selection
    :param benchmark: If true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)
    :return: best_solution: The best Solution found
    """

    best_solution = min(population)
    iterations = 0

    # get static data
    dependency_matrix_index_encoding = Data.job_task_index_matrix
    usable_machines_matrix = Data.usable_machines_matrix

    # variables used for benchmarks
    best_makespans = []
    avg_population_makespan = [statistics.mean([sol.makespan for sol in population])]
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

        # tournament style selection
        selection_group = sorted([random.randrange(len(population)) for _ in range(selection_size)],
                                 key=lambda i: population[i].makespan)

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
                if stop_condition():
                    if benchmark:
                        return [best_solution, iterations, best_makespans, avg_population_makespan,
                                (best_solution_iteration, best_solution.makespan)]
                    else:
                        return best_solution

        # breed the parents to produce child2 (parent2 cross parent1)
        feasible_child = False
        while not feasible_child:
            try:
                child2 = crossover(parent2_operation_2d_array, parent1_operation_2d_array,
                                   mutation_probability, dependency_matrix_index_encoding, usable_machines_matrix)
                feasible_child = True
            except solution.InfeasibleSolutionException:
                if stop_condition():
                    if benchmark:
                        return [best_solution, iterations, best_makespans, avg_population_makespan,
                                (best_solution_iteration, best_solution.makespan)]
                    else:
                        return best_solution

        # replace worse solutions in selection with children
        population[selection_group[-1]] = child1
        population[selection_group[-2]] = child2

        # check for better solution than best_solution
        if min(child1, child2) < best_solution:
            best_solution = min(child1, child2)
            if benchmark:
                best_solution_iteration = iterations

        if benchmark:
            iterations += 1
            best_makespans.append(best_solution.makespan)
            avg_population_makespan.append(statistics.mean([sol.makespan for sol in population]))
        elif not time_condition:
            iterations += 1

    if benchmark:
        return [best_solution, iterations, best_makespans, avg_population_makespan,
                (best_solution_iteration, best_solution.makespan)]
    else:
        return best_solution
