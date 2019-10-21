import random
import statistics
import time
from enum import Enum

from JSSP.data import Data
from JSSP.solution import Solution, SolutionFactory, InfeasibleSolutionException
from ._ga_helpers import crossover

"""
GA selection functions
"""


def _tournament_selection(*args):
    """
    Tournament style selection for the genetic algorithm.

    This function selects args[1] (i.e. selection_size) solutions from the population,
    then removes the best solution out of the selection from the population and returns it.

    See https://en.wikipedia.org/wiki/Tournament_selection for more info.

    :param args: list where args[0] is the population of solutions and args[1] is the selection size

    :rtype: Solution
    :returns: a Solution from the population
    """
    selection_indices = random.sample(range(len(args[0])), args[1])
    selection_group = sorted([index for index in selection_indices],
                             key=lambda index: args[0][index].makespan)

    parent = args[0].pop(selection_group[0])
    return parent


def _fitness_proportionate_selection(*args):
    """
    Fitness proportionate selection for the genetic algorithm (also called roulette wheel selection).

    This function first normalizes the fitness values (makespan) of the solutions in the population,
    then randomly removes a solution from the population and returns it.

    See https://en.wikipedia.org/wiki/Fitness_proportionate_selection for more info.

    :param args: list where args[0] is the population

    :rtype: Solution
    :returns: a Solution from the population
    """
    fitness_sum = 0
    for sol in args[0]:
        fitness_sum += sol.makespan

    s = random.uniform(0, fitness_sum)
    partial_sum = 0
    for sol in args[0]:
        partial_sum += sol.makespan
        if partial_sum > s:
            args[0].remove(sol)
            return sol


def _random_selection(*args):
    """
    Random selection for the genetic algorithm.

    This function randomly removes a solution from the population and returns it.

    :param args: list where args[0] is the population

    :rtype: Solution
    :returns: a solution from the population
    """
    return args[0].pop(random.randrange(0, len(args[0])))


class GASelectionEnum(Enum):
    """
    Enumeration class containing three selection methods for selecting parent solutions for the genetic algorithm.

    Selection Methods:
        1. GASelectionEnum.TOURNAMENT - Tournament style selection
        2. GASelectionEnum. FITNESS_PROPORTIONATE - Fitness proportionate selection (also called roulette wheel selection)
        3. GASelectionEnum.RANDOM - Random selection
    """
    TOURNAMENT = _tournament_selection
    FITNESS_PROPORTIONATE = _fitness_proportionate_selection
    RANDOM = _random_selection


"""
GA agent class
"""


class GeneticAlgorithmAgent:
    """
    Genetic algorithm optimization agent.

    :type stopping_condition: float
    :param stopping_condition: either the duration to run GA in seconds or the number of generations to iterate though

    :type population: [Solution]
    :param population: list of Solutions to start the GA from

    :type time_condition: bool
    :param time_condition: if true GA is ran for stopping_condition number of seconds else it is ran for stopping_condition generations

    :type selection_method_enum: GASelectionEnum
    :param selection_method_enum: selection method to use for selecting parents from the population. (see GASelectionEnum for selection methods)

    :type mutation_probability: float
    :param mutation_probability: probability of mutating a child solution (i.e change a random operation's machine)

    :type selection_size: int
    :param selection_size: size of the selection group. (applicable only for tournament style selection)

    :type benchmark: bool
    :param benchmark: if true benchmark data is gathered
    """

    def __init__(self, stopping_condition, population, time_condition=False,
                 selection_method_enum=GASelectionEnum.TOURNAMENT, mutation_probability=0.8,
                 selection_size=5, benchmark=False):
        """
        Initializes an instance of GeneticAlgorithmAgent.

        See help(GeneticAlgorithmAgent)
        """
        assert selection_method_enum in [GASelectionEnum.TOURNAMENT, GASelectionEnum.FITNESS_PROPORTIONATE, GASelectionEnum.RANDOM], "selection_method must be a GASelectionEnum"
        assert selection_size is not None and 1 < selection_size, "selection_size must be an integer greater than 1"
        assert population is not None and isinstance(population, list) and all(isinstance(x, Solution) for x in population), "population must be a list of solutions"

        # parameters
        self.time_condition = time_condition
        if time_condition:
            self.runtime = stopping_condition
        else:
            self.iterations = stopping_condition

        self.initial_population = population
        self.population_size = len(population)
        self.selection_method = selection_method_enum
        self.mutation_probability = mutation_probability
        self.selection_size = selection_size
        self.benchmark = benchmark

        # results
        self.result_population = []
        self.best_solution = None

        if benchmark:
            self.benchmark_iterations = 0
            self.best_solution_makespan_v_iter = []
            self.avg_population_makespan_v_iter = []
            self.min_makespan_coordinates = []

    def start(self):
        """
        Starts the genetic algorithm for this GeneticAlgorithmAgent.

        :rtype: Solution
        :returns: best Solution found
        """

        population = self.initial_population[:]
        best_solution = min(population)
        iterations = 0

        # get static data
        dependency_matrix_index_encoding = Data.job_task_index_matrix
        usable_machines_matrix = Data.usable_machines_matrix

        # variables used for benchmarks
        best_solution_makespan_v_iter = []
        avg_population_makespan_v_iter = []
        best_solution_iteration = 0

        # create stopping condition function
        if self.time_condition:
            stop_time = time.time() + self.runtime

            def stop_condition():
                return time.time() >= stop_time
        else:
            stop_iter = self.iterations

            def stop_condition():
                return iterations >= stop_iter

        not_done = True
        while not stop_condition():
            if self.benchmark:
                avg_population_makespan_v_iter.append(statistics.mean([sol.makespan for sol in population]))

            next_population = []
            while len(population) > self.selection_size and not_done:

                parent1 = self.selection_method(population, self.selection_size)
                parent2 = self.selection_method(population, self.selection_size)

                # breed the parents to produce child1 (parent1 cross parent2)
                # Note mutation happens in crossover function
                feasible_child = False
                while not feasible_child:
                    # the try except block is because sometimes the crossover operation results in a setup of -1
                    # which then produces an infeasible solution. This is due to the sequence dependency setup times matrix not allowing for wait time.
                    try:
                        child1 = crossover(parent1.operation_2d_array, parent2.operation_2d_array,
                                           self.mutation_probability, dependency_matrix_index_encoding,
                                           usable_machines_matrix)
                        if child1 != parent1 and child1 != parent2:
                            feasible_child = True
                    except InfeasibleSolutionException:
                        if stop_condition():
                            not_done = False
                            break

                # breed the parents to produce child2 (parent2 cross parent1)
                feasible_child = False
                while not feasible_child:
                    try:
                        child2 = crossover(parent2.operation_2d_array, parent1.operation_2d_array,
                                           self.mutation_probability, dependency_matrix_index_encoding,
                                           usable_machines_matrix)
                        if child2 != parent1 and child2 != parent2:
                            feasible_child = True
                    except InfeasibleSolutionException:
                        if stop_condition():
                            not_done = False
                            break

                # add best 2 individuals to next generation if they are not already in the next generation (elitist strategy)
                if not_done:
                    sorted_individuals = sorted([parent1, parent2, child1, child2])
                    added = 0
                    index = 0
                    while added < 2 and index < len(sorted_individuals):
                        if sorted_individuals[index] not in next_population:
                            next_population.append(sorted_individuals[index])
                            added += 1
                        index += 1

                    # if parent1, parent2, child1, and child2 are all in next_population, add random solutions
                    while added < 2:
                        next_population.append(SolutionFactory.get_solution())
                        added += 1
                else:
                    next_population.append(parent1)
                    next_population.append(parent2)

                # check for better solution than best_solution
                if min(child1, child2) < best_solution:
                    best_solution = min(child1, child2)
                    if self.benchmark:
                        best_solution_iteration = iterations

            if self.benchmark:
                best_solution_makespan_v_iter.append(best_solution.makespan)
                iterations += 1
            elif not self.time_condition:
                iterations += 1

            next_population += population
            population = next_population

        self.best_solution = best_solution
        self.result_population = next_population

        if self.benchmark:
            self.benchmark_iterations = iterations
            self.best_solution_makespan_v_iter = best_solution_makespan_v_iter
            self.avg_population_makespan_v_iter = avg_population_makespan_v_iter
            self.min_makespan_coordinates = (best_solution_iteration, best_solution.makespan)

        return self.best_solution
