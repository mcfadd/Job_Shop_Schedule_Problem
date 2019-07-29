Examples
========

This document contains examples for how to use JSSP.
For more in depth examples see the jupyter notebook files in the `examples <https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/examples>`_ folder on GitHub.

Tabu Search & Genetic Algorithm Example
---------------------------------------

The example below demonstrates how to utilize both parallel tabu search and the genetic algorithm to solve an instance of a job shop schedule problem.
In the example, after initializing the static data from the three csv files, 4 tabu search processes are ran in parallel with each returning 5 solutions.
Next the resulting solutions from parallel tabu search are added to the initial population for the genetic algorithm. The ``solver.genetic_algorithm_time``
function adds randomly generated solutions to the initial population until it has ``population_size`` solutions.
Lastly, an excel file of the production schedule (i.e. solution) is created in the ``./example_output`` directory.

.. code-block:: python

    from JSSP.data import Data
    from JSSP.genetic_algorithm import GASelectionEnum

    # initialize data
    Data.initialize_data_from_csv('data/given_data/sequenceDependencyMatrix.csv',
                                  'data/given_data/machineRunSpeed.csv',
                                  'data/given_data/jobTasks.csv')

    # create solver
    solver = Solver()

    # run tabu seach
    solver.tabu_search_time(runtime=300, # seconds
                            num_processes=4,
                            num_solutions_per_process=5,
                            tabu_list_size=15,
                            neighborhood_size=250,
                            neighborhood_wait=0.1,
                            probability_change_machine=0.8,
                            reset_threshold=80
                            )

    # add all tabu search solutions to population
    population = []
    for ts_agent in solver.ts_agent_list:
        population += ts_agent.all_solutions

    # run genetic algorithm
    solution = solver.genetic_algorithm_time(runtime=300, # seconds
                                             population_size=100,
                                             selection_method_enum=GASelectionEnum.FITNESS_PROPORTIONATE,
                                             mutation_probability=0.1
                                             )

    # create an excel file of the schedule
    solution.create_schedule_xlsx_file('./example_output')

**Output**

`Schedule.xlsx <_static/Schedule.xlsx>`_

Alternatively you can run either the genetic algorithm or parallel tabu search for a certain number of iterations instead of time - just use ``solver.tabu_search_iter()`` and/or ``solver.genetic_algorithm_iter()``.

Gantt Chart Example
-------------------

The example below demonstrates how to create a gantt chart given a Solution.

.. code-block:: python

    # create a gantt chart html file
    solution.create_gantt_chart_html_file('./output', continuous=True)

    # alternatively you can plot a gantt chart in an ipython notebook
    solution.iplot_gantt_chart(continuous=True)

**Output**

.. raw:: html
   :file: _static/jsp_gantt_chart.html

Benchmark Example
-----------------

The example below demonstrates how to run a benchmark (i.e. create plots & statistical information for run) for both parallel tabu search and the genetic algorithm.

.. code-block:: python

    from JSSP.data import Data
    from JSSP.genetic_algorithm import GASelectionEnum
    from JSSP.solution import SolutionFactory

    # initialize fjs data
    Data.initialize_data_from_fjs('data/fjs_data/Brandimarte/Brandimarte_Mk10.fjs')

    # ts parameters
    ts_iterations = 300
    num_solutions_per_process = 20
    num_processes = 5
    tabu_list_size = 15
    neighborhood_size = 300
    neighborhood_wait = 0.15
    probability_change_machine = 0.8
    reset_threshold = 100

    # ga parameters
    ga_iterations = 500
    population_size = 400
    selection_method = GASelectionEnum.FITNESS_PROPORTIONATE
    mutation_probability = 0.2

    # create solver
    solver = Solver()

    # run tabu search
    solver.tabu_search_iter(ts_iterations,
                            num_solutions_per_process=num_solutions_per_process,
                            num_processes=num_processes,
                            tabu_list_size=tabu_list_size,
                            neighborhood_size=neighborhood_size,
                            neighborhood_wait=neighborhood_wait,
                            probability_change_machine=probability_change_machine,
                            verbose=True,
                            benchmark=True
                            )

    # add all ts solutions to population
    population = []
    for ts_agent in solver.ts_agent_list:
        population += ts_agent.all_solutions

    # add 25% spt solutions to population
    population += SolutionFactory.get_n_shortest_process_time_first_solution(int(.25 * population_size))

    # add 25% lpt solutions to population
    population += SolutionFactory.get_n_longest_process_time_first_solution(int(.25 * population_size))

    # add 25% random solutions to population
    population += SolutionFactory.get_n_solutions(int(.25 * population_size))

    # run genetic algorithm
    solver.genetic_algorithm_iter(ga_iterations,
                                  population=population,
                                  population_size=population_size,
                                  selection_method_enum=selection_method,
                                  mutation_probability=mutation_probability,
                                  selection_size=selection_size,
                                  verbose=True,
                                  benchmark=True
                                  )

    # output benchmark results
    solver.output_benchmark_results('./example_output', name='example_benchmark')

    # alternatively you can output the results in an ipython notebook
    solver.iplot_benchmark_results()

**Output**

::

    Running benchmark of TS
    Parameters:
    stopping_condition = 300
    time_condition = False
    num_solutions_per_process = 20
    num_processes = 5
    tabu_list_size = 15
    neighborhood_size = 300
    neighborhood_wait = 0.15
    probability_change_machine = 0.8
    reset_threshold = 100

    Initial Solution's makespans:
    [587, 611, 707, 709, 618]

    child TS process started. pid = 21060
    child TS process started. pid = 21061
    child TS process started. pid = 21062
    child TS process started. pid = 21063
    child TS process started. pid = 21064
    child TS process finished. pid = 21060
    child TS process finished. pid = 21061
    child TS process finished. pid = 21062
    child TS process finished. pid = 21063
    child TS process finished. pid = 21064
    Running benchmark of GA
    Parameters:
    stopping_condition = 100
    time_condition = False
    population_size = 400
    selection_method = _fitness_proportionate_selection
    mutation_probability = 0.2

To view the benchmark results see `example_benchmark <_static/example_benchmark/index.html>`_.

