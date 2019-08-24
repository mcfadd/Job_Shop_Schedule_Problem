Input Data
==========

The input data for partial flexible job shop schedule problem instances with sequence dependent setup times is encoded in three csv files.
The input data for flexible job shop schedule problem instances is encoded in a ``.fjs`` file.

To see the full example files, view them on `GitHub <https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data>`_.

FJS Instances with Sequence Dependent Setup Times
-------------------------------------------------

jobTasks.csv
~~~~~~~~~~~~
Contains a table of all job-tasks and their sequence numbers, usable machines, and pieces. |br|
**Job-tasks need to be in ascending order according to (job_id, task_id)** |br|

=== ==== ======== =============== ======
Job Task Sequence Usable_Machines Pieces
0   0    0        [4 5]           19116
0   1    1        [0 1 2 4 5 6 7] 7897
0   2    2        [0 1 2]         23430
0   3    2        [2 7]           21321
0   4    3        [0 3 6]         15368
0   5    3        [3 4]           23025
0   6    4        [2 3 4 6 7]     20115
1   0    0        [3 6]           22455
1   1    1        [3 6]           19165
1   2    1        [2]             8762
1   3    2        [5 7]           18824
1   4    2        [0 2]           9305
2   0    0        [0 3 4]         19368
2   1    1        [1 4 5 6]       20875
2   2    1        [1 2 4 6]       12997
2   3    1        [2 3 4 6]       6134
=== ==== ======== =============== ======

machineRunSpeed.csv
~~~~~~~~~~~~~~~~~~~
Contains a list of all machine IDs and run speeds. |br|

======= ========
Machine RunSpeed
0       123
1       58
2       76
3       83
4       111
5       100
6       98
7       151
======= ========

sequenceDependencyMatrix.csv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contains a matrix of job-task setup times. |br|
**Job-tasks need to be in ascending order according to (job_id, task_id)** |br|

=== === === === === === === === === === === === === === === ===
 .  0_0 0_1 0_2 0_3 0_4 0_5 0_6 1_0 1_1 1_2 1_3 1_4 2_0 2_1 2_2
0_0 -1  -1  -1  -1  -1  -1  -1  5   2   3   1   1   8   7   3
0_1 1   -1  -1  -1  -1  -1  -1  8   2   1   8   7   8   1   5
0_2 -1  7   -1  4   -1  -1  -1  8   8   6   3   2   8   6   1
0_3 -1  2   6   -1  -1  -1  -1  3   2   3   7   8   5   7   2
0_4 -1  -1  2   3   -1  2   -1  5   8   9   5   5   7   6   2
0_5 -1  -1  5   4   2   -1  -1  2   3   9   2   8   9   3   7
0_6 -1  -1  -1  -1  9   9   -1  5   1   5   3   8   5   5   6
1_0 7   7   8   1   6   5   8   -1  -1  -1  -1  -1  5   7   7
1_1 4   4   5   2   3   5   9   2   -1  4   -1  -1  1   8   9
1_2 7   4   8   9   5   9   3   7   7   -1  -1  -1  6   8   9
1_3 3   6   2   7   7   1   4   -1  8   1   -1  7   9   3   9
1_4 8   9   3   5   7   1   8   -1  9   6   5   -1  4   6   9
2_0 3   1   7   9   6   8   4   6   1   4   1   9   -1  -1  -1
2_1 3   2   4   3   6   8   1   7   7   2   1   7   6   -1  8
2_2 5   5   3   9   3   2   6   8   6   5   7   6   4   9   -1
=== === === === === === === === === === === === === === === ===

The rows of `sequenceDependencyMatrix.csv`_ represent the current job-task
in the form *j_t* where *j* is the job ID and *t* is the task ID.
The columns represent the previous job-task. A matrix value at index *(j_t, x_y)*
represents the setup time to schedule job-task *j_t* after job-task *x_y* on
a machine. Matrix values with the value -1 represent cases where the
current job-task (row) cannot be scheduled after the previous job-task (column).

FJS Instances
-------------

In the first line there are (at least) 2 numbers:

1. the number of jobs
2. the number of machines
3. the average number of machines per operation (optional)

Every row represents one job: |br|

* the first number is the number of operations of that job
* the second number (let's say k>=1) is the number of machines that can process the first operation; then according to k, there are k pairs of numbers (machine, processing time) that specify which are the machines and the processing times

**Example: Fisher and Thompson 6x6 instance, alternate name (mt06)**
::
        6   6   1
        6   1   3   1   1   1   3   1   2   6   1   4   7   1   6   3   1   5   6
        6   1   2   8   1   3   5   1   5   10  1   6   10  1   1   10  1   4   4
        6   1   3   5   1   4   4   1   6   8   1   1   9   1   2   1   1   5   7
        6   1   2   5   1   1   5   1   3   5   1   4   3   1   5   8   1   6   9
        6   1   3   9   1   2   3   1   5   5   1   6   4   1   1   3   1   4   1
        6   1   2   3   1   4   3   1   6   9   1   1   10  1   5   4   1   3   1


first row: 6 jobs, 6 machines, and 1 machine per operation  |br|
second row: job 1 has 6 operations; the first operation can be processed by 1 machine, that is machine 3 with processing time 1.

.. _jobTasks.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/data_set2/jobTasks.csv
.. _machineRunSpeed.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/machineRunSpeed.csv
.. _sequenceDependencyMatrix.csv: https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/given_data/sequenceDependencyMatrix.csv

.. |br| raw:: html

  <br/>
