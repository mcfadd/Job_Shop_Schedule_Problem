import datetime
import os
import statistics
import webbrowser

import plotly.graph_objs as go
from jinja2 import PackageLoader, Environment, select_autoescape
from plotly.offline import plot, iplot

template_env = Environment(
    loader=PackageLoader('JSSP', 'templates')
)

benchmark_template = "benchmark.html"


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


def output_benchmark_results(output_dir, ts_agent_list=None, ga_agent=None, title=None, auto_open=True):
    """
    Outputs html files containing benchmark results in the output directory specified.

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to output the benchmark results for

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent instance to output the benchmark results for

    :type output_dir: Path
    :param output_dir: path to the output directory to place the html files into

    :type title: str
    :param title: name of the benchmark run, default to current datetime

    :type auto_open: bool
    :param auto_open: if true the benchmark output is automatically opened in a browser

    :returns: None
    """
    if (ts_agent_list is None or not all(ts_agent.benchmark for ts_agent in ts_agent_list)) \
            and (ga_agent is None or not ga_agent.benchmark):
        return

    if title is None:
        title = "Benchmark Run {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    def compute_stats(lst):
        return {
            'min': round(min(lst)),
            'median': round(statistics.median(lst)),
            'max': round(max(lst)),
            'std': round(statistics.stdev(lst)) if len(lst) > 1 else 0,
            'var': round(statistics.variance(lst)) if len(lst) > 1 else 0,
            'mean': round(statistics.mean(lst))
        }

    # tabu search results
    if ts_agent_list is not None:
        _ts_benchmark_results(ts_agent_list, output_dir)
        ts_result_makespans = []
        ts_initial_makespans = []
        ts_iterations = []
        for ts_agent in ts_agent_list:
            ts_result_makespans.append(ts_agent.best_solution.makespan)
            ts_initial_makespans.append(ts_agent.initial_solution.makespan)
            ts_iterations.append(ts_agent.benchmark_iterations)

        ts_result_makespans_stats = compute_stats(ts_result_makespans)
        ts_initial_makespans_stats = compute_stats(ts_initial_makespans)
        ts_iterations_stats = compute_stats(ts_iterations)

    else:
        ts_result_makespans_stats = None
        ts_initial_makespans_stats = None
        ts_iterations_stats = None

    # genetic algorithm results
    if ga_agent is not None:
        _ga_benchmark_results(ga_agent, output_dir)
        ga_initial_makespans = [sol.makespan for sol in ga_agent.initial_population]
        ga_result_makespans = [sol.makespan for sol in ga_agent.result_population]

        ga_initial_makespans_stats = compute_stats(ga_initial_makespans)
        ga_result_makespans_stats = compute_stats(ga_result_makespans)

    else:
        ga_initial_makespans_stats = None
        ga_result_makespans_stats = None

    # render template
    template = template_env.get_template(benchmark_template)
    rendered_template = template.render(
        title=title,
        ts_agent_list=ts_agent_list,
        ts_initial_makespans_stats=ts_initial_makespans_stats,
        ts_result_makespans_stats=ts_result_makespans_stats,
        iterations_per_ts_agent_stats=ts_iterations_stats,
        output_directory=output_dir.resolve(),
        ga_agent=ga_agent,
        ga_initial_makespans_stats=ga_initial_makespans_stats,
        ga_result_makespans_stats=ga_result_makespans_stats,
    )

    # create index.html
    with open(output_dir / 'index.html', 'w') as output_file:
        output_file.write(rendered_template)

    if auto_open:
        webbrowser.open(f'file://{output_dir.resolve()}/index.html')


def _ts_benchmark_results(ts_agent_list, output_directory):
    """
    Formats TS benchmark results in an html file & creates plots (html files).

    :type ts_agent_list: [TabuSearchAgent]
    :param ts_agent_list: list of TabuSearchAgent instances to output the benchmark results for

    :type output_directory: Path
    :param output_directory: path to the directory to place the html files containing plots into

    :rtype: str
    :returns: html containing benchmark results
    """

    # create traces for plots
    makespans_traces, makespans_layout, \
    nh_sizes_traces, nh_sizes_layout, \
    tl_sizes_traces, tl_sizes_layout = _make_ts_traces(ts_agent_list)

    # create plots
    plot(dict(data=makespans_traces, layout=makespans_layout),
         filename=str(output_directory / 'ts_makespans.html'),
         auto_open=False)
    plot(dict(data=nh_sizes_traces, layout=nh_sizes_layout),
         filename=str(output_directory / 'neighborhood_sizes.html'),
         auto_open=False)
    plot(dict(data=tl_sizes_traces, layout=tl_sizes_layout),
         filename=str(output_directory / 'tabu_list_sizes.html'),
         auto_open=False)

    # create schedule
    best_solution = min([ts_agent.best_solution for ts_agent in ts_agent_list])
    best_solution.create_schedule_xlsx_file(str(output_directory / 'ts_schedule'), continuous=True)
    best_solution.create_gantt_chart_html_file(str(output_directory / 'ts_gantt_chart.html'), continuous=True)


def _ga_benchmark_results(ga_agent, output_directory):
    """
    Formats GA benchmark results in an html file & creates plots (html files).

    :type ga_agent: GeneticAlgorithmAgent
    :param ga_agent: GeneticAlgorithmAgent instance to output the benchmark results for

    :type output_directory: Path
    :param output_directory: path to the directory to place the html files containing plots

    :rtype: str
    :returns: html containing benchmark results
    """

    # create trace for plot
    makespans_traces, makespans_layout = _make_ga_traces(ga_agent)

    # create plot
    plot(dict(data=makespans_traces, layout=makespans_layout),
         filename=str(output_directory / 'ga_makespans.html'),
         auto_open=False)

    # create schedule
    ga_agent.best_solution.create_schedule_xlsx_file(str(output_directory / 'ga_schedule'), continuous=True)
    ga_agent.best_solution.create_gantt_chart_html_file(str(output_directory / 'ga_gantt_chart.html'), continuous=True)


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
                   y=[ts_agent.min_makespan_coordinates[1] for ts_agent in ts_agent_list], mode='markers',
                   name='best makespans')
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
