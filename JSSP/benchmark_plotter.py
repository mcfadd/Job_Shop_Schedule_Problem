import datetime
import os
import statistics
import webbrowser

import plotly.graph_objs as go
from plotly.offline import plot, iplot


def iplot_benchmark_results(ts_agent_list=None, ga_agent=None):
    """
    Plots the benchmark results in an ipython notebook.

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to plot the benchmark results for

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent to plot the results for

    :returns: None
    """
    if ts_agent_list is not None and all(ts_agent.benchmark for ts_agent in ts_agent_list):
        best_makespans_per_ts_agent = []
        iterations_per_ts_agent = []
        for ts_agent in ts_agent_list:
            best_makespans_per_ts_agent.append(ts_agent.min_makespan_coordinates[1])
            iterations_per_ts_agent.append(ts_agent.benchmark_iterations)

        # create traces for plots
        makespans_traces, makespans_layout, \
        nh_sizes_traces, nh_sizes_layout, \
        tl_sizes_traces, tl_sizes_layout = _make_ts_traces(ts_agent_list)

        # create plots
        iplot(dict(data=makespans_traces, layout=makespans_layout))
        iplot(dict(data=nh_sizes_traces, layout=nh_sizes_layout))
        iplot(dict(data=tl_sizes_traces, layout=tl_sizes_layout))
        min([ts_agent.best_solution for ts_agent in ts_agent_list]).iplot_gantt_chart(continuous=True)

    if ga_agent is not None and ga_agent.benchmark:
        # create traces for plot
        makespans_traces, makespans_layout = _make_ga_traces(ga_agent)

        # create plot
        iplot(dict(data=makespans_traces, layout=makespans_layout))
        ga_agent.best_solution.iplot_gantt_chart(continuous=True)


def output_benchmark_results(output_dir, ts_agent_list=None, ga_agent=None, name=None, auto_open=True):
    """
    Outputs html files containing benchmark results in the output directory specified.

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to output the benchmark results for

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent instance to output the benchmark results for

    :type output_dir: str
    :param output_dir: path to the output directory to place the html files into

    :type name: str
    :param name: name of the benchmark run, default to current datetime

    :type auto_open: bool
    :param auto_open: if true the benchmark output is automatically opened in a browser

    :returns: None
    """
    if (ts_agent_list is None or not all(ts_agent.benchmark for ts_agent in ts_agent_list)) \
            and (ga_agent is None or not ga_agent.benchmark):
        return

    if name is None:
        name = "benchmark_run_{}".format(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))

    # output results
    output_directory = os.path.abspath(output_dir + os.sep + name)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    index_text = f'''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
                    <html>
                        <head>
                            <meta content="text/html; charset=ISO-8859-1"
                                http-equiv="content-type">
                            <title>{name}</title>
                        </head>
                        <body>
                            <h2>{name}</h2>
                            {_ts_benchmark_results(ts_agent_list, output_directory) if ts_agent_list and all(ts_agent.benchmark for ts_agent in ts_agent_list) else ''}
                            {_ga_benchmark_results(ga_agent, output_directory) if ga_agent and ga_agent.benchmark else ''}
                        {'<br>' * 10}
                        </body>
                    </html>
                    '''

    # create index.html
    with open(output_directory + '/index.html', 'w') as output_file:
        output_file.write(index_text)

    if auto_open:
        print(f'opening file://{output_directory} in browser')
        webbrowser.open(f'file://{output_directory}/index.html')


def _ts_benchmark_results(ts_agent_list, output_directory):
    """
    Formats TS benchmark results in an html file & creates plots (html files).

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to output the benchmark results for

    :type output_directory: str
    :param output_directory: path to the directory to place the html files containing plots into

    :rtype: str
    :returns: html containing benchmark results
    """
    best_makespans_per_ts_agent = []
    iterations_per_ts_agent = []
    for ts_agent in ts_agent_list:
        best_makespans_per_ts_agent.append(ts_agent.min_makespan_coordinates[1])
        iterations_per_ts_agent.append(ts_agent.benchmark_iterations)

    # TODO come up with a way to display individual TS agent parameters
    html = f'''
        <h3>Tabu Search</h3>
        <b>Parameters:</b>
        <br>
        {"runtime = " + str(ts_agent_list[0].runtime) + " seconds" if ts_agent_list[0].time_condition
    else "iterations = " + str(ts_agent_list[0].iterations)}<br>
        number of processes = {len(ts_agent_list)}<br>
        number of solutions to return per processes = {ts_agent_list[0].num_solutions_to_find}<br>
        tabu list size = {ts_agent_list[0].tabu_list_size}<br>
        neighborhood size = {ts_agent_list[0].neighborhood_size}<br>
        neighborhood wait = {ts_agent_list[0].neighborhood_wait} seconds<br>
        probability of changing an operation's machine = {ts_agent_list[0].probability_change_machine}<br>
        reset threshold = {ts_agent_list[0].reset_threshold} iterations<br>
        best initial makespan = {round(min([ts_agent.initial_solution for ts_agent in ts_agent_list]).makespan)}<br>
        <br>
        <b>Makespan Results:</b>
        <br>
        min = {round(min(best_makespans_per_ts_agent))}<br>
        median = {round(statistics.median(best_makespans_per_ts_agent))}<br>
        max = {round(max(best_makespans_per_ts_agent))}<br>
        stdev = {round(statistics.stdev(best_makespans_per_ts_agent)) if len(
        best_makespans_per_ts_agent) > 1 else 0}<br>
        var = {round(statistics.variance(best_makespans_per_ts_agent)) if len(
        best_makespans_per_ts_agent) > 1 else 0}<br>
        mean = {round(statistics.mean(best_makespans_per_ts_agent))}<br>
        <br>
        <b>Iterations Results:</b>
        <br>
        min = {min(iterations_per_ts_agent)}<br>
        median = {statistics.median(iterations_per_ts_agent)}<br>
        max = {max(iterations_per_ts_agent)}<br>
        stdev = {statistics.stdev(iterations_per_ts_agent) if len(iterations_per_ts_agent) > 1 else 0}<br>
        var = {statistics.variance(iterations_per_ts_agent) if len(iterations_per_ts_agent) > 1 else 0}<br>
        mean = {statistics.mean(iterations_per_ts_agent)}<br>
        <br>
        <b>Plots:</b>
        <br>
        <a href="./ts_makespans.html">Makespan vs Iteration</a><br>
        <a href="./neighborhood_sizes.html">Neighborhood Size vs Iteration</a><br>
        <a href="./tabu_list_sizes.html">Tabu Size vs Iteration</a><br>
        <br>
        <b>Schedule:</b>
        <br>
        <a href="file://{output_directory}/ts_schedule.xlsx">ts_schedule.xlsx</a><br>
        <a href="./ts_gantt_chart.html">Gantt Chart</a>
        <br>
        '''

    # create traces for plots
    makespans_traces, makespans_layout, \
    nh_sizes_traces, nh_sizes_layout, \
    tl_sizes_traces, tl_sizes_layout = _make_ts_traces(ts_agent_list)

    # create plots
    plot(dict(data=makespans_traces, layout=makespans_layout),
         filename=output_directory + '/ts_makespans.html',
         auto_open=False)
    plot(dict(data=nh_sizes_traces, layout=nh_sizes_layout),
         filename=output_directory + '/neighborhood_sizes.html',
         auto_open=False)
    plot(dict(data=tl_sizes_traces, layout=tl_sizes_layout),
         filename=output_directory + '/tabu_list_sizes.html',
         auto_open=False)

    # create schedule
    best_solution = min([ts_agent.best_solution for ts_agent in ts_agent_list])
    best_solution.create_schedule_xlsx_file(output_directory + os.sep + 'ts_schedule', continuous=True)
    best_solution.create_gantt_chart_html_file(output_directory + os.sep + 'ts_gantt_chart.html', continuous=True)

    return html


def _ga_benchmark_results(ga_agent, output_directory):
    """
    Formats GA benchmark results in an html file & creates plots (html files).

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent instance to output the benchmark results for

    :type output_directory: str
    :param output_directory: path to the directory to place the html files containing plots

    :rtype: str
    :returns: html containing benchmark results
    """
    initial_population_makespans = [sol.makespan for sol in ga_agent.initial_population]
    result_population_makespans = [sol.makespan for sol in ga_agent.result_population]
    html = f'''
        <h3>Genetic Algorithm</h3>
        <b>Parameters:</b>
        <br>
        {"runtime = " + str(ga_agent.runtime) + " seconds" if ga_agent.time_condition
    else "generations = " + str(ga_agent.iterations)}<br>
        population size = {ga_agent.population_size}<br>
        selection method = {ga_agent.selection_method.__name__}<br>
        selection size = {ga_agent.selection_size}<br>
        mutation probability = {ga_agent.mutation_probability}<br>
        <br>
        <b>Initial Population Makespans:</b>
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
        <b>Final Population Makespans:</b>
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
        <br>
        <b>Schedule:</b>
        <br>
        <a href="file://{output_directory}/ga_schedule.xlsx">ga_schedule.xlsx</a><br>
        <a href="./ga_gantt_chart.html">Gantt Chart</a>
        <br>
        '''

    # create trace for plot
    makespans_traces, makespans_layout = _make_ga_traces(ga_agent)

    # create plot
    plot(dict(data=makespans_traces, layout=makespans_layout),
         filename=output_directory + '/ga_makespans.html',
         auto_open=False)

    # create schedule
    ga_agent.best_solution.create_schedule_xlsx_file(output_directory + os.sep + 'ga_schedule', continuous=True)
    ga_agent.best_solution.create_gantt_chart_html_file(output_directory + os.sep + 'ga_gantt_chart.html', continuous=True)

    return html


def _make_ts_traces(ts_agent_list):
    """
    Makes and returns traces and layouts of the benchmark results of the TabuSearchAgent instances in ts_agent_list.

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to make traces and layouts for

    :rtype: [trace, layout]
    :returns: list of traces and layouts
    """
    # create traces for plots
    makespans_traces = [
        go.Scatter(x=[ts_agent.min_makespan_coordinates[0] for ts_agent in ts_agent_list],
                   y=[ts_agent.min_makespan_coordinates[1] for ts_agent in ts_agent_list], mode='markers', name='best makespans')
    ]

    nh_sizes_traces = []
    tl_sizes_traces = []

    for i, ts_agent in enumerate(ts_agent_list):
        x_axis = list(range(ts_agent.benchmark_iterations))
        makespans_traces.append(
            go.Scatter(x=x_axis, y=ts_agent.seed_solution_makespan_v_iter, name=f'TS trace {i}'))
        nh_sizes_traces.append(
            go.Scatter(x=x_axis, y=ts_agent.neighborhood_size_v_iter, name=f'TS trace {i}'))
        tl_sizes_traces.append(go.Scatter(x=x_axis, y=ts_agent.tabu_size_v_iter, name=f'TS trace {i}'))

    # create layouts for plots
    makespans_layout = dict(title='Seed Solution Makespan vs Iteration',
                            xaxis=dict(title='Iteration'),
                            yaxis=dict(title='Makespans (minutes)'))
    nh_sizes_layout = dict(title='Neighborhood size vs Iteration',
                           xaxis=dict(title='Iteration'),
                           yaxis=dict(title='Size of Neighborhood'))
    tl_sizes_layout = dict(title='Tabu list size vs Iteration',
                           xaxis=dict(title='Iteration'),
                           yaxis=dict(title='Size of Tabu list'))

    return makespans_traces, makespans_layout, nh_sizes_traces, nh_sizes_layout, tl_sizes_traces, tl_sizes_layout


def _make_ga_traces(ga_agent):
    """
    Makes and returns traces and layouts of the benchmark results of ga_agent.

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent instance to make traces and layouts for

    :rtype: (trace, layout)
    :returns: tuple containing (trace, layout)
    """
    # create traces for plot
    makespans_traces = [
        go.Scatter(x=[ga_agent.min_makespan_coordinates[0]], y=[ga_agent.min_makespan_coordinates[1]],
                   mode='markers',
                   name='best makespan'),
        go.Scatter(x=list(range(ga_agent.benchmark_iterations)), y=ga_agent.best_solution_makespan_v_iter,
                   name='Best makespan trace'),
        go.Scatter(x=list(range(ga_agent.benchmark_iterations)), y=ga_agent.avg_population_makespan_v_iter,
                   name='Avg population makespan')
    ]

    # create layouts for plot
    makespans_layout = dict(title='Makespans vs Iterations',
                            xaxis=dict(title='Iteration'),
                            yaxis=dict(title='Makespans (minutes)'))

    return makespans_traces, makespans_layout
