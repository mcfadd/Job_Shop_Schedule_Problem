import datetime
import multiprocessing as mp
import pickle
import shutil
import statistics
import webbrowser
import os

import plotly.graph_objs as go
from plotly.offline import plot

from JSSP.pbar import run_progress_bar
from JSSP.solution import generate_feasible_solution
from .ts import search


class TabuSearchManager:
    def __init__(self, runtime, num_processes=4, tabu_list_size=50, neighborhood_size=300,
                 neighborhood_wait=0.1, probability_change_machine=0.8, initial_solution=None):
        """
        This class starts, then collects the results from the tabu_search search processes.
        The processes are started with the arguments in arguments_namespace when self.start() is called.

        :param runtime: The duration that Tabu search will run in seconds.
        :param num_processes: The number of Tabu search processes to run in parallel.
        :param tabu_list_size: The size of the Tabu list.
        :param neighborhood_size: The size of neighborhoods to generate during Tabu search.
        :param neighborhood_wait: The maximum time to wait for generating a neighborhood in seconds.
        :param probability_change_machine: The probability of changing a chosen operations machine.
        :param initial_solution: The initial solution to start the Tabu searches from (defaults to generating random solutions).
        """

        # get required arguments for tabu_search search
        self.runtime = runtime
        self.num_processes = num_processes
        self.tabu_list_size = tabu_list_size
        self.neighborhood_size = neighborhood_size
        self.neighborhood_wait = neighborhood_wait
        self.probability_change_machine = probability_change_machine

        # initial solution to start TS from if not None
        self.initial_solution = initial_solution
        self.initial_solutions = []

        # uninitialized results
        self.all_solutions = []
        self.best_solution = None

        # benchmark specific arguments and results
        self.benchmark_makespans = []
        self.benchmark_iterations = []
        self.benchmark_neighborhood_sizes = []
        self.benchmark_tabu_list_sizes = []
        self.benchmark_min_makespan_coorinates = []

    def start(self, benchmark=False, verbose=False, progress_bar=False):
        """
        This function first generates random initial solutions if an initial solution is not given,
        then it forks a number of child processes equal to self.number_processes that run tabu_search search with the fields of this TabuSearchManager.
        The parent process waits for the children to finish, then collects their pickled results from a temporary directory.

        :param benchmark: If True benchmark data is collected while performing tabu search
        :param verbose: It True extra information is printed
        :param progress_bar: If True, a progress bar is spawned
        :return: None
        """

        if progress_bar:
            mp.Process(target=run_progress_bar, args=[self.runtime]).start()

        parent_process_id = os.getpid()

        # remove temporary directory if it exists
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp", ignore_errors=True)

        # create temporary directory for storing results
        os.mkdir(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")

        if self.initial_solution is not None:
            self.initial_solutions = [self.initial_solution] * self.num_processes
        else:
            # generate random initial solutions
            for _ in range(self.num_processes):
                self.initial_solutions.append(generate_feasible_solution())

        if verbose:
            print("Initial Solution's makespans:")
            print([round(x.makespan) for x in self.initial_solutions])
            print()

        # create child processes to run tabu_search search
        processes = []
        for tabu_id, initial_solution in enumerate(self.initial_solutions):
            processes.append(mp.Process(target=search, args=[tabu_id,
                                                             initial_solution,
                                                             self.runtime,
                                                             self.tabu_list_size,
                                                             self.neighborhood_size,
                                                             self.neighborhood_wait,
                                                             self.probability_change_machine,
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
        for tabu_id in range(self.num_processes):
            with open(f"{os.path.dirname(os.path.realpath(__file__))}/tmp/solution_{tabu_id}", 'rb') as file:
                if benchmark:
                    results = pickle.load(file)
                    self.all_solutions.append(results[0])
                    self.benchmark_iterations.append(results[1])
                    self.benchmark_neighborhood_sizes.append(results[2])
                    self.benchmark_makespans.append(results[3])
                    self.benchmark_tabu_list_sizes.append(results[4])
                    self.benchmark_min_makespan_coorinates.append(results[5])
                else:
                    self.all_solutions.append(pickle.load(file))

        self.best_solution = min(self.all_solutions)

        # remove temporary directory
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")

    def output_benchmark_results(self, output_dir, name=None):
        """
        This function generates an html file containing the following benchmark results
        obtained from this TabuSearchManager in the output directory specified.

            benchmark results:
            1. min, median, max, mean, stdev, var of all the best makespans found by each TS.
            2. min, median, max, mean, stdev, var of the total iterations of each TS.
            3. makespans vs iterations graph
            4. neighborhood sizes vs iterations graph
            5. tabu list size vs iterations graph
            6. Schedule.xlsx - schedule of the best solution found
            7. best_solution.pkl - pickled Solution object of the best solution found

        :param self: This TabuSearchManager
        :param output_dir: The output directory to place the results into
        :return: None
        """
        # get numerical results from self
        best_solution = self.best_solution
        iterations_list = self.benchmark_iterations
        neighborhood_sizes_list = self.benchmark_neighborhood_sizes
        tabu_list_sizes_list = self.benchmark_tabu_list_sizes
        makespans = self.benchmark_makespans
        min_makespan_coorinates = self.benchmark_min_makespan_coorinates
        best_makespans_list = [p[1] for p in min_makespan_coorinates]

        if name is None:
            name = "benchmark_run_{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))

        # output results
        output_directory = output_dir + "/" + name

        os.mkdir(output_directory)

        # TODO make a template for the html
        index_text = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                        <html>
                            <head>
                                <meta content="text/html; charset=ISO-8859-1"
                                    http-equiv="content-type">
                                <title>{name}</title>
                            </head>
                            <body>
                                <h2>{name}</h2>
                                <b>Parameters:</b>
                                <br>
                                search time = {self.runtime} seconds<br>
                                tabu list size = {self.tabu_list_size}<br>
                                neighborhood size = {self.neighborhood_size}<br>
                                neighborhood wait time = {self.neighborhood_wait} seconds<br>
                                probability of changing an operation's machine = {self.probability_change_machine}<br>
                                number of processes = {self.num_processes}<br>
                                initial makespan = {round(
            self.initial_solution.makespan) if self.initial_solution is not None else None}<br>
                                <br>
                                <b>Results:</b>
                                <br>
                                makespans:
                                <br>
                                min = {round(min(best_makespans_list))}<br>
                                median = {round(statistics.median(best_makespans_list))}<br>
                                max = {round(max(best_makespans_list))}<br>
                                stdev = {round(statistics.stdev(best_makespans_list))}<br>
                                var = {round(statistics.variance(best_makespans_list))}<br>
                                mean = {round(statistics.mean(best_makespans_list))}<br>
                                <br>
                                iterations:
                                <br>
                                min = {min(iterations_list)}<br>
                                median = {statistics.median(iterations_list)}<br>
                                max = {max(iterations_list)}<br>
                                stdev = {statistics.stdev(iterations_list)}<br>
                                var = {statistics.variance(iterations_list)}<br>
                                mean = {statistics.mean(iterations_list)}<br>
                                <br>
                                <b>Plots:</b>
                                <br>
                                <a href="./makespans.html">makespans vs iterations</a><br>
                                <a href="./neighborhood_sizes.html">neighborhood sizes vs iterations</a><br>
                                <a href="./tabu_list_sizes.html">tabu_search list sizes vs iterations</a><br>
                                <br>
                                <b>Schedule:</b>
                                <br>
                                <a href="file://{os.path.abspath(output_directory + "Schedule.xlsx")}">Schedule.xlsx</a><br>
                            </body>
                        </html>'''

        # create traces for plots
        makespans_traces = []
        neighborhood_sizes_traces = []
        tabu_list_sizes_traces = []
        makespans_traces.append(go.Scatter(x=[p[0] for p in min_makespan_coorinates], y=best_makespans_list, mode='markers',
                                           name='best makespans'))
        for i in range(len(iterations_list)):
            x_axis = list(range(iterations_list[i]))
            makespans_traces.append(go.Scatter(x=x_axis, y=makespans[i], name=f'tabu_search search {i}'))
            neighborhood_sizes_traces.append(go.Scatter(x=x_axis, y=neighborhood_sizes_list[i]))
            tabu_list_sizes_traces.append(go.Scatter(x=x_axis, y=tabu_list_sizes_list[i]))

        # create layouts for plots
        makespans_layout = dict(title='Makespans vs Iterations', xaxis=dict(title='Iteration'),
                                yaxis=dict(title='Makespans (minutes)'))
        nh_sizes_layout = dict(title='Neighborhood sizes vs Iterations', xaxis=dict(title='Iteration'),
                               yaxis=dict(title='Size of Neighborhood'))
        tl_sizes_layout = dict(title='Tabu list sizes vs Iterations', xaxis=dict(title='Iteration'),
                               yaxis=dict(title='Size of Tabu list'))

        # create plots
        plot(dict(data=makespans_traces, layout=makespans_layout), filename=output_directory + "/makespans.html",
             auto_open=False)
        plot(dict(data=neighborhood_sizes_traces, layout=nh_sizes_layout),
             filename=output_directory + "/neighborhood_sizes.html", auto_open=False)
        plot(dict(data=tabu_list_sizes_traces, layout=tl_sizes_layout), filename=output_directory + "/tabu_list_sizes.html",
             auto_open=False)

        # create index.html
        with open(output_directory + "/index.html", 'w') as output_file:
            output_file.write(index_text)

        # pickle best solution
        best_solution.pickle_to_file(os.path.abspath(output_directory + "/best_solution.pkl"))

        # create Schedule.xlsx
        self.best_solution.create_schedule(output_directory)

        print(f"opening file://{os.path.abspath(output_directory)} in browser")

        # open index.html in web browser
        webbrowser.open("file://" + os.path.abspath(output_directory + "/index.html"))
