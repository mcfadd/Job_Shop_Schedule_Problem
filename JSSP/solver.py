import datetime
import multiprocessing as mp
import os
import pickle
import shutil
import statistics
import time
import webbrowser

import plotly.graph_objs as go
from plotly.offline import plot
from progressbar import Bar, ETA, ProgressBar, RotatingMarker

from JSSP import genetic_algorithm
from JSSP import solution
from JSSP import tabu_search


def run_progress_bar(seconds):
    """
    Runs a progress bar for a certain duration.

    :param seconds: Duration to run the process bar for in seconds
    :return: None
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
    The main solver class which calls tabu search and/or the genetic algorithm
    """
    def __init__(self):

        # uninitialized ts results
        self.ts_all_solutions = []
        self.ts_best_solution = None

        # uninitialized ts parameters
        self.ts_parameters = {
            'runtime': None,
            'processes': None,
            'tabu list size': None,
            'neighborhood size': None,
            'neighborhood wait': None,
            'probability change_machine': None,
            'reset threshold': None,
            'initial solutions': [],
        }

        # uninitialized ts benchmark results
        self.ts_benchmark = False
        self.ts_iterations = []
        self.ts_nh_sizes = []
        self.ts_makespans = []
        self.ts_tabu_sizes = []
        self.ts_min_makespan_coordinates = []

        # uninitialized ga results
        self.ga_result_population = []
        self.ga_best_solution = None

        # uninitialized ga parameters
        self.ga_parameters = {
            'runtime': None,
            'mutation probability': None,
            'selection size': None,
            'population size': None,
            'population': [],
        }

        # uninitialized ga benchmark results
        self.ga_benchmark = False
        self.ga_iterations = None
        self.ga_best_makespans = []
        self.ga_avg_population_makespans = []
        self.ga_min_makespan_coordinates = []

    def tabu_search(self, runtime, num_processes=4, tabu_list_size=50, neighborhood_size=300,
                    neighborhood_wait=0.1, probability_change_machine=0.8, reset_threshold=100, initial_solutions=None,
                    benchmark=False, verbose=False, progress_bar=False):
        """
        This function performs tabu search for a given duration starting with an initial solution.

        First this function generates random initial solutions if initial_solutions is None,
        then it forks a number_processes child processes to run tabu search.

        The parent process waits for the child processes to finish, then collects their results from a temporary directory.

        :param runtime: The duration that tabu search will run in seconds
        :param num_processes: The number of processes to run tabu search
        :param tabu_list_size: The size of the tabu list
        :param neighborhood_size: The size of neighborhoods to generate during tabu search
        :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds
        :param probability_change_machine: The probability of changing a chosen operations machine
        :param reset_threshold: The number of iteration to potentially force a worse move after if the best solution is not improved
        :param initial_solutions: The initial solutions to start the tabu searches from
        :param benchmark: If true benchmark data is gathered (e.g. # of iterations, makespans, etc.)
        :param verbose: If true runs in verbose mode
        :param progress_bar: If true a progress bar is spawned
        :return:
        """
        # initial solution to start TS from if not None
        if initial_solutions is not None and not (
                len(initial_solutions) == 0 or all(isinstance(s, solution.Solution) for s in initial_solutions)):
            raise TypeError("initial_solutions must be a list of solutions")

        tmp_dir = f"{os.path.dirname(os.path.realpath(__file__))}/tabu_search/tmp"

        self.ts_benchmark = benchmark
        self.ts_parameters = {
            'runtime': runtime,
            'processes': num_processes,
            'tabu list size': tabu_list_size,
            'neighborhood size': neighborhood_size,
            'neighborhood wait': neighborhood_wait,
            'probability change_machine': probability_change_machine,
            'reset threshold': reset_threshold,
            'initial solutions': [solution.generate_feasible_solution() for _ in range(num_processes)]
            if initial_solutions is None else
            initial_solutions + [solution.generate_feasible_solution()
                                 for _ in range(max(0, num_processes - len(initial_solutions)))],
        }

        if progress_bar:
            mp.Process(target=run_progress_bar, args=[runtime]).start()

        parent_process_id = os.getpid()

        # remove temporary directory if it exists
        shutil.rmtree(tmp_dir, ignore_errors=True)

        # create temporary directory for storing results
        os.mkdir(tmp_dir)

        if verbose:
            print("Initial Solution's makespans:")
            print([round(x.makespan) for x in self.ts_parameters['initial solutions']])
            print()

        # create child processes to run tabu search
        processes = []
        for tabu_id, initial_solution in enumerate(self.ts_parameters['initial solutions']):
            processes.append(mp.Process(target=tabu_search.search, args=[tabu_id,
                                                                         initial_solution,
                                                                         runtime,
                                                                         tabu_list_size,
                                                                         neighborhood_size,
                                                                         neighborhood_wait,
                                                                         probability_change_machine,
                                                                         reset_threshold,
                                                                         benchmark]))

        # start child processes
        for p in processes:
            if parent_process_id == os.getpid():
                p.start()
                if verbose:
                    print(f"child TS process started. pid = {p.pid}")

        # wait for child processes to finish
        if parent_process_id == os.getpid():
            for p in processes:
                p.join()
                if verbose:
                    print(f"child TS process finished. pid = {p.pid}")

        if verbose:
            print("collecting results from tmp directory")

        # get the results from the tmp directory
        for tabu_id in range(num_processes):
            with open(tmp_dir + f'/solution{tabu_id}', 'rb') as file:
                if benchmark:
                    results = pickle.load(file)
                    self.ts_all_solutions.append(results[0])
                    self.ts_iterations.append(results[1])
                    self.ts_nh_sizes.append(results[2])
                    self.ts_makespans.append(results[3])
                    self.ts_tabu_sizes.append(results[4])
                    self.ts_min_makespan_coordinates.append(results[5])
                else:
                    self.ts_all_solutions.append(pickle.load(file))

        # remove temporary directory
        shutil.rmtree(tmp_dir)

        self.ts_best_solution = min(self.ts_all_solutions)
        return self.ts_best_solution

    def genetic_algorithm(self, runtime, population=None, population_size=200, mutation_probability=0.8,
                          selection_size=10, benchmark=False, progress_bar=False):
        """
        This function performs a Genetic Algorithm for a given duration starting with an initial population.

        First this function generates a random initial population if population is None, then it runs GA with the parameters specified.

        :param runtime: The duration that the genetic algorithm will run in seconds
        :param population: The initial population to start the GA from
        :param population_size: The size of the initial population
        :param mutation_probability: The probability of mutating a chromosome (i.e change an operation's machine)
        :param selection_size: The size of the selection group for tournament style selection
        :param benchmark: If true benchmark data is gathered (i.e. # of iterations, makespans, min makespan iteration)
        :param progress_bar: If true a progress bar is spawned
        :return:
        """

        self.ga_benchmark = benchmark
        self.ga_parameters = {
            'runtime': runtime,
            'mutation probability': mutation_probability,
            'selection size': selection_size,
            'population size': population_size,
            'population': [solution.generate_feasible_solution() for _ in
                           range(population_size)] if population is None else population + [
                solution.generate_feasible_solution() for _ in range(max(0, population_size - len(population)))],
        }

        if progress_bar:
            mp.Process(target=run_progress_bar, args=[runtime]).start()

        self.ga_result_population = self.ga_parameters['population'].copy()
        results = genetic_algorithm.search(runtime, self.ga_result_population, mutation_probability, selection_size,
                                           benchmark)

        if benchmark:
            self.ga_best_solution = results[0]
            self.ga_iterations = results[1]
            self.ga_best_makespans = results[2]
            self.ga_avg_population_makespans = results[3]
            self.ga_min_makespan_coordinates = results[4]
        else:
            self.ga_best_solution = results

        return self.ga_best_solution

    def output_benchmark_results(self, output_dir, name=None, auto_open=True):
        """
        This function outputs html files containing benchmark results in the output directory specified.

        :param output_dir: The output directory to place the results into
        :param name: The name of the benchmark run. defaults to current datetime
        :param auto_open: If true index.html is automatically opened in a browser
        :return: None
        """
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if name is None:
            name = "benchmark_run_{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))

        # output results
        output_directory = os.path.abspath(output_dir + "/" + name)

        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        index_text = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                        <html>
                            <head>
                                <meta content="text/html; charset=ISO-8859-1"
                                    http-equiv="content-type">
                                <title>{name}</title>
                            </head>
                            <body>
                                <h2>{name}</h2>
                                {self._ts_benchmark_results(output_directory) if self.ts_benchmark else ''}
                                {self._ga_benchmark_results(output_directory) if self.ga_benchmark else ''}
                            </body>
                        </html>
                        '''

        # create index.html
        with open(output_directory + '/index.html', 'w') as output_file:
            output_file.write(index_text)

        if auto_open:
            print(f'opening file://{output_directory} in browser')
            webbrowser.open(f'file://{output_directory}/index.html')

    def _ts_benchmark_results(self, output_directory):
        """
        Formats TS benchmark results & plots in html.

        used by Solver.output_benchmark_results

        :param output_directory: The directory to place the html files containing plots
        :return: html containing benchmark results
        """
        best_makespans_per_ts = [p[1] for p in self.ts_min_makespan_coordinates]
        html = f'''
            <h3>Tabu Search</h3>
            <b>Parameters:</b>
            <br>
            runtime = {self.ts_parameters['runtime']} seconds<br>
            number of processes = {self.ts_parameters['processes']}<br>
            tabu list size = {self.ts_parameters['tabu list size']}<br>
            neighborhood size = {self.ts_parameters['neighborhood size']}<br>
            neighborhood wait = {self.ts_parameters['neighborhood wait']} seconds<br>
            probability of changing an operation's machine = {self.ts_parameters['probability change_machine']}<br>
            reset threshold = {self.ts_parameters['reset threshold']} seconds<br>
            best initial makespan = {round(min(self.ts_parameters['initial solutions']).makespan)}<br>
            <br>
            <b>Results:</b>
            <br>
            makespans:
            <br>
            min = {round(min(best_makespans_per_ts))}<br>
            median = {round(statistics.median(best_makespans_per_ts))}<br>
            max = {round(max(best_makespans_per_ts))}<br>
            stdev = {round(statistics.stdev(best_makespans_per_ts)) if len(best_makespans_per_ts) > 1 else 0}<br>
            var = {round(statistics.variance(best_makespans_per_ts)) if len(best_makespans_per_ts) > 1 else 0}<br>
            mean = {round(statistics.mean(best_makespans_per_ts))}<br>
            <br>
            iterations:
            <br>
            min = {min(self.ts_iterations)}<br>
            median = {statistics.median(self.ts_iterations)}<br>
            max = {max(self.ts_iterations)}<br>
            stdev = {statistics.stdev(self.ts_iterations) if len(self.ts_iterations) > 1 else 0}<br>
            var = {statistics.variance(self.ts_iterations) if len(self.ts_iterations) > 1 else 0}<br>
            mean = {statistics.mean(self.ts_iterations)}<br>
            <br>
            <b>Plots:</b>
            <br>
            <a href="./ts_makespans.html">Makespan vs Iteration</a><br>
            <a href="./neighborhood_sizes.html">Neighborhood Size vs Iteration</a><br>
            <a href="./tabu_list_sizes.html">Tabu Size vs Iteration</a><br>
            <b>Schedule:</b>
            <br>
            <a href="file://{output_directory}/ts_schedule.xlsx">ts_schedule.xlsx</a>
            <br>
            '''

        # create traces for plots
        makespans_traces = [
            go.Scatter(x=[p[0] for p in self.ts_min_makespan_coordinates], y=best_makespans_per_ts, mode='markers',
                       name='best makespans')
        ]

        neighborhood_sizes_traces = []
        tabu_list_sizes_traces = []

        for i in range(len(self.ts_iterations)):
            x_axis = list(range(self.ts_iterations[i]))
            makespans_traces.append(go.Scatter(x=x_axis, y=self.ts_makespans[i], name=f'TS trace {i}'))
            neighborhood_sizes_traces.append(go.Scatter(x=x_axis, y=self.ts_nh_sizes[i], name=f'TS trace {i}'))
            tabu_list_sizes_traces.append(go.Scatter(x=x_axis, y=self.ts_tabu_sizes[i], name=f'TS trace {i}'))

        # create layouts for plots
        makespans_layout = dict(title='Makespans vs Iterations',
                                xaxis=dict(title='Iteration'),
                                yaxis=dict(title='Makespans (minutes)'))
        nh_sizes_layout = dict(title='Neighborhood sizes vs Iterations',
                               xaxis=dict(title='Iteration'),
                               yaxis=dict(title='Size of Neighborhood'))
        tl_sizes_layout = dict(title='Tabu list sizes vs Iterations',
                               xaxis=dict(title='Iteration'),
                               yaxis=dict(title='Size of Tabu list'))

        # create plots
        plot(dict(data=makespans_traces, layout=makespans_layout),
             filename=output_directory + '/ts_makespans.html',
             auto_open=False)
        plot(dict(data=neighborhood_sizes_traces, layout=nh_sizes_layout),
             filename=output_directory + '/neighborhood_sizes.html',
             auto_open=False)
        plot(dict(data=tabu_list_sizes_traces, layout=tl_sizes_layout),
             filename=output_directory + '/tabu_list_sizes.html',
             auto_open=False)

        # create schedule
        self.ts_best_solution.create_schedule(output_directory, filename='ts_schedule')

        return html

    def _ga_benchmark_results(self, output_directory):
        """
        Formats GA benchmark results & plots in html.

        used by Solver.output_benchmark_results

        :param output_directory: The directory to place the html files containing plots
        :return: html containing benchmark results
        """
        initial_population_makespans = [sol.makespan for sol in self.ga_parameters['population']]
        result_population_makespans = [sol.makespan for sol in self.ga_result_population]
        html = f'''
            <h3>Genetic Algorithm</h3>
            <b>Parameters:</b>
            <br>
            runtime = {self.ga_parameters['runtime']} seconds<br>
            population size = {self.ga_parameters['population size']}<br>
            selection size = {self.ga_parameters['selection size']}<br>
            mutation probability = {self.ga_parameters['mutation probability']}<br>
            <br>
            <b>Initial Population:</b>
            <br>
            min = {round(min(initial_population_makespans))}<br>
            median = {round(statistics.median(initial_population_makespans))}<br>
            max = {round(max(initial_population_makespans))}<br>
            stdev = {round(statistics.stdev(initial_population_makespans)) if len(
            initial_population_makespans) > 1 else 0}<br>
            var = {round(statistics.variance(initial_population_makespans)) if len(
            initial_population_makespans) > 1 else 0}<br>
            mean = {round(statistics.mean(initial_population_makespans))}<br>
            <br>
            <b>Final Population:</b>
            <br>
            min = {round(min(result_population_makespans))}<br>
            median = {round(statistics.median(result_population_makespans))}<br>
            max = {round(max(result_population_makespans))}<br>
            stdev = {round(statistics.stdev(result_population_makespans)) if len(
            result_population_makespans) > 1 else 0}<br>
            var = {round(statistics.variance(result_population_makespans)) if len(
            result_population_makespans) > 1 else 0}<br>
            mean = {round(statistics.mean(result_population_makespans))}<br>
            <br>
            <b>Plots:</b>
            <br>
            <a href="./ga_makespans.html">Makespan vs Iteration</a><br>
            <b>Schedule:</b>
            <br>
            <a href="file://{output_directory}/ga_schedule.xlsx">ga_schedule.xlsx</a>
            <br>
            '''

        # create traces for plot
        makespans_traces = [
            go.Scatter(x=[self.ga_min_makespan_coordinates[0]], y=[self.ga_min_makespan_coordinates[1]], mode='markers',
                       name='best makespan'),
            go.Scatter(x=list(range(self.ga_iterations)), y=self.ga_best_makespans, name='Best makespan trace'),
            go.Scatter(x=list(range(self.ga_iterations)), y=self.ga_avg_population_makespans, name='Avg population makespan')
        ]

        # create layouts for plot
        makespans_layout = dict(title='Makespans vs Iterations',
                                xaxis=dict(title='Iteration'),
                                yaxis=dict(title='Makespans (minutes)'))

        # create plot
        plot(dict(data=makespans_traces, layout=makespans_layout),
             filename=output_directory + '/ga_makespans.html',
             auto_open=False)

        # create schedule
        self.ga_best_solution.create_schedule(output_directory, filename='ga_schedule')

        return html
