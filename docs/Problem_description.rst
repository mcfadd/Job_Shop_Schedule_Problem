Job Shop Schedule Problem Description
=====================================

The specific job shop schedule problem JSSP was made to solve is classified as the **Partial Flexible Job Shop Scheduling Problem with Sequence Dependent Setup Times**. 
For more general information on job shop scheduling problems see `https://en.wikipedia.org/wiki/Job_shop_scheduling`_.

Problem Description
-------------------

Given *m* machines with different run speeds and *n* jobs which have a varying number of tasks
that need to be completed, schedule the tasks from all jobs on the machines such that the
completion time (i.e. makespan) is minimized.

**Additional Information**

-  Each task has a set amount of pieces that needs to be processed for
   it to be complete.
-  The machines all have different run speeds.
-  Certain tasks can be run in parallel on these machines.
-  Each task has a sequence dependent setup time. |br| Setup times are
   encoded in `sequenceDependencyMatrix.csv`_.
-  If a task is the first to run on a machine there will be no setup
   time.

Constraints
-----------

-  On a machine, there can be no overlap in start and end times for any
   job-task.
-  Tasks within the same job cannot be started unless all other tasks
   within the same job with a sequence number less than the current task
   are complete.
-  Each task can only be run on certain machines.

Data
----

-  `jobTasks.csv`_: Contains an ordered list of all job-tasks and their
   sequence numbers, usable machines, and pieces.
-  `machineRunSpeed.csv`_: Contains a list of all machine IDs and run
   speeds.
-  `sequenceDependencyMatrix.csv`_: Contains a matrix of job-task setup
   times.

The rows of `sequenceDependencyMatrix.csv`_ represent the current job-task
in the form *j_t* where *j* is the job ID and *t* is the task ID.
The columns represent the previous job-task. A matrix value at index *(j_t, x_y)*
represents the setup time to schedule job-task *j_t* after job-task *x_y* on
a machine. Matrix values with the value -1 represent cases where the
current job-task (row) would never be scheduled after the previous job-task (column).

Solution Formulation
--------------------

A solution is formulated as a vector of operations where an operation is
a vector consisting of job ID, task ID, sequence number, and machine number.
The order of the operations (rows) determines the order in which the operations are scheduled.
For example, below is a feasible solution to a problem instance with 3 jobs, and 2 machines.
Each row represents an operation in the form [job id, task id, sequence number, machine number].

.. code:: python

   [[0, 0, 0, 0],
    [0, 1, 1, 1],
    [1, 0, 0, 1],
    [2, 0, 0, 0],
    [1, 1, 1, 0]]

Here is an example of an infeasible solution:

.. code:: python

   [[0, 1, 1, 0],
    [0, 0, 0, 0],
    [1, 0, 0, 1],
    [2, 0, 0, 0],
    [1, 1, 1, 0]]

The solution is infeasible because job 0, task 1 with sequence # = 1 is
scheduled on machine 0 before job 0, task 0 with sequence # = 0.

Solution Makespan
-----------------

To compute the makespan (cost) of a feasible solution,
take the max of [(total run time + total wait time + total setup
time) for each machine], where

-  run time = time required to process a task on a machine
-  wait time = time a machine has to wait for a task with sequence # < current task's sequence # to be processed
-  setup time = set up time before processing a task on a machine

For a more detailed description of how this works see the `source code`_.

.. _source code: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/JSSP/solution/makespan.pyx
.. _`https://en.wikipedia.org/wiki/Job_shop_scheduling`: https://en.wikipedia.org/wiki/Job_shop_scheduling
.. _jobTasks.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/data_set2/jobTasks.csv
.. _machineRunSpeed.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/machineRunSpeed.csv
.. _sequenceDependencyMatrix.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/sequenceDependencyMatrix.csv

.. |br| raw:: html

  <br/>
