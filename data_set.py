import csv


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


class Operation:

    def __init__(self, task, machine):
        """
        Constructs an Operation object composed of a task and a machine for the task to run on.

        :param task: The Task this Operation will perform.
        :param machine: The machine this Operation will perform it's task on.
        """
        self._task = task
        self._machine = machine

    def get_task(self):
        return self._task

    def get_machine(self):
        return self._machine

    def set_machine(self, machine_id):
        self._machine = machine_id

    def get_usable_machines(self):
        return self.get_task().get_usable_machines()

    def __eq__(self, other_operation):
        return (self.get_machine() == other_operation.get_machine()
                and self.get_task() == other_operation.get_task())

    def pprint(self):
        print(f"[{self._task.get_job_id()}, "
              f"{self._task.get_task_id()}, "
              f"{self._task.get_sequence()}, "
              f"{self._machine}]")


class Data:
    """
    This static class contains all of the data that is read in from the csv files.
    """

    sequence_dependency_matrix = []
    dependency_matrix_index_encoding = {}
    jobs = {}
    machine_speeds = []

    @staticmethod
    def read_job_tasks_file(job_tasks_file):
        """
        Populates Data.jobs by reading the job_tasks_file csv file.
        Additionally, this function populates Data.dependency_matrix_index_encoding
        by creating a mapping of (job_id, task_id) : index for each task (row).

        Note: this function assumes that all of the jobs in job_tasks_file are in ascending order
         and are in the same order as in the sequence_dependency_matrix csv file.

        :param job_tasks_file: The csv file that contains the job-task data.
        :return: None
        """
        prev_job_id = -1  # record previously seen job
        index = 0  # used for mapping (job_id, task_id) : index
        with open(job_tasks_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            for row in csv.reader(fin):
                # create task object
                tmp_task = Task(
                    int(row[0]),
                    int(row[1]),
                    int(row[2]),
                    [int(x) for x in row[3][1:-1].split(' ')],
                    int(row[4])
                )
                # create & append new job if we encounter job_id that has not been seen
                if tmp_task.get_job_id() != prev_job_id:
                    Data.jobs[tmp_task.get_job_id()] = Job(tmp_task.get_job_id())
                    prev_job_id = tmp_task.get_job_id()

                # update Job's max sequence number
                if tmp_task.get_sequence() > Data.jobs[tmp_task.get_job_id()].get_max_sequence():
                    Data.jobs[tmp_task.get_job_id()]._max_sequence = tmp_task.get_sequence()

                # append task to associated job.tasks list
                Data.jobs[tmp_task.get_job_id()]._tasks.append(tmp_task)

                # add mapping task : index to dependencyMatrixIndexEncoding dictionary
                Data.dependency_matrix_index_encoding[(tmp_task.get_job_id(), tmp_task.get_task_id())] = index
                index += 1

    @staticmethod
    def read_sequence_dependency_matrix_file(seq_dep_matrix_file):
        """
        Populates Data.sequence_dependency_matrix by reading the seq_dep_matrix_file csv file.

        :param seq_dep_matrix_file: The csv file that contains the sequence dependency matrix.
        :return: None
        """
        with open(seq_dep_matrix_file) as fin:
            # skip headers (i.e. first row in csv file)
            next(fin)
            for row in csv.reader(fin):
                Data.sequence_dependency_matrix.append([int(x) for x in row[1:]])

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
            for row in csv.reader(fin):
                Data.machine_speeds.append(int(row[1]))

    @staticmethod
    def get_setup_time(prev_task, cur_task):
        """
        Gets the set up time required before processing cur_task after prev_task is complete.
        The set up time is encoded in Data.sequence_dependency_matrix.

        :param prev_task: The previous task.
        :param cur_task: The current task.
        :return: set up time required before processing cur_task after prev_task is complete.
        """
        return Data.sequence_dependency_matrix[Data.dependency_matrix_index_encoding[prev_task]][
            Data.dependency_matrix_index_encoding[cur_task]]

    @staticmethod
    def get_job(job_id):
        return Data.jobs[job_id]

    @staticmethod
    def get_machine_speed(machine_id):
        return Data.machine_speeds[machine_id]

    @staticmethod
    def get_number_of_machines():
        return len(Data.machine_speeds)

    @staticmethod
    def get_number_of_jobs():
        return len(Data.jobs)

    @staticmethod
    def get_number_of_tasks():
        return len(Data.dependency_matrix_index_encoding)

    @staticmethod
    def print_data():
        print("job_tasks:\n")
        print("  [jobId, taskId, sequence, usable_machines, pieces]\n")
        for job in Data.jobs.values():
            for task in job._tasks:
                print("  ", end="")
                task.pprint()

        print("\nsequence_dependency_matrix:\n")
        for row in Data.sequence_dependency_matrix:
            print("  ", end="")
            print(row)

        print("\ndependency_matrixIndex_encoding:\n")
        print("  (jobId, taskId) : index\n")
        for key in Data.dependency_matrix_index_encoding:
            print("  ", end="")
            print(f"({key.get_job_id()}, {key.get_task_id()}) : {Data.dependency_matrix_index_encoding[key]}")

        print("\nmachine_speeds:\n")
        print("  machine : speed\n")
        for machine, speed in enumerate(Data.machine_speeds):
            print("  ", end="")
            print(f"{machine} : {speed}")

    @staticmethod
    def read_data_from_files(seq_dep_matrix_file, machine_speeds_file, job_tasks_file):
        Data.read_sequence_dependency_matrix_file(seq_dep_matrix_file)
        Data.read_machine_speeds_file(machine_speeds_file)
        Data.read_job_tasks_file(job_tasks_file)
