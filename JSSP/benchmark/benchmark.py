import datetime
import os
import statistics
import webbrowser

import plotly.graph_objs as go
from plotly.offline import plot

from JSSP import tabu_search


def run(runtime, output_dir, num_processes=4, tabu_list_size=50, neighborhood_size=300, neighborhood_wait=0.1,
        probability_change_machine=0.8, initial_solution=None, verbose=False):
    """
    Runs a benchmark of the program.

    This function runs Tabu Search in parallel for a certain duration,
    then puts the following benchmark results into the output directory specified.

        benchmark results:
        1. min, median, max, mean, stdev, var of best makespans found by each TS.
        2. min, median, max, mean, stdev, var of total iterations of each TS.
        3. makespans vs iterations graph
        4. neighborhood sizes vs iterations graph
        5. tabu list size vs iterations
        6. Schedule.xlsx
        7. best_solution.pkl

    :param runtime:
    :param output_dir:
    :param num_processes:
    :param tabu_list_size:
    :param neighborhood_size:
    :param neighborhood_wait:
    :param probability_change_machine:
    :param initial_solution:
    :param verbose:
    :return: 0 if successful
    """
    print("Running Benchmark")

    setup_parameters = f"\n" \
        f"Parameters:\n\n" \
        f"  search time = {runtime} seconds\n" \
        f"  tabu_search list size = {tabu_list_size}\n" \
        f"  neighborhood size = {neighborhood_size}\n" \
        f"  neighborhood wait time = {neighborhood_wait} seconds\n" \
        f"  probability of changing an operation's machine = {probability_change_machine}\n" \
        f"  output directory = {output_dir}\n" \
        f"  number of processes = {num_processes}\n" \
        f"  initial makespan = {round(initial_solution.makespan) if initial_solution is not None else None}\n\n"

    print(setup_parameters)

    ts_manager = tabu_search.TabuSearchManager(runtime,
                                               num_processes,
                                               tabu_list_size,
                                               neighborhood_size,
                                               neighborhood_wait,
                                               probability_change_machine,
                                               initial_solution)

    ts_manager.start(benchmark=True, verbose=verbose)

    best_solution = ts_manager.best_solution
    iterations_list = ts_manager.benchmark_iterations
    neighborhood_sizes_list = ts_manager.benchmark_neighborhood_sizes
    tabu_list_sizes_list = ts_manager.benchmark_tabu_list_sizes
    makespans = ts_manager.benchmark_makespans
    min_makespan_coorinates = ts_manager.benchmark_min_makespan_coorinates
    best_makespans_list = [p[1] for p in min_makespan_coorinates]

    # output results
    now = datetime.datetime.now()
    output_directory = output_dir + "/benchmark_run_{}/".format(now.strftime("%Y-%m-%d_%H:%M"))
    os.mkdir(output_directory)
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
                            <b>Parameters:</b>
                            <br>
                            search time = {runtime} seconds<br>
                            tabu_search list size = {tabu_list_size}<br>
                            neighborhood size = {neighborhood_size}<br>
                            neighborhood wait time = {neighborhood_wait} seconds<br>
                            probability of changing an operation's machine = {probability_change_machine}<br>
                            output directory = {output_dir}<br>
                            number of processes = {num_processes}<br>
                            initial makespan = {round(
        initial_solution.makespan) if initial_solution is not None else None}<br>
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
    plot(dict(data=makespans_traces, layout=makespans_layout), filename=output_directory + "makespans.html",
         auto_open=False)
    plot(dict(data=neighborhood_sizes_traces, layout=nh_sizes_layout),
         filename=output_directory + "neighborhood_sizes.html", auto_open=False)
    plot(dict(data=tabu_list_sizes_traces, layout=tl_sizes_layout), filename=output_directory + "tabu_list_sizes.html",
         auto_open=False)

    # create index.html
    with open(output_directory + "index.html", 'w') as output_file:
        output_file.write(index_text)

    # open in web brower
    webbrowser.open("file://" + os.path.abspath(output_directory + "index.html"))

    # pickle best solution
    best_solution.pickle_to_file(os.path.abspath(output_directory + "best_solution.pkl"))

    # create schedule
    best_solution.create_schedule(os.path.abspath(output_directory))

    return 0
