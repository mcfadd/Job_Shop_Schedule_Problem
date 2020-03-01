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

.. _`https://en.wikipedia.org/wiki/Job_shop_scheduling`: https://en.wikipedia.org/wiki/Job_shop_scheduling
.. _sequenceDependencyMatrix.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/sequenceDependencyMatrix.csv

.. |br| raw:: html

  <br/>
