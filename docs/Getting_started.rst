Getting Started
===============

How to Install
--------------

1. Download the latest stable release of `JSSP <https://github.com/mcfadd/Job_Shop_Schedule_Problem/releases>`_ from GitHub
2. Run ``easy_install JSSP-<release>.<os>.egg`` |br| If you downloaded the source code, ``cd`` to the directory where ``setup.py`` is and run ``pip install .``

If you get an error about ``python.h`` not being found try installing `python3-dev <https://stackoverflow.com/questions/31002091/what-is-python-dev-package-used-for>`_.

How to Use
----------

After installation, JSSP can imported as a normal python module.

**Important Note** |br|
Job-tasks in jobTasks.csv and sequenceDependencyMatrix.csv need to be in ascending order according to (job_id, task_id). |br|
(see the csv files on `GitHub <https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/given_data>`_ for a reference)

For more information on the input data see the `Input Data <Input_data.html>`_ section.

Read Data
~~~~~~~~~

To read in a partial flexible job shop schedule problem instance with sequence dependent setup times (i.e. ``.csv`` files), run the following:

.. code-block:: python

    from JSSP.data import Data

    Data.initialize_data_from_csv('sequenceDependencyMatrix.csv',
                                  'machineRunSpeed.csv',
                                  'jobTasks.csv')

To read in a flexible job shop schedule problem instance (i.e. ``.fjs`` file), run the following:

.. code-block:: python

    from JSSP.data import Data

    Data.initialize_data_from_fjs('Brandimarte_Mk10.fjs')

Optimization
~~~~~~~~~~~~

To run an optimization algorithm first create a ``Solver`` instance:

.. code-block:: python

    from JSSP.solver import Solver

    solver = Solver()

Next, run the optimization algorithm:

.. code-block:: python

    # runs 4 parallel tabu search processes for 500 iterations each
    solution = solver.tabu_search_iter(iterations=500,
                                       num_processes=4,
                                       tabu_list_size=15,
                                       neighborhood_size=250,
                                       neighborhood_wait=0.1,
                                       probability_change_machine=0.8,
                                       reset_threshold=100,
                                       )

**Note:** See the `Solver module <doc/JSSP.html#module-JSSP.solver>`_ for more optimization functions and parameter options.

Output
~~~~~~

Now that you have a Solution object run the following to produce a production schedule (excel file):

.. code-block:: python

    import datetime

    solution.create_schedule_xlsx_file(output_dir='./example_output',
                                       start_time=datetime.time(8, 0),
                                       end_time=datetime.time(20, 0),
                                       filename='Schedule')

Below is only a portion of the produced ``Schedule.xlsx``. |br|
To view the full schedule `download it <_static/Schedule.xlsx>`_.

============= =============== =============== ============= =============== ===============
Machine 0                                     Machine 1
Makespan =    5d 10h 12m                      Makespan =    7d 6h 7m
Total Wait =  0d 2h 53m                       Total Wait =  0d 0h 0m
Total Setup = 0d 1h 56m                       Total Setup = 0d 1h 1m
Job_Task      Start           End             Job_Task      Start           End
25_1 setup    day 1  08:00:00 day 1  08:00:00 27_0 setup    day 1  08:00:00 day 1  08:00:00
25_1 run      day 1  08:00:00 day 1  08:52:00 27_0 run      day 1  08:00:00 day 1  13:22:00
2_0 setup     day 1  08:52:00 day 1  08:54:00 41_0 setup    day 1  13:22:00 day 1  13:26:00
2_0 run       day 1  08:54:00 day 1  11:31:00 41_0 run      day 1  13:26:00 day 1  16:11:00
25_0 setup    day 1  11:31:00 day 1  11:36:00 2_1 setup     day 2  08:00:00 day 2  08:03:00
25_0 run      day 1  11:36:00 day 1  14:30:00 2_1 run       day 2  08:03:00 day 2  14:02:00
36_1 setup    day 1  14:30:00 day 1  14:35:00 39_0 setup    day 2  14:02:00 day 2  14:07:00
36_1 run      day 1  14:35:00 day 1  15:44:00 39_0 run      day 2  14:07:00 day 2  18:26:00
31_0 setup    day 1  15:44:00 day 1  15:51:00 49_0 setup    day 3  08:00:00 day 3  08:04:00
31_0 run      day 1  15:51:00 day 1  19:04:00 49_0 run      day 3  08:04:00 day 3  12:58:00
47_0 setup    day 2  08:00:00 day 2  08:06:00 4_0 setup     day 3  12:58:00 day 3  13:02:00
47_0 run      day 2  08:06:00 day 2  11:02:00 4_0 run       day 3  13:02:00 day 3  14:31:00
32_1 setup    day 2  11:02:00 day 2  11:03:00 20_1 setup    day 3  14:31:00 day 3  14:36:00
32_1 run      day 2  11:03:00 day 2  12:22:00 20_1 run      day 3  14:36:00 day 3  17:25:00
33_1 setup    day 2  12:22:00 day 2  12:24:00 40_0 setup    day 4  08:00:00 day 4  08:02:00
33_1 run      day 2  12:24:00 day 2  15:44:00 40_0 run      day 4  08:02:00 day 4  13:39:00
18_2 setup    day 2  15:44:00 day 2  15:48:00 6_0 setup     day 4  13:39:00 day 4  13:42:00
18_2 run      day 2  15:48:00 day 2  18:03:00 6_0 run       day 4  13:42:00 day 4  16:42:00
13_0 setup    day 3  08:00:00 day 3  08:03:00 2_4 setup     day 5  08:00:00 day 5  08:02:00
13_0 run      day 3  08:03:00 day 3  10:24:00 2_4 run       day 5  08:02:00 day 5  13:56:00
4_2 setup     day 3  10:24:00 day 3  10:25:00 24_2 setup    day 5  13:56:00 day 5  14:00:00
4_2 run       day 3  10:25:00 day 3  11:26:00 24_2 run      day 5  14:00:00 day 5  19:45:00
28_3 setup    day 3  11:26:00 day 3  11:31:00 28_4 setup    day 6  08:00:00 day 6  08:02:00
28_3 run      day 3  11:31:00 day 3  13:27:00 28_4 run      day 6  08:02:00 day 6  12:03:00
15_0 setup    day 3  13:27:00 day 3  13:33:00 14_5 setup    day 6  12:03:00 day 6  12:08:00
============= =============== =============== ============= =============== ===============

.. |br| raw:: html

  <br/>
