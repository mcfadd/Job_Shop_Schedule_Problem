import datetime
import os
import statistics
import webbrowser

import plotly.graph_objs as go
from plotly.offline import plot

import tabu
from data import Data


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
        f"  output directory = {args.output_dir}\n" \
        f"  iterations = {args.iterations}\n" \
        f"  initial makespan = {round(args.initial_solution.makespan)}\n\n"

    print(setup_parameters)

    result_makespans = []
    iterations = []
    neighborhood_sizes = []
    tabu_list_sizes = []
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
        tabu_list_sizes.append(result[4])

    # output results
    now = datetime.datetime.now()
    directory = args.output_dir + "/benchmark_run_{}/".format(now.strftime("%Y-%m-%d_%H:%M"))
    os.mkdir(directory)
    # TODO make a template for the html
    index_text = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                    <html>
                        <head>
                            <meta content="text/html; charset=ISO-8859-1"
                                http-equiv="content-type">
                            <title>Benchmark Results {now.strftime("%Y-%m-%d %H:%M")}</title>
                        </head>
                        <body>
                        <h2>Benchmark Results {now.strftime("%Y-%m-%d %H:%M")}</h2>
                        <b>Parameters:</b><br>
                        search time = {args.runtime} seconds<br>
                        tabu list size = {args.tabu_list_size}<br>
                        neighborhood size = {args.neighborhood_size}<br>
                        neighborhood wait time = {args.neighborhood_wait} seconds<br>
                        probability of changing an operation's machine = {args.probability_change_machine}<br>
                        data directory = {args.data}<br>
                        output directory = {args.output_dir}<br>
                        iterations = {args.iterations}<br>
                        initial makespan = {round(args.initial_solution.makespan)}<br><br>
                        <b>Benchmark results:</b><br>
                        makespan:<br>
                        min = {round(min(result_makespans))}<br>
                        median = {round(statistics.median(result_makespans))}<br>
                        max = {round(max(result_makespans))}<br>
                        stdev = {round(statistics.stdev(result_makespans))}<br>
                        var = {round(statistics.variance(result_makespans))}<br>
                        mean = {round(statistics.mean(result_makespans))}<br><br>
                        iterations:<br>
                        min = {min(iterations)}<br>
                        median = {statistics.median(iterations)}<br>
                        max = {max(iterations)}<br>
                        stdev = {statistics.stdev(iterations)}<br>
                        var = {statistics.variance(iterations)}<br>
                        mean = {statistics.mean(iterations)}<br><br>
                        <b>Plots:</b><br>
                        <a href="./makespans.html">makespans vs iterations</a><br>
                        <a href="./neighborhood_sizes.html">neighborhood sizes vs iterations</a><br>
                        <a href="./tabu_list_sizes.html">tabu list sizes vs iterations</a><br>
                        </body>
                    </html>'''

    # create plots for makespans vs iterations and neighborhood sizes vs iterations
    makespans_traces = []
    neighborhood_sizes_traces = []
    tabu_list_sizes_traces = []
    for i in range(len(iterations)):
        x_axis = list(range(iterations[i]))
        makespans_traces.append(go.Scatter(x=x_axis, y=makespans[i]))
        neighborhood_sizes_traces.append(go.Scatter(x=x_axis, y=neighborhood_sizes[i]))
        tabu_list_sizes_traces.append(go.Scatter(x=x_axis, y=tabu_list_sizes[i]))

    plot(makespans_traces, filename=directory + "makespans.html", auto_open=False)
    plot(neighborhood_sizes_traces, filename=directory + "neighborhood_sizes.html", auto_open=False)
    plot(tabu_list_sizes_traces, filename=directory + "tabu_list_sizes.html", auto_open=False)

    # create index.html
    with open(directory + "index.html", 'w') as output_file:
        output_file.write(index_text)

    webbrowser.open("file://" + os.path.abspath(directory + "index.html"))
