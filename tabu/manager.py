import os
import shutil
import solution
import multiprocessing as mp
from tabu.search import search
import pickle


class TabuSearchManager:

    def __init__(self, arguments_namespace):

        # get required arguments for tabu search
        self.tabu_search_runtime = arguments_namespace.runtime
        self.tabu_list_size = arguments_namespace.tabu_list_size
        self.neighborhood_size = arguments_namespace.neighborhood_size
        self.neighborhood_wait = arguments_namespace.neighborhood_wait
        self.probability_change_machine = arguments_namespace.probability_change_machine
        self.number_processes = arguments_namespace.num_processes

        # uninitialized initial solutions to start TS from
        self.initial_solutions = []

        # uninitialized results
        self.all_solutions = []
        self.best_solution = None

        # benchmark specific arguments and results
        if arguments_namespace.benchmark:
            self.is_benchmark = True
            self.benchmark_initial_solution = arguments_namespace.initial_solution
            self.benchmark_best_makespan_found = []
            self.benchmark_makespans = []
            self.benchmark_iterations = []
            self.benchmark_neighborhood_sizes = []
            self.benchmark_tabu_list_sizes = []
        else:
            self.is_benchmark = False

    def start(self, verbose=False):
        parent_process_id = os.getpid()

        # remove temporary directory if it exists
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp", ignore_errors=True)

        # create temporary directory for storing results
        os.mkdir(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")

        # create random initial solutions
        if self.is_benchmark and self.benchmark_initial_solution is not None:
            self.initial_solutions = [self.benchmark_initial_solution] * self.number_processes
        else:
            for _ in range(self.number_processes):
                self.initial_solutions.append(solution.generate_feasible_solution())

        if verbose:
            print()
            print("Initial Solutions makespans:")
            print([round(x.makespan) for x in self.initial_solutions])
            print()

        # create child processes
        processes = []
        for tabu_id, initial_solution in enumerate(self.initial_solutions):
            processes.append(mp.Process(target=search, args=[tabu_id,
                                                             initial_solution,
                                                             self.tabu_search_runtime,
                                                             self.tabu_list_size,
                                                             self.neighborhood_size,
                                                             self.neighborhood_wait,
                                                             self.probability_change_machine,
                                                             self.is_benchmark]))

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
                if self.is_benchmark:
                    results = pickle.load(file)
                    self.benchmark_best_makespan_found.append(results[0].makespan)
                    self.benchmark_iterations.append(results[1])
                    self.benchmark_neighborhood_sizes.append(results[2])
                    self.benchmark_makespans.append(results[3])
                    self.benchmark_tabu_list_sizes.append(results[4])
                else:
                    self.all_solutions.append(pickle.load(file))

        if not self.is_benchmark:
            self.best_solution = min(self.all_solutions)

        # remove temporary directory
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp")
