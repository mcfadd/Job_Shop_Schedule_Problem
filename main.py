import time
from progressbar import Bar, ETA, ProgressBar, RotatingMarker
import multiprocessing as mp
import sys
import tabu
import benchmark
import solution
from data import Data
from parser import parser


def progress_bar(seconds):
    widgets = [Bar(marker=RotatingMarker()), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        time.sleep(.97)
        pbar.update(i)
    pbar.finish()
    print()


def main(args):
    print(f"Parameters:\n"
          f"runtime = {args.runtime} seconds\n"
          f"tabu list size = {args.tabu_list_size}\n"
          f"neighborhood size = {args.neighborhood_size}\n"
          f"neighborhood wait time = {args.neighborhood_wait} seconds\n"
          f"probability of changing an operation's machine = {args.probability_change_machine}\n"
          f"data directory = {args.data}")

    Data.initialize_data(f'{args.data}/sequenceDependencyMatrix.csv',
                         f'{args.data}/machineRunSpeed.csv',
                         f'{args.data}/jobTasks.csv')

    initial_solution = solution.generate_feasible_solution()

    print()
    print("Initial Solution:")
    print(f"makespan = {round(initial_solution.makespan)}")
    print()

    result = tabu.search(initial_solution=initial_solution,
                         search_time=args.runtime,
                         tabu_size=args.tabu_list_size,
                         neighborhood_size=args.neighborhood_size,
                         neighborhood_wait=args.neighborhood_wait,
                         probability_change_machine=args.probability_change_machine)

    print("Tabu Search Result:")
    result.pprint()


if __name__ == '__main__':
    arguments = parser.parse_args(sys.argv[1:])
    if not arguments.benchmark:
        arguments.iterations = 1
        func = main
    else:
        func = benchmark.run

    if arguments.progress_bar:
        mp.set_start_method('spawn')
        mp.Process(target=progress_bar, args=[arguments.iterations * arguments.runtime]).start()

    func(arguments)
