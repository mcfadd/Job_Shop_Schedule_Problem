import multiprocessing as mp
import pickle
import time

from progressbar import Bar, ETA, ProgressBar, RotatingMarker

from . import benchmark_plotter
from . import genetic_algorithm
from . import tabu_search
from .solution import SolutionFactory, Solution


def _run_progress_bar(seconds):
    """
    Runs a progress bar for a certain duration.

    :type seconds: int
    :param seconds: duration to run the process bar for in seconds

    :returns: None
    """
    time.sleep(.5)
    widgets = [Bar(marker=RotatingMarker()), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        time.sleep(.98)
        pbar.update(i)
    pbar.finish()


class Solver:
    """
    The main solver class which calls tabu search and/or the genetic algorithm.

    :type data: Data
    :param data: JSSP instance data
    """

    def __init__(self, data):
        """
        Initializes an instance of Solver.
        """
        self.data = data
        self.solution = None
        self.ts_agent_list = None
        self.ga_agent = None
        self.solution_factory = SolutionFactory(data)

    def tabu_search_time(self, runtime, num_solutions_per_process=1, num_processes=4, tabu_list_size=50,
                         neighborhood_size=300, neighborhood_wait=0.1, probability_change_machine=0.8,
                         reset_threshold=100, initial_solutions=None, benchmark=False, verbose=False, progress_bar=False):
        """
        Performs parallel tabu search for a certain number of seconds.

        First the function generates random initial solutions if the initial_solutions parameter is None,
        then it forks/spawns num_processes of child processes to run tabu search in parallel.

        The parent process waits for the child processes to finish, then collects their results and updates self.solution.

        :type runtime: float
        :param runtime: seconds that tabu search should run for

        :type num_solutions_per_process: int
        :param num_solutions_per_process: number of solutions that one tabu search process should gather

        :type num_processes: int
        :param num_processes: number of processes to run tabu search in parallel

        :type tabu_list_size: int
        :param tabu_list_size: size of the tabu list

        :type neighborhood_size: int
        :param neighborhood_size: size of neighborhoods to generate during tabu search

        :type neighborhood_wait: float
        :param neighborhood_wait: maximum time to wait while generating a neighborhood in seconds

        :type probability_change_machine: float
        :param probability_change_machine: probability of changing a chosen operations machine, must be in range [0, 1]

        :type reset_threshold: int
        :param reset_threshold: number of iterations to potentially force a worse move after if the best solution is not improved

        :type initial_solutions: [Solution]
        :param initial_solutions: initial solutions to start the tabu searches from

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (e.g. # of iterations, makespans, etc.)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :type progress_bar: bool
        :param progress_bar: if true a progress bar is spawned

        :rtype: Solution
        :returns: best solution found
        """
        return self._tabu_search(runtime, time_condition=True, num_solutions_per_process=num_solutions_per_process,
                                 num_processes=num_processes, tabu_list_size=tabu_list_size,
                                 neighborhood_size=neighborhood_size, neighborhood_wait=neighborhood_wait,
                                 probability_change_machine=probability_change_machine,
                                 reset_threshold=reset_threshold, initial_solutions=initial_solutions,
                                 benchmark=benchmark, verbose=verbose, progress_bar=progress_bar)

    def tabu_search_iter(self, iterations, num_solutions_per_process=1, num_processes=4, tabu_list_size=50,
                         neighborhood_size=300, neighborhood_wait=0.1, probability_change_machine=0.8,
                         reset_threshold=100, initial_solutions=None, benchmark=False, verbose=False):
        """
        Performs parallel tabu search for a certain number of iterations.

        First the function generates random initial solutions if the initial_solutions parameter is None,
        then it forks a number of child processes to run tabu search.

        The parent process waits for the child processes to finish, then collects their results and updates self.solution.

        :type iterations: int
        :param iterations: number of iterations for each tabu search to go through

        :type num_solutions_per_process: int
        :param num_solutions_per_process: number of solutions that one tabu search process should gather

        :type num_processes: int
        :param num_processes: number of processes to run tabu search in parallel

        :type tabu_list_size: int
        :param tabu_list_size: size of the tabu list

        :type neighborhood_size: int
        :param neighborhood_size: size of neighborhoods to generate during tabu search

        :type neighborhood_wait: float
        :param neighborhood_wait: maximum time to wait while generating a neighborhood in seconds

        :type probability_change_machine: float
        :param probability_change_machine: probability of changing a chosen operations machine, must be in range [0, 1]

        :type reset_threshold: int
        :param reset_threshold: number of iterations to potentially force a worse move after if the best solution is not improved

        :type initial_solutions: [Solution]
        :param initial_solutions: initial solutions to start the tabu searches from

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (e.g. # of iterations, makespans, etc.)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :rtype: Solution
        :returns: best solution found
        """
        return self._tabu_search(iterations, time_condition=False, num_solutions_per_process=num_solutions_per_process,
                                 num_processes=num_processes, tabu_list_size=tabu_list_size,
                                 neighborhood_size=neighborhood_size, neighborhood_wait=neighborhood_wait,
                                 probability_change_machine=probability_change_machine,
                                 reset_threshold=reset_threshold, initial_solutions=initial_solutions,
                                 benchmark=benchmark, verbose=verbose, progress_bar=False)

    def _tabu_search(self, stopping_condition, time_condition, num_solutions_per_process, num_processes, tabu_list_size,
                     neighborhood_size, neighborhood_wait, probability_change_machine, reset_threshold,
                     initial_solutions, benchmark, verbose, progress_bar):
        """
        Performs parallel tabu search until the stopping condition is met.

        First the function generates random initial solutions if the initial_solutions parameter is None,
        then it forks a number of child processes to run tabu search.

        The parent process waits for the child processes to finish, then collects their results and updates self.solution.

        :type stopping_condition: float
        :param stopping_condition: either the duration in seconds or the number of iterations to search

        :type time_condition: bool
        :param time_condition: if true tabu search is ran for stopping_condition number of seconds else tabu search is ran for stopping_condition number of generations

        :type num_solutions_per_process: int
        :param num_solutions_per_process: number of solutions that one tabu search process should gather

        :type num_processes: int
        :param num_processes: number of processes to run tabu search in parallel

        :type tabu_list_size: int
        :param tabu_list_size: size of the tabu list

        :type neighborhood_size: int
        :param neighborhood_size: size of neighborhoods to generate during tabu search

        :type neighborhood_wait: float
        :param neighborhood_wait: maximum time to wait while generating a neighborhood in seconds

        :type probability_change_machine: float
        :param probability_change_machine: probability of changing a chosen operations machine, must be in range [0, 1]

        :type reset_threshold: int
        :param reset_threshold: number of iterations to potentially force a worse move after if the best solution is not improved

        :type initial_solutions: [Solution]
        :param initial_solutions: initial solutions to start the tabu searches from

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (e.g. # of iterations, makespans, etc.)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :type progress_bar: bool
        :param progress_bar: if true a progress bar is spawned

        :rtype: Solution
        :returns: best solution found
        """
        if initial_solutions is None:
            initial_solutions = [self.solution_factory.get_solution() for _ in range(num_processes)]
        else:
            initial_solutions += [self.solution_factory.get_solution() for _ in
                                  range(max(0, num_processes - len(initial_solutions)))]

        ts_agent_list = [tabu_search.TabuSearchAgent(stopping_condition,
                                                     time_condition,
                                                     initial_solution,
                                                     num_solutions_per_process,
                                                     tabu_list_size,
                                                     neighborhood_size,
                                                     neighborhood_wait,
                                                     probability_change_machine,
                                                     reset_threshold,
                                                     benchmark)
                         for initial_solution in initial_solutions
                         ]

        if verbose:
            if benchmark:
                print("Running benchmark of TS")
            else:
                print("Running TS")
            print("Parameters:")
            print(f"stopping_condition = {stopping_condition} {'seconds' if time_condition else 'iterations'}")
            print("time_condition =", time_condition)
            print("num_solutions_per_process =", num_solutions_per_process)
            print("num_processes =", num_processes)
            print("tabu_list_size =", tabu_list_size)
            print("neighborhood_size =", neighborhood_size)
            print("neighborhood_wait =", neighborhood_wait)
            print("probability_change_machine =", probability_change_machine)
            print("reset_threshold =", reset_threshold)
            print()
            print("Initial Solution's makespans:")
            print([round(x.makespan) for x in initial_solutions])
            print()

        # create child processes to run tabu search
        child_results_queue = mp.Queue()
        processes = [
            mp.Process(target=ts_agent.start, args=[child_results_queue])
            for ts_agent in ts_agent_list
        ]

        # start child processes
        for p in processes:
            p.start()
            if verbose:
                print(f"child TS process started. pid = {p.pid}")

        # start progress bar
        if progress_bar and time_condition:
            mp.Process(target=_run_progress_bar, args=[stopping_condition]).start()

        # collect results from Queue and wait for child processes to finish
        self.ts_agent_list = []
        for p in processes:
            self.ts_agent_list.append(pickle.loads(child_results_queue.get()))

            if verbose:
                print(f"child TS process finished. pid = {p.pid}")

        self.solution = min([ts_agent.best_solution for ts_agent in self.ts_agent_list])
        return self.solution

    def genetic_algorithm_time(self, runtime, population=None, population_size=200,
                               selection_method_enum=genetic_algorithm.GASelectionEnum.TOURNAMENT,
                               mutation_probability=0.8, selection_size=10, benchmark=False, verbose=False,
                               progress_bar=False):
        """
        Performs the genetic algorithm for a certain number of seconds.

        First this function generates a random initial population if the population parameter is None,
        then it runs GA with the parameters specified and updates self.solution.

        :type runtime: float
        :param runtime: seconds to run the GA

        :type population: [Solution]
        :param population: list of Solutions to start the GA from

        :type population_size: int
        :param population_size: size of the initial population

        :type selection_method_enum: GASelectionEnum
        :param selection_method_enum: selection method to use for selecting parents from the population. Options are GASelectionEnum.TOURNAMENT, GASelectionEnum.FITNESS_PROPORTIONATE, GASelectionEnum.RANDOM

        :type mutation_probability: float
        :param mutation_probability: probability of mutating a chromosome (i.e change an operation's machine), must be in range [0, 1]

        :type selection_size: int
        :param selection_size: size of the selection group for tournament style selection

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :type progress_bar: bool
        :param progress_bar: if true a progress bar is spawned

        :rtype: Solution
        :returns: best solution found
        """
        return self._genetic_algorithm(runtime, time_condition=True, population=population,
                                       population_size=population_size, selection_method_enum=selection_method_enum,
                                       mutation_probability=mutation_probability,
                                       selection_size=selection_size, benchmark=benchmark, verbose=verbose,
                                       progress_bar=progress_bar)

    def genetic_algorithm_iter(self, iterations, population=None, population_size=200,
                               selection_method_enum=genetic_algorithm.GASelectionEnum.TOURNAMENT,
                               mutation_probability=0.8,
                               selection_size=10, benchmark=False, verbose=False):
        """
        Performs the genetic algorithm for a certain number of generations.

        First this function generates a random initial population if the population parameter is None,
        then it runs GA with the parameters specified and updates self.solution.

        :type iterations: int
        :param iterations: number of generations to go through during the GA

        :type population: [Solution]
        :param population: list of Solutions to start the GA from

        :type population_size: int
        :param population_size: size of the initial population

        :type selection_method_enum: GASelectionEnum
        :param selection_method_enum: selection method to use for selecting parents from the population. Options are GASelectionEnum.TOURNAMENT, GASelectionEnum.FITNESS_PROPORTIONATE, GASelectionEnum.RANDOM

        :type mutation_probability: float
        :param mutation_probability: probability of mutating a chromosome (i.e change an operation's machine), must be in range [0, 1]

        :type selection_size: int
        :param selection_size: size of the selection group for tournament style selection

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :rtype: Solution
        :returns: best solution found
        """
        return self._genetic_algorithm(iterations, time_condition=False, population=population,
                                       population_size=population_size, selection_method_enum=selection_method_enum,
                                       mutation_probability=mutation_probability,
                                       selection_size=selection_size, benchmark=benchmark, verbose=verbose,
                                       progress_bar=False)

    def _genetic_algorithm(self, stopping_condition, time_condition, population=None, population_size=200,
                           selection_method_enum=genetic_algorithm.GASelectionEnum.TOURNAMENT, mutation_probability=0.8,
                           selection_size=5, benchmark=False, verbose=False, progress_bar=False):
        """
        Performs the genetic algorithm until the stopping condition is met.

        First this function generates a random initial population if the population parameter is None,
        then it runs GA with the parameters specified and updates self.solution.

        :type stopping_condition: float
        :param stopping_condition: either the duration in seconds or the number of generations to iterate through

        :type time_condition: bool
        :param time_condition: if true GA is ran for stopping_condition number of seconds else GA is ran for stopping_condition number of iterations

        :type population: [Solution]
        :param population: list of Solutions to start the GA from

        :type population_size: int
        :param population_size: size of the initial population

        :type selection_method_enum: GASelectionEnum
        :param selection_method_enum: selection method to use for selecting parents from the population. Options are GASelectionEnum.TOURNAMENT, GASelectionEnum.FITNESS_PROPORTIONATE, GASelectionEnum.RANDOM

        :type mutation_probability: float
        :param mutation_probability: probability of mutating a chromosome (i.e change an operation's machine), must be in range [0, 1]

        :type selection_size: int
        :param selection_size: size of the selection group for tournament style selection

        :type benchmark: bool
        :param benchmark: if true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)

        :type verbose: bool
        :param verbose: if true runs in verbose mode

        :type progress_bar: bool
        :param progress_bar: if true a progress bar is spawned

        :rtype: Solution
        :returns: best solution found
        """
        if population is None:
            population = [self.solution_factory.get_solution() for _ in range(population_size)]
        else:
            population = population[:] + [self.solution_factory.get_solution() for _ in range(max(0, population_size - len(population)))]

        self.ga_agent = genetic_algorithm.GeneticAlgorithmAgent(stopping_condition,
                                                                population,
                                                                time_condition,
                                                                selection_method_enum,
                                                                mutation_probability,
                                                                selection_size,
                                                                benchmark
                                                                )

        if verbose:
            if benchmark:
                print("Running benchmark of GA")
            else:
                print("Running GA")
            print("Parameters:")
            print(f"stopping_condition = {stopping_condition} {'seconds' if time_condition else 'iterations'}")
            print("time_condition =", time_condition)
            print("population_size =", population_size)
            print("selection_method =", selection_method_enum.__name__)
            print("mutation_probability =", mutation_probability)
            if selection_method_enum is genetic_algorithm.GASelectionEnum.TOURNAMENT:
                print("selection_size =", selection_size)

        if progress_bar and time_condition:
            mp.Process(target=_run_progress_bar, args=[stopping_condition]).start()

        self.solution = self.ga_agent.start()
        return self.solution

    def output_benchmark_results(self, output_dir, name=None, auto_open=True):
        """
        Outputs html files containing benchmark results in the output directory specified.

        :type output_dir: Path | str
        :param output_dir: path to the output directory to place the results into

        :type name: str
        :param name: name of the benchmark run

        :type auto_open: bool
        :param auto_open: if true index.html is automatically opened in a browser

        :returns: None
        """
        benchmark_plotter.output_benchmark_results(output_dir, ts_agent_list=self.ts_agent_list, ga_agent=self.ga_agent,
                                                   title=name, auto_open=auto_open)

    def iplot_benchmark_results(self):
        """
        Plots the benchmark results in an ipython notebook.

        :returns: None
        """
        benchmark_plotter.iplot_benchmark_results(ts_agent_list=self.ts_agent_list, ga_agent=self.ga_agent)
