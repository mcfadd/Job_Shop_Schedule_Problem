import csv
import os
import re
import shutil
import numpy as np


class Task:

    def __init__(self, job_id, task_id, sequence, usable_machines, pieces):
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

    def pprint(self):
        print(f"[{self._jobId}, "
              f"{self._taskId}, "
              f"{self._sequence}, "
              f"{self._usable_machines}, "
              f"{self._pieces}]")


class Job:

    def __init__(self, job_id):
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


class Data:
    """
    This static class contains all of the static data that is read in.
    """

    # uninitialized static fields
    sequence_dependency_matrix = None
    dependency_matrix_index_encoding = None
    usable_machines_matrix = None
    machine_speeds = None
    jobs = []
    total_number_of_jobs = 0
    total_number_of_tasks = 0
    total_number_of_machines = 0
    max_tasks_for_a_job = 0

    @staticmethod
    def initialize_data_from_csv(seq_dep_matrix_file, machine_speeds_file, job_tasks_file):
        """
        This function initializes all of the static data from the csv files.

        :param seq_dep_matrix_file: csv file containing the sequence dependency setup times
        :param machine_speeds_file: csv file containing all of the machine speeds
        :param job_tasks_file: csv file containg all of the job-tasks
        :return: None
        """
        Data.read_job_tasks_file(job_tasks_file)
        Data.read_sequence_dependency_matrix_file(seq_dep_matrix_file)
        Data.read_machine_speeds_file(machine_speeds_file)
        Data._initialize_derived_data()

    @staticmethod
    def initialize_data_from_fjs(input_file):
        """
        This function initializes all of the static data from a .fjs file

        :param input_file: The .fjs file to read the data from
        :return:
        """
        tmp_dir = f"{os.path.dirname(os.path.realpath(__file__))}/tmp"

        # convert .fjs to csv then initialize
        Data.convert_fjs_to_csv(input_file, tmp_dir)
        Data.initialize_data_from_csv(tmp_dir + '/sequenceDependencyMatrix.csv',
                                      tmp_dir + '/machineRunSpeed.csv',
                                      tmp_dir + '/jobTasks.csv')

        # remove temporary directory
        shutil.rmtree(f"{os.path.dirname(os.path.realpath(__file__))}/tmp", ignore_errors=True)

    @staticmethod
    def read_job_tasks_file(job_tasks_file):
        """
        Populates Data.jobs by reading the job_tasks_file csv file.

        Note: this function assumes that all of the jobs in job_tasks_file are in ascending order
         and are in the same order as in the sequence_dependency_matrix csv file.

        :param job_tasks_file: The csv file that contains the job-task data.
        :return: None
        """
        Data.jobs = []
        prev_job_id = -1  # record previously seen job_id
        with open(job_tasks_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            for row in csv.reader(fin):
                # create task object
                task = Task(
                    int(row[0]),  # job_id
                    int(row[1]),  # task_id
                    int(row[2]),  # seq num
                    np.array([int(x) for x in row[3][1:-1].strip().split(' ')], dtype=np.intc),  # usable machines
                    int(row[4])  # pieces
                )
                # create & append new job if we encounter job_id that has not been seen
                if task.get_job_id() != prev_job_id:
                    Data.jobs.append(Job(task.get_job_id()))
                    prev_job_id = task.get_job_id()

                # update job's max sequence number
                if task.get_sequence() > Data.jobs[task.get_job_id()].get_max_sequence():
                    Data.jobs[task.get_job_id()].set_max_sequence(task.get_sequence())

                # append task to associated job.tasks list
                Data.jobs[task.get_job_id()].get_tasks().append(task)

    @staticmethod
    def read_sequence_dependency_matrix_file(seq_dep_matrix_file):
        """
        Populates Data.sequence_dependency_matrix by reading the seq_dep_matrix_file csv file.

        Note: this function assumes that all of the jobs in job_tasks_file are in ascending order
         and are in the same order as in the sequence_dependency_matrix csv file.

        :param seq_dep_matrix_file: The csv file that contains the sequence dependency matrix.
        :return: None
        """
        with open(seq_dep_matrix_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            Data.sequence_dependency_matrix = np.array(
                [[int(x) for x in row[1:]]
                 for row in csv.reader(fin)], dtype=np.intc)

    @staticmethod
    def read_machine_speeds_file(machine_speeds_file):
        """
        Populates Data.machine_speeds by reading the machine_speeds_file csv file.

        Note: this function assumes that the machines are listed in ascending order.

        :param machine_speeds_file: The csv file that contains the machine run speeds
        :return: None
        """
        with open(machine_speeds_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            Data.machine_speeds = np.array([int(row[1]) for row in csv.reader(fin)], dtype=np.float)

    @staticmethod
    def _initialize_derived_data():
        """
        Initializes derived data such as Data.dependency_matrix_index_encoding and Data.usable_machines_matrix

        :return: None
        """
        Data.total_number_of_jobs = len(Data.jobs)
        Data.total_number_of_tasks = Data.sequence_dependency_matrix.shape[0]
        Data.max_tasks_for_a_job = max([x.get_number_of_tasks() for x in Data.jobs])
        Data.total_number_of_machines = Data.machine_speeds.shape[0]
        Data.dependency_matrix_index_encoding = np.full((Data.total_number_of_jobs, Data.max_tasks_for_a_job), -1,
                                                        dtype=np.intc)
        Data.usable_machines_matrix = np.empty((Data.total_number_of_tasks, Data.total_number_of_machines),
                                               dtype=np.intc)
        index = 0
        for job in Data.jobs:
            for task in job.get_tasks():
                Data.dependency_matrix_index_encoding[job.get_job_id(), task.get_task_id()] = index
                Data.usable_machines_matrix[index] = np.resize(task.get_usable_machines(),
                                                               Data.total_number_of_machines)
                index += 1

    @staticmethod
    def get_job(job_id):
        return Data.jobs[job_id]

    @staticmethod
    def print_data():
        print("total jobs =", Data.total_number_of_jobs)
        print("total tasks =", Data.total_number_of_tasks)
        print("total machines =", Data.total_number_of_machines)
        print("max tasks for a job =", Data.max_tasks_for_a_job)
        print("tasks:", end="\n\n")
        print("[jobId, taskId, sequence, usable_machines, pieces]", end="\n\n")
        for job in Data.jobs:
            for task in job.get_tasks():
                task.pprint()
        print()
        print("sequence_dependency_matrix:", Data.sequence_dependency_matrix.shape, end="\n\n")
        print(Data.sequence_dependency_matrix)
        print()
        print("dependency_matrix_index_encoding:", Data.dependency_matrix_index_encoding.shape, end="\n\n")
        print(Data.dependency_matrix_index_encoding)
        print()
        print("usable_machines_matrix:", Data.usable_machines_matrix.shape, end="\n\n")
        print(Data.usable_machines_matrix)
        print()
        print("machine_speeds:", Data.machine_speeds.shape, end="\n\n")
        print(Data.machine_speeds)

    @staticmethod
    def convert_fjs_to_csv(input_file, output_dir):
        """
        This function converts a .fjs file into three csv files, jobTasks.csv, machineRunSpeed.csv, and sequenceDependencyMatrix.csv,
        then it puts them in the output directory:

        :param input_file: The .fjs file containing a flexible job shop schedule problem instance
        :param output_dir: The directory to place the csv files into
        :return: None
        """
        total_num_tasks = 0

        # create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        # read .fjs input file and create jobTasks.csv
        with open(input_file, 'r') as fin:
            with open(output_dir + '/jobTasks.csv', 'w') as fout:
                fout.write("Job,Task,Sequence,Usable_Machines,Pieces\n")

                lines = fin.readlines()
                line = [int(s) for s in re.sub(r'\s+', ' ', lines[0].strip()).split(' ')]

                total_num_mahines = line[1]

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
                        # print(output_line)

        # create machineRunSpeed.csv
        with open(output_dir + '/machineRunSpeed.csv', 'w') as fout:
            fout.write("Machine,RunSpeed\n")
            for i in range(total_num_mahines):
                fout.write(f"{i},1\n")

        # create sequenceDependencyMatrix.csv
        with open(output_dir + '/sequenceDependencyMatrix.csv', 'w') as fout:
            line = "0," * total_num_tasks + "0\n"
            for _ in range(total_num_tasks + 1):
                fout.write(line)
