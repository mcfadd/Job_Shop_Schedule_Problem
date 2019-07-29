#!/usr/bin/env python

import os

from JSSP.data import Data
from JSSP.solver import Solver
from JSSP.genetic_algorithm import GASelectionEnum
from JSSP.solution import SolutionFactory

# test given data
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'benchmark_output'

# ts parameters
ts_iterations = 250
num_solutions_per_process = 12
num_processes = 10
tabu_list_size = 15
neighborhood_size = 300
neighborhood_wait = 0.1
probability_change_machine = 0.8
reset_threshold = 100

# ga parameters
ga_iterations = 250
population_size = 500
selection_method = GASelectionEnum.FITNESS_PROPORTIONATE
mutation_probability = 0.5
selection_size = 10

# # TS parameters
# ts_iterations = 360
# num_processes = 10
# num_solutions_per_process = 10
# tabu_list_size = 15
# neighborhood_size = 300
# neighborhood_wait = 0.2
# probability_change_machine = 0.8
# reset_threshold = 100
#
# # GA parameters
# ga_iterations = 240
# population_size = 400
# selection_method = GASelectionEnum.FITNESS_PROPORTIONATE
# selection_size = 5
# mutation_probability = 0.1


def benchmark_run_with_given_data():
    data_directory = project_root + os.sep + 'data' + os.sep + 'given_data'
    Data.initialize_data_from_csv(data_directory + os.sep + 'sequenceDependencyMatrix.csv',
                                  data_directory + os.sep + 'machineRunSpeed.csv',
                                  data_directory + os.sep + 'jobTasks.csv')

    # run tabu search
    solver = Solver()
    solver.tabu_search_iter(ts_iterations,
                            num_solutions_per_process=num_solutions_per_process,
                            num_processes=num_processes,
                            tabu_list_size=tabu_list_size,
                            neighborhood_size=neighborhood_size,
                            neighborhood_wait=neighborhood_wait,
                            probability_change_machine=probability_change_machine,
                            reset_threshold=reset_threshold,
                            verbose=True,
                            benchmark=True,
                            progress_bar=True
                            )

    # add all ts solutions to population
    population = []
    for ts_agent in solver.ts_agent_list:
        population += ts_agent.all_solutions

    solver.genetic_algorithm_iter(ga_iterations,
                                  population=population,
                                  population_size=population_size,
                                  selection_method_enum=selection_method,
                                  mutation_probability=mutation_probability,
                                  selection_size=selection_size,
                                  verbose=True,
                                  benchmark=True,
                                  progress_bar=True
                                  )

    solver.output_benchmark_results(output_dir)


def benchmark_run_with_fjs_data():
    data_directory = project_root + os.sep + 'data' + os.sep + 'fjs_data'
    Data.initialize_data_from_fjs(data_directory + os.sep + 'Brandimarte' + os.sep + 'Brandimarte_Mk10.fjs')

    # run tabu search
    solver = Solver()
    solver.tabu_search_iter(ts_iterations,
                            num_solutions_per_process=num_solutions_per_process,
                            num_processes=num_processes,
                            tabu_list_size=tabu_list_size,
                            neighborhood_size=neighborhood_size,
                            neighborhood_wait=neighborhood_wait,
                            probability_change_machine=probability_change_machine,
                            verbose=True,
                            benchmark=True
                            )

    # add all ts solutions to population
    population = []
    for ts_agent in solver.ts_agent_list:
        population += ts_agent.all_solutions

    # add 25% spt solutions to population
    population += SolutionFactory.get_n_shortest_process_time_first_solution(int(.25 * population_size))

    # add 25% lpt solutions to population
    population += SolutionFactory.get_n_longest_process_time_first_solution(int(.25 * population_size))

    # add 25% random solutions to population
    population += SolutionFactory.get_n_solutions(int(.25 * population_size))

    solver.genetic_algorithm_iter(ga_iterations,
                                  population=population,
                                  population_size=population_size,
                                  selection_method_enum=selection_method,
                                  mutation_probability=mutation_probability,
                                  selection_size=selection_size,
                                  verbose=True,
                                  benchmark=True
                                  )

    solver.output_benchmark_results(output_dir)


if __name__ == '__main__':
    benchmark_run_with_given_data()
    # benchmark_run_with_fjs_data()
