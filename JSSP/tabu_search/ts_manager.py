import multiprocessing as mp
import os
import pickle
import shutil

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
        self.number_processes = num_processes
        self.tabu_search_runtime = runtime
        self.tabu_list_size = tabu_list_size
        self.neighborhood_size = neighborhood_size
        self.neighborhood_wait = neighborhood_wait
        self.probability_change_machine = probability_change_machine

        # uninitialized initial solutions to start TS from
        self.initial_solutions = []

        # uninitialized results
        self.all_solutions = []
        self.best_solution = None

        # benchmark specific arguments and results
        self.benchmark_initial_solution = initial_solution
        self.benchmark_makespans = []
        self.benchmark_iterations = []
        self.benchmark_neighborhood_sizes = []
        self.benchmark_tabu_list_sizes = []
        self.benchmark_min_makespan_coorinates = []

    def start(self, benchmark=False, verbose=False):
        """
        This function first generates random initial solutions if an initial solution is not given,
        then it forks a number of child processes equal to self.number_processes that run tabu_search search with the fields of this TabuSearchManager.
        The parent process waits for the children to finish, then collects their pickled results from a temporary directory.

        :param benchmark:
        :param verbose:
        :return:
        """
        parent_process_id = os.getpid()

        # remove temporary directory if it exists
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp", ignore_errors=True)

        # create temporary directory for storing results
        os.mkdir(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")

        # create random initial solutions
        if benchmark and self.benchmark_initial_solution is not None:
            self.initial_solutions = [self.benchmark_initial_solution] * self.number_processes
        else:
            for _ in range(self.number_processes):
                self.initial_solutions.append(generate_feasible_solution())

        if verbose:
            print()
            print("Initial Solutions makespans:")
            print([round(x.makespan) for x in self.initial_solutions])
            print()

        # create child processes to run tabu_search search
        processes = []
        for tabu_id, initial_solution in enumerate(self.initial_solutions):
            processes.append(mp.Process(target=search, args=[tabu_id,
                                                             initial_solution,
                                                             self.tabu_search_runtime,
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
        for tabu_id in range(self.number_processes):
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

        # create population of all solutions found
        # with open(f"{os.path.dirname(os.path.realpath(__file__))}/test_population.pkl", 'wb') as file:
        #     pickle.dump(self.all_solutions, file, protocol=-1)

        # remove temporary directory
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")
