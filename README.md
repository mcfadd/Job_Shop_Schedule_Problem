# Job Shop Schedule Problem (JSSP)

This problem was given to us in a mathematics course titled *Math 490 Preparation for Industrial Careers: Solving Industrial and Applied Problems in Teams* (sponsered by [PIC Math](https://www.maa.org/programs-and-communities/professional-development/pic-math)) at The University of Wisconsin - Milwauikee.

**Team**  
[Matthew McFadden](https://github.com/mcfadd)  
[Jessica Wolfson](https://github.com/JFWolfson)  
[Maddie Kenney](https://github.com/MaddieKenney)  
[Anthony Valdez ](https://github.com/avaldez96)  

## Problem

The specific JSSP problem this program attempts to solve is classified as the  
**Partial Flexible Job Shop Scheduling Problem With Sequence Dependent Setup Times**  
For more information see https://en.wikipedia.org/wiki/Job_shop_scheduling.

**Description**

Given m machines with different run speeds and n jobs which have a varying number of tasks that need to be completed, create a program that schedules the tasks from all jobs on the machines such that the completion time (i.e. make span) is minimized.

**Additional Information**  
* Each Task has a set amount of pieces that needs to be processed for the task to be complete.
* The machines all have different run speeds.
* Certain tasks can be run in parallel on these machines.
* Each task has a sequence dependent setup time. Setup times are encoded in sequenceDependencyMatrix.csv, where the columns represent the preceding job task, and the rows represent the current job task.
* If a task is the first to run on a machine there will be no setup time.

**Constraints**  
* On a machine, there can be no overlap in start and end times for any job task.
* Tasks within the same job cannot be started unless all other tasks within the same job with a sequence number less than the current task are complete.
* Each task can only be run on certain machines.

**Data**  
* [jobTasks.csv](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/data_set2/jobTasks.csv)
* [machineRunSpeed.csv](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/data_set2/machineRunSpeed.csv)
* [sequenceDependencyMatrix.csv](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/data/data_set2/sequenceDependencyMatrix.csv)

## Solution Formulation

We formulate a solution as a list of operations where and operation consists of JobId, taskId, sequence number, and machine for the task to run on. The order of the list determines the order in which the operations are scheduled.

For example, below is a feasible solution to a problem instance with 3 jobs, and 2 machine.  
Each row represents an operation in the form [jobId, taskId, sequence number, machine number, pieces].  

```python
[[0, 0, 0, 0, 10],
 [0, 1, 1, 1, 5],
 [1, 0, 0, 1, 8],
 [2, 0, 0, 0, 8],
 [1, 1, 1, 0, 5]]
```

Here is an example of an infeasible solution:

```python
[[0, 1, 1, 0, 5],
 [0, 0, 0, 0, 10],
 [1, 0, 0, 1, 8],
 [2, 0, 0, 0, 8],
 [1, 1, 1, 0, 5]]
```

The solution is infeasible because job 0, task 1 with sequence = 1 is scheduled on machine 0 before job 0, task 0 with sequence = 0.

To calculate the make span of a feasible solution we calculate the max of (total run time + total wait time + total setup time) for each machine, where

* run time = task pieces / machine speed
* wait time = time a machine has to wait for a task with sequence < current task's sequence to be processed 
* setup time = set up time before processing the current task


To produce a schedule for each machine given a feasible solution, we iterate over the solution and add each Job-Task to a queue for the machine specified in the operation.

## Program

JSSP is only supported on unix type operating systems.  
Make sure you have the following packages installed:

Python 3.6  
python3-dev   
pip  
gcc

(These can be installed with a package manager such as apt, yum, brew, etc.)

### How to Install:
Clone this repository:
```
git clone https://github.com/mcfadd/Job_Shop_Schedule_Problem
```
Then navigate to the cloned directory where setup.py is located.  
Now run the following:
```
pip install -r requirements.txt
python setup.py build_ext
pip install .
```

### How to Use:

JSSP can be ran from the command line or it can be imported into a python project/ipython notebook (see [Example.ipynb](https://github.com/mcfadd/Job_Shop_Schedule_Problem/blob/master/Example.ipynb)).
As of right now the command line program only runs parallel Tabu Search. 

**Important Note:**

Job-Tasks in jobTasks.csv and sequenceDependencyMatrix.csv need to be in ascending order according to their (job_id, task_id).  
(see csv files in [data](https://github.com/mcfadd/Job_Shop_Schedule_Problem/tree/master/data/data_set2) for reference)


When you install JSSP a command called `jssp` is put into your bin.  
Below is the command line usage:

```bash
jssp [-h] [-pb] [-b initial_solution.pkl] [-v] 
        [-o output] [-np num_processes] [-ts tabu_list_size] 
        [-ns neighborhood_size] [-nw neighborhood_wait] 
        [-p prob_change_machine] -rt runtime data
```

<br>

#### Arguments  

| Arg | Description |
| --- | --- |
| -h | Prints a help message |
| -pb | Spawns a progress bar |
| -b | Runs a benchmark of the program starting with initial_solution.pkl. <br> To generate random initial solutions use `-b na` |
| -v | Runs in verbose mode |
| -o | Directory where output is placed (default = ~/jssp_output) |
| -np | Number of processes to run tabu search search in parallel (default = 4) |
| -ts | Tabu list size (default = 50) |
| -ns | Neighborhood size (default = 300) |
| -nw | Maximum time in seconds to wait while generating a neighborhood (default = 0.1) |  
| -p |  Probability of changing an operation's machine when generating a neighbor (default = 0.8) |
| -rt | Runtime in seconds |
| data | Directory containing the csv files: <br> jobTasks.csv <br> machineRunSpeed.csv <br> sequenceDependencyMatrix.csv|  


**Example**  

```bash
jssp -pb -np 4 -rt 300 -ns 350 -nw 0.15 ./data/data_set2
```

## Program Design

Below is a basic high-level flow digram describing the design of the program.

![Flow Diagram](diagrams/Flow_Diagram.png)  

