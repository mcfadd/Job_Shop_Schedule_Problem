import multiprocessing as mp
import time

from progressbar import Bar, ETA, ProgressBar, RotatingMarker

from . import benchmark
from . import parser
from . import tabu_search
from .data import Data


def progress_bar(seconds):
    """
    Runs a progress bar for a certain duration.

    :param seconds: Duration to run the process bar for in seconds
    :return: None
    """
    widgets = [Bar(marker=RotatingMarker()), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        time.sleep(.99)
        pbar.update(i)
    pbar.finish()
    print()


def main(runtime, output_dir, num_processes=4, tabu_list_size=50, neighborhood_size=300, neighborhood_wait=0.1,
         probability_change_machine=0.8, verbose=False):
    """
    Runs the main program.

    This function runs Tabu Search in parallel for a certain duration then outputs a schedule of the best solution found in the output directory.

    :param runtime:
    :param output_dir:
    :param num_processes:
    :param tabu_list_size:
    :param neighborhood_size:
    :param neighborhood_wait:
    :param probability_change_machine:
    :param verbose:
    :return: 0 if successful
    """
    print(f"Parameters:\n"
          f"number of processes = {num_processes}\n"
          f"runtime = {runtime} seconds\n"
          f"tabu_search list size = {tabu_list_size}\n"
          f"neighborhood size = {neighborhood_size}\n"
          f"neighborhood wait time = {neighborhood_wait} seconds\n"
          f"probability of changing an operation's machine = {probability_change_machine}\n"
          f"output directory = {output_dir}")

    ts_manager = tabu_search.TabuSearchManager(runtime,
                                               num_processes,
                                               tabu_list_size,
                                               neighborhood_size,
                                               neighborhood_wait,
                                               probability_change_machine)
    ts_manager.start(verbose=verbose)

    print("Tabu Search Makespan Results:")
    print([solution.makespan for solution in ts_manager.all_solutions])
    print()
    print("Best Solution Found:")
    ts_manager.best_solution.pprint()
    print()
    print(f"Schedule.xlsx placed in {output_dir}")
    ts_manager.best_solution.create_schedule(output_dir)

    return 0


def command_line_interface():
    mp.set_start_method('fork')
    args = parser.parse_args()

    # initialize static data from csv files
    Data.initialize_data(f'{args.data}/sequenceDependencyMatrix.csv',
                         f'{args.data}/machineRunSpeed.csv',
                         f'{args.data}/jobTasks.csv')

    if args.progress_bar:
        mp.Process(target=progress_bar, args=[args.runtime]).start()

    if args.benchmark:
        return benchmark.run(args.runtime, args.output_dir, args.num_processes, args.tabu_list_size, args.neighborhood_size,
                             args.neighborhood_wait, args.probability_change_machine, args.initial_solution,
                             args.verbose)
    else:
        return main(args.runtime, args.output_dir, args.num_processes, args.tabu_list_size, args.neighborhood_size,
                    args.neighborhood_wait, args.probability_change_machine,
                    args.verbose)
