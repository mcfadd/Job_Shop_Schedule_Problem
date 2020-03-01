Getting Started
===============

How to Install
--------------

1. Download the latest stable release of `JSSP <https://github.com/mcfadd/Job_Shop_Schedule_Problem/releases>`_ from GitHub
2. Run ``easy_install JSSP-<release>.<os>.egg`` |br|
If you downloaded the source code, ``cd`` to the directory where ``setup.py`` is and run ``pip install .``

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

    from JSSP.data import CSVData

    data = CSVData('sequenceDependencyMatrix.csv',
                   'machineRunSpeed.csv',
                   'jobTasks.csv')

To read in a flexible job shop schedule problem instance (i.e. ``.fjs`` file), run the following:

.. code-block:: python

    from JSSP.data import FJSData

    data = FJSData('Brandimarte_Mk10.fjs')

Optimization
~~~~~~~~~~~~

To run an optimization algorithm first create a ``Solver`` instance:

.. code-block:: python

    from JSSP.solver import Solver

    solver = Solver(data)

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

**Note:** See the `Solver module <api/JSSP.html#module-JSSP.solver>`_ for more optimization functions and parameter options.

Output
~~~~~~

Now that you have a Solution object run the following to produce a production schedule (excel file):

.. code-block:: python

    import datetime

    solution.create_schedule_xlsx_file(output_path='./Schedule.xlsx',
                                       start_date=datetime.date.today(),
                                       start_time=datetime.time(8, 0),
                                       end_time=datetime.time(20, 0))

Below is only a portion of the produced ``Schedule.xlsx``. |br|
To view the full schedule `download it <_static/Schedule.xlsx>`_.

==========  =================== =================== ==========  =================== ===================
Machine 0                                           Machine 1
Makespan =  15 days, 19:24:51                       Makespan =  9 days, 19:05:14
Job_Task    Start               End                 Job_Task    Start               End
48_0 setup  2020-02-29 08:00:00	2020-02-29 08:00:00 28_1 setup	2020-02-29 08:00:00 2020-02-29 08:00:00
48_0 run    2020-02-29 08:00:00	2020-02-29 10:20:36 28_1 run	2020-02-29 08:00:00 2020-02-29 10:40:15
4_2 setup   2020-02-29 10:20:36	2020-02-29 10:21:36 19_0 setup	2020-02-29 10:40:15 2020-02-29 10:45:15
4_2 run	    2020-02-29 10:21:36	2020-02-29 11:23:04 19_0 run	2020-02-29 10:45:15 2020-02-29 17:33:45
11_2 setup  2020-02-29 11:23:04	2020-02-29 11:24:04 40_0 setup	2020-03-01 17:33:45 2020-03-01 17:33:45
11_2 run    2020-02-29 11:24:04	2020-02-29 13:18:12 40_0 run	2020-03-01 17:33:45 2020-03-01 23:11:31
31_0 setup  2020-02-29 13:18:12	2020-02-29 13:21:12 30_0 setup	2020-03-03 23:11:31 2020-03-03 23:11:31
31_0 run    2020-02-29 13:21:12	2020-02-29 16:33:53 30_0 run	2020-03-03 23:11:31 2020-03-04 01:17:44
8_0 setup   2020-02-29 16:33:53	2020-02-29 16:34:53 4_0 setup	2020-03-04 01:17:44 2020-03-04 01:18:44
8_0 run	    2020-02-29 16:34:53	2020-02-29 17:54:21 4_0 run     2020-03-04 01:18:44 2020-03-04 02:47:17
10_0 setup  2020-02-29 17:54:21	2020-02-29 17:56:21 10_1 setup	2020-03-04 02:47:17 2020-03-04 02:48:17
10_0 run    2020-02-29 17:56:21	2020-02-29 19:13:43 10_1 run	2020-03-04 02:48:17 2020-03-04 05:36:09
49_1 setup  2020-03-01 19:13:43	2020-03-01 19:13:43 45_1 setup	2020-03-04 05:36:09 2020-03-04 05:37:09
49_1 run    2020-03-01 19:13:43	2020-03-01 22:25:26 45_1 run	2020-03-04 05:37:09 2020-03-04 07:08:35
32_1 setup  2020-03-03 22:25:26	2020-03-03 22:25:26 37_3 setup	2020-03-04 07:08:35 2020-03-04 07:11:35
32_1 run    2020-03-03 22:25:26	2020-03-03 23:45:17 37_3 run	2020-03-04 07:11:35 2020-03-04 08:46:16
25_0 setup  2020-03-05 23:45:17	2020-03-05 23:45:17 29_0 setup	2020-03-04 08:46:16 2020-03-04 08:47:16
25_0 run    2020-03-05 23:45:17	2020-03-06 02:39:25 29_0 run	2020-03-04 08:47:16 2020-03-04 10:29:46
13_0 setup  2020-03-06 02:39:25	2020-03-06 02:40:25 44_1 setup	2020-03-04 10:29:46 2020-03-04 10:32:46
13_0 run    2020-03-06 02:40:25	2020-03-06 05:01:55 44_1 run	2020-03-04 10:32:46 2020-03-04 13:39:18
28_3 setup  2020-03-06 05:01:55	2020-03-06 05:05:55 6_0 setup	2020-03-04 13:39:18 2020-03-04 13:43:18
28_3 run    2020-03-06 05:05:55	2020-03-06 07:01:30 6_0 run     2020-03-04 13:43:18 2020-03-04 16:42:47
5_3 setup   2020-03-06 07:01:30	2020-03-06 07:02:30 28_4 setup	2020-03-05 16:42:47 2020-03-05 16:42:47
5_3 run	    2020-03-06 07:02:30	2020-03-06 09:00:23 28_4 run	2020-03-05 16:42:47 2020-03-05 20:44:03
9_1 setup   2020-03-06 09:00:23	2020-03-06 09:01:23 12_2 setup	2020-03-07 20:44:03 2020-03-07 20:44:03
9_1 run	    2020-03-06 09:01:23	2020-03-06 10:35:41 12_2 run	2020-03-07 20:44:03 2020-03-08 00:39:12
22_1 setup  2020-03-06 10:35:41	2020-03-06 10:36:41 48_4 setup	2020-03-08 00:39:12 2020-03-08 00:40:12
22_1 run    2020-03-06 10:36:41	2020-03-06 12:06:51 48_4 run	2020-03-08 00:40:12 2020-03-08 03:07:43
==========  =================== =================== ==========  =================== ===================

.. |br| raw:: html

  <br/>
