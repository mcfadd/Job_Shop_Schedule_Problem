import datetime
import os
import statistics
import webbrowser

import plotly.graph_objs as go
from plotly.offline import plot


def output_benchmark_results(ts_manager, output_dir):
    """
    This function generates an html file containing the following benchmark results
    obtained from a TabuSearchManager in the output directory specified.

        benchmark results:
        1. min, median, max, mean, stdev, var of all the best makespans found by each TS.
        2. min, median, max, mean, stdev, var of the total iterations of each TS.
        3. makespans vs iterations graph
        4. neighborhood sizes vs iterations graph
        5. tabu list size vs iterations graph
        6. Schedule.xlsx - schedule of the best solution found
        7. best_solution.pkl - pickled Solution object of the best solution found

    :param ts_manager: The TabuSearchManager object to get the results from
    :param output_dir: The output directory to place the results into
    :return: None
    """
    # get numerical results from ts_manager
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
                            search time = {ts_manager.runtime} seconds<br>
                            tabu list size = {ts_manager.tabu_list_size}<br>
                            neighborhood size = {ts_manager.neighborhood_size}<br>
                            neighborhood wait time = {ts_manager.neighborhood_wait} seconds<br>
                            probability of changing an operation's machine = {ts_manager.probability_change_machine}<br>
                            output directory = {output_dir}<br>
                            number of processes = {ts_manager.num_processes}<br>
                            initial makespan = {round(
        ts_manager.initial_solution.makespan) if ts_manager.initial_solution is not None else None}<br>
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
    plot(dict(data=makespans_traces, layout=makespans_layout), filename=output_directory + "makespans.html",
         auto_open=False)
    plot(dict(data=neighborhood_sizes_traces, layout=nh_sizes_layout),
         filename=output_directory + "neighborhood_sizes.html", auto_open=False)
    plot(dict(data=tabu_list_sizes_traces, layout=tl_sizes_layout), filename=output_directory + "tabu_list_sizes.html",
         auto_open=False)

    # create index.html
    with open(output_directory + "index.html", 'w') as output_file:
        output_file.write(index_text)

    # pickle best solution
    best_solution.pickle_to_file(os.path.abspath(output_directory + "best_solution.pkl"))

    # create Schedule.xlsx
    ts_manager.best_solution.create_schedule(output_directory)

    print(f"opening file://{os.path.abspath(output_directory)} in browser")

    # open index.html in web browser
    webbrowser.open("file://" + os.path.abspath(output_directory + "index.html"))
