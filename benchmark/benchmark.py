import datetime
import statistics

from data import Data
import tabu


def run(args):
    print("Running Benchmark")
    # read csv files and construct static data
    Data.initialize_data(f'{args.data}/sequenceDependencyMatrix.csv',
                         f'{args.data}/machineRunSpeed.csv',
                         f'{args.data}/jobTasks.csv')

    setup_parameters = f"\n" \
        f"Parameters:\n\n" \
        f"  search time = {args.runtime} seconds\n" \
        f"  tabu list size = {args.tabu_list_size}\n" \
        f"  neighborhood size = {args.neighborhood_size}\n" \
        f"  neighborhood wait time = {args.neighborhood_wait} seconds\n" \
        f"  probability of changing an operation's machine = {args.probability_change_machine}\n" \
        f"  data directory = {args.data}\n" \
        f"  iterations = {args.iterations}\n" \
        f"  initial makespan = {round(args.initial_solution.makespan)}\n\n"

    if args.output_dir is None:
        print(setup_parameters)

    result_makespans = []
    iterations = []
    neighborhood_sizes = []
    makespans = []
    for i in range(args.iterations):
        result = tabu.search(initial_solution=args.initial_solution,
                             search_time=args.runtime,
                             tabu_size=args.tabu_list_size,
                             neighborhood_size=args.neighborhood_size,
                             neighborhood_wait=args.neighborhood_wait,
                             probability_change_machine=args.probability_change_machine,
                             benchmark=True)

        result_makespans.append(result[0].makespan)
        iterations.append(result[1])
        neighborhood_sizes.append(result[2])
        makespans.append(result[3])

    benchmark_results = "Benchmark results:\n\n" \
                        " makespan:\n" \
        f"  min = {round(min(result_makespans))}\n" \
        f"  median = {round(statistics.median(result_makespans))}\n" \
        f"  max = {round(max(result_makespans))}\n" \
        f"  stdev = {round(statistics.stdev(result_makespans))}\n" \
        f"  var = {round(statistics.variance(result_makespans))}\n" \
        f"  mean = {round(statistics.mean(result_makespans))}\n\n" \
                        " iterations:\n" \
        f"  min = {min(iterations)}\n" \
        f"  median = {statistics.median(iterations)}\n" \
        f"  max = {max(iterations)}\n" \
        f"  stdev = {statistics.stdev(iterations)}\n" \
        f"  var = {statistics.variance(iterations)}\n" \
        f"  mean = {statistics.mean(iterations)}\n\n"

    # f"  neighborhood_sizes:\n{neighborhood_sizes}\n" \
    # f"  makespans:\n {makespans}\n\n" \

    if args.output_dir is not None:
        now = datetime.datetime.now()
        with open(args.output_dir + "/benchmark_results_{}".format(now.strftime("%Y-%m-%d_%H:%M")), 'w') as output_file:
            output_file.write(setup_parameters)
            output_file.write(benchmark_results)
    else:
        print(benchmark_results)
