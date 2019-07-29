import csv
import os
import re

import numpy as np


class _Task:
    def __init__(self, job_id, task_id, sequence, usable_machines, pieces):
        """
        Initializes an instance of Task.

        :type job_id: int
        :param job_id: The job ID of this Task

        :type task_id: int
        :param task_id: The task ID of this Task

        :type sequence: int
        :param sequence: Sequence number of this Task

        :type usable_machines: 1d nparray
        :param usable_machines: Usable machines that this Task can be processed on

        :type pieces: int
        :param pieces: Number of pieces this Task has
        """
        self._jobId = job_id
        self._taskId = task_id
        self._sequence = sequence
        self._usable_machines = usable_machines
        self._pieces = pieces

    def get_job_id(self):
        return self._jobId

    def get_task_id(self):
        return self._taskId

    def get_sequence(self):
        return self._sequence

    def get_usable_machines(self):
        return self._usable_machines

    def get_pieces(self):
        return self._pieces

    def __eq__(self, other):
        return self._jobId == other.get_job_id() \
               and self._taskId == other.get_task_id() \
               and self._sequence == other.get_sequence() \
               and np.array_equal(self._usable_machines, other.get_usable_machines())  # note pieces are omitted

    def __str__(self):
        return f"[{self._jobId}, " \
            f"{self._taskId}, " \
            f"{self._sequence}, " \
            f"{self._usable_machines}, " \
            f"{self._pieces}]"


class _Job:
    def __init__(self, job_id):
        """
        Initializes an instance of Job.

        :type job_id: int
        :param job_id: The job Id of this Job
        """
        self._jobId = job_id
        self._tasks = []
        self._max_sequence = 0

    def set_max_sequence(self, max_sequence):
        self._max_sequence = max_sequence

    def get_max_sequence(self):
        return self._max_sequence

    def get_tasks(self):
        return self._tasks

    def get_task(self, task_id):
        return self._tasks[task_id]

    def get_job_id(self):
        return self._jobId

    def get_number_of_tasks(self):
        return len(self._tasks)

    def __eq__(self, other):
        return self._jobId == other.get_job_id() \
               and self._max_sequence == other.get_max_sequence() \
               and self._tasks == other.get_tasks()


class Data:
    """
    Static class containing all of the static data that is read in.
    """

    # uninitialized static fields
    fjs_instance = False
    sequence_dependency_matrix = None
    job_task_index_matrix = None
    usable_machines_matrix = None
    task_processing_times_matrix = None
    machine_speeds = None
    jobs = []
    total_number_of_jobs = 0
    total_number_of_tasks = 0
    total_number_of_machines = 0
    max_tasks_for_a_job = 0

    @staticmethod
    def reset_data():
        """
        Resets all of the static data.

        :returns: None
        """
        Data.fjs_instance = False
        Data.sequence_dependency_matrix = None
        Data.job_task_index_matrix = None
        Data.usable_machines_matrix = None
        Data.task_processing_times_matrix = None
        Data.machine_speeds = None
        Data.jobs = []
        Data.total_number_of_jobs = 0
        Data.total_number_of_tasks = 0
        Data.total_number_of_machines = 0
        Data.max_tasks_for_a_job = 0

    @staticmethod
    def initialize_data_from_csv(seq_dep_matrix_file, machine_speeds_file, job_tasks_file):
        """
        Initializes all of the static data from the csv files.

        :type seq_dep_matrix_file: str
        :param seq_dep_matrix_file: Path to the csv file containing the sequence dependency setup times

        :type machine_speeds_file: str
        :param machine_speeds_file: Path to the csv file containing all of the machine speeds

        :type job_tasks_file: str
        :param job_tasks_file: Path to the csv file containing all of the job-tasks

        :returns: None
        """
        Data.reset_data()
        Data._read_job_tasks_file(job_tasks_file)
        Data._read_sequence_dependency_matrix_file(seq_dep_matrix_file)
        Data._read_machine_speeds_file(machine_speeds_file)
        Data._initialize_derived_data()

    @staticmethod
    def initialize_data_from_fjs(input_file):
        """
        Initializes all of the static data from a fjs file.

        :type input_file: str
        :param input_file: Path to the fjs file to read the data from

        :returns: None
        """
        Data.reset_data()
        Data.fjs_instance = True
        # read .fjs input file
        with open(input_file, 'r') as fin:

            lines = [line for line in [l.strip() for l in fin] if line]  # read all non-blank lines
            first_line = [int(s) for s in re.sub(r'\s+', ' ', lines[0].strip()).split(' ')[:-1]]

            Data.total_number_of_jobs = first_line[0]  # get total num jobs
            Data.total_number_of_machines = first_line[1]  # get total num machines

            Data.total_number_of_tasks = 0
            Data.max_tasks_for_a_job = 0
            for line in lines[1:]:  # iterate over jobs
                # convert row (task data) to list of integers
                line = [int(s) for s in re.sub(r'\s+', ' ', line.strip()).split(' ')]

                num_tasks = int(line[0])
                Data.total_number_of_tasks += num_tasks
                Data.max_tasks_for_a_job = max(num_tasks, Data.max_tasks_for_a_job)

            # initialize matrices
            Data.task_processing_times_matrix = np.full((Data.total_number_of_tasks, Data.total_number_of_machines), -1,
                                                        dtype=np.float)
            Data.sequence_dependency_matrix = np.zeros((Data.total_number_of_tasks, Data.total_number_of_tasks),
                                                       dtype=np.intc)
            Data.usable_machines_matrix = np.empty((Data.total_number_of_tasks, Data.total_number_of_machines),
                                                   dtype=np.intc)
            Data.job_task_index_matrix = np.full((Data.total_number_of_jobs, Data.max_tasks_for_a_job), -1,
                                                 dtype=np.intc)

            task_index = 0
            for job_id, task_data in enumerate(lines[1:]):  # iterate over jobs

                # create and append new Job
                Data.jobs.append(_Job(job_id))

                task_id = 0
                sequence = 0

                # get all the Job's task data
                task_data = [int(s) for s in re.sub(r'\s+', ' ', task_data.strip()).split(' ')]

                i = 1
                while i < len(task_data):  # iterate over tasks

                    num_usable_machines = task_data[i]
                    usable_machines = []

                    for j in range(i + 1, i + num_usable_machines * 2 + 1,
                                   2):  # iterate over machines & run times for task

                        machine = task_data[j] - 1  # machines are zero indexed
                        runtime = task_data[j + 1]

                        usable_machines.append(machine)
                        Data.task_processing_times_matrix[task_index, machine] = runtime

                    Data.jobs[job_id].get_tasks().append(_Task(job_id, task_id, sequence, usable_machines, -1))
                    Data.usable_machines_matrix[task_index] = np.resize(np.array(usable_machines, dtype=np.intc),
                                                                        Data.total_number_of_machines)
                    Data.job_task_index_matrix[job_id, task_id] = task_index

                    task_id += 1
                    sequence += 1
                    task_index += 1
                    i += num_usable_machines * 2 + 1

                Data.jobs[job_id].set_max_sequence(sequence - 1)

    @staticmethod
    def _read_job_tasks_file(job_tasks_file):
        """
        Populates Data.jobs by reading the job_tasks_file csv file.

        :type job_tasks_file: str
        :param job_tasks_file: Path to the csv file that contains the job-task data

        :returns: None

        .. Note:: this function assumes that all of the jobs in job_tasks_file are in ascending order
        and are in the same order as in the sequence_dependency_matrix csv file.
        """
        prev_job_id = -1  # record previously seen job_id
        with open(job_tasks_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            for row in csv.reader(fin):
                # create task object
                task = _Task(
                    int(row[0]),  # job_id
                    int(row[1]),  # task_id
                    int(row[2]),  # seq num
                    np.array([int(x) for x in row[3][1:-1].strip().split(' ')], dtype=np.intc),  # usable machines
                    int(row[4])  # pieces
                )
                # create & append new job if we encounter job_id that has not been seen
                if task.get_job_id() != prev_job_id:
                    Data.jobs.append(_Job(task.get_job_id()))
                    prev_job_id = task.get_job_id()

                # update job's max sequence number
                if task.get_sequence() > Data.jobs[task.get_job_id()].get_max_sequence():
                    Data.jobs[task.get_job_id()].set_max_sequence(task.get_sequence())

                # append task to associated job.tasks list
                Data.jobs[task.get_job_id()].get_tasks().append(task)

    @staticmethod
    def _read_sequence_dependency_matrix_file(seq_dep_matrix_file):
        """
        Populates Data.sequence_dependency_matrix by reading the seq_dep_matrix_file csv file.

        :type seq_dep_matrix_file: str
        :param seq_dep_matrix_file: Path to the csv file that contains the sequence dependency matrix

        :returns: None

        .. Note:: this function assumes that all of the jobs in job_tasks_file are in ascending order
        and are in the same order as in the sequence_dependency_matrix csv file.

        """
        with open(seq_dep_matrix_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            Data.sequence_dependency_matrix = np.array(
                [[int(x) for x in row[1:]]
                 for row in csv.reader(fin)], dtype=np.intc)

    @staticmethod
    def _read_machine_speeds_file(machine_speeds_file):
        """
        Populates Data.machine_speeds by reading the machine_speeds_file csv file.

        :type machine_speeds_file: str
        :param machine_speeds_file: Path to the csv file that contains the machine run speeds

        :returns: None

        .. Note:: this function assumes that the machines are listed in ascending order.
        """
        with open(machine_speeds_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            Data.machine_speeds = np.array([int(row[1]) for row in csv.reader(fin)], dtype=np.float)

    @staticmethod
    def _initialize_derived_data():
        """
        Initializes derived data such as Data.dependency_matrix_index_encoding and Data.usable_machines_matrix

        :returns: None
        """
        Data.total_number_of_jobs = len(Data.jobs)
        Data.total_number_of_tasks = Data.sequence_dependency_matrix.shape[0]
        Data.max_tasks_for_a_job = max([x.get_number_of_tasks() for x in Data.jobs])
        Data.total_number_of_machines = Data.machine_speeds.shape[0]

        Data.job_task_index_matrix = np.full((Data.total_number_of_jobs, Data.max_tasks_for_a_job), -1, dtype=np.intc)
        Data.usable_machines_matrix = np.empty((Data.total_number_of_tasks, Data.total_number_of_machines),
                                               dtype=np.intc)
        Data.task_processing_times_matrix = np.full((Data.total_number_of_tasks, Data.total_number_of_machines), -1,
                                                    dtype=np.float)
        # process all job-tasks
        task_index = 0
        for job in Data.jobs:
            for task in job.get_tasks():

                # create mapping of (job id, task id) to index
                Data.job_task_index_matrix[job.get_job_id(), task.get_task_id()] = task_index

                # create row in Data.usable_machines_matrix
                Data.usable_machines_matrix[task_index] = np.resize(task.get_usable_machines(),
                                                                    Data.total_number_of_machines)

                # create row in Data.task_processing_times
                for machine in task.get_usable_machines():
                    Data.task_processing_times_matrix[task_index, machine] = task.get_pieces() / Data.machine_speeds[
                        machine]

                task_index += 1

    @staticmethod
    def print_data():
        """
        Prints all of the static data that was read in.

        :returns: None
        """
        print("total jobs =", Data.total_number_of_jobs)
        print("total tasks =", Data.total_number_of_tasks)
        print("total machines =", Data.total_number_of_machines)
        print("max tasks for a job =", Data.max_tasks_for_a_job)
        print("tasks:", end="\n\n")
        print("[jobId, taskId, sequence, usable_machines, pieces]", end="\n\n")
        for job in Data.jobs:
            for task in job.get_tasks():
                print(task)
        print()
        print("sequence_dependency_matrix:", Data.sequence_dependency_matrix.shape, end="\n\n")
        print(Data.sequence_dependency_matrix)
        print()
        print("dependency_matrix_index_encoding:", Data.job_task_index_matrix.shape, end="\n\n")
        print(Data.job_task_index_matrix)
        print()
        print("usable_machines_matrix:", Data.usable_machines_matrix.shape, end="\n\n")
        print(Data.usable_machines_matrix)
        print()
        print("task_processing_times:", Data.task_processing_times_matrix.shape, end="\n\n")
        print(Data.task_processing_times_matrix)
        print()
        if not Data.fjs_instance:
            print("machine_speeds:", Data.machine_speeds.shape, end="\n\n")
            print(Data.machine_speeds)

    @staticmethod
    def convert_fjs_to_csv(input_file, output_dir):
        """
        Converts a fjs file into three csv files, jobTasks.csv, machineRunSpeed.csv, and sequenceDependencyMatrix.csv,
        then it puts them in the output directory:

        :type input_file: str
        :param input_file: Path to the fjs file containing a flexible job shop schedule problem instance

        :type output_dir: str
        :param output_dir: Path to the directory to place the csv files into

        :returns: None
        """
        total_num_tasks = 0

        # create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # read .fjs input file and create jobTasks.csv
        with open(input_file, 'r') as fin:
            with open(output_dir + '/jobTasks.csv', 'w') as fout:
                fout.write("Job,Task,Sequence,Usable_Machines,Pieces\n")

                lines = [line for line in [l.strip() for l in fin] if line]
                line = [int(s) for s in re.sub(r'\s+', ' ', lines[0].strip()).split(' ')[:-1]]

                total_num_machines = line[1]

                # iterate over jobs
                for job_id, tasks in enumerate(lines[1:]):

                    # get the tasks data
                    task_data = [int(s) for s in re.sub(r'\s+', ' ', tasks.strip()).split(' ')]
                    total_num_tasks += task_data[0]
                    task_id = 0
                    sequence = 0

                    # iterate over tasks
                    i = 1
                    while i < len(task_data):

                        usable_machines = "["
                        output_line = f"{job_id},{task_id},{sequence},"
                        num_usable_machines = task_data[i]

                        for j in range(i + 1, i + num_usable_machines * 2 + 1, 2):
                            usable_machines += f"{task_data[j] - 1} "

                        output_line += usable_machines[:-1] + "]," + str(task_data[i + 2])
                        i += num_usable_machines * 2 + 1
                        task_id += 1
                        sequence += 1
                        fout.write(output_line + '\n')

        # create machineRunSpeed.csv
        with open(output_dir + '/machineRunSpeed.csv', 'w') as fout:
            fout.write("Machine,RunSpeed\n")
            for i in range(total_num_machines):
                fout.write(f"{i},1\n")

        # create sequenceDependencyMatrix.csv
        with open(output_dir + '/sequenceDependencyMatrix.csv', 'w') as fout:
            line = "0," * total_num_tasks + "0\n"
            for _ in range(total_num_tasks + 1):
                fout.write(line)
