from random import randint
from data_set import Operation, Data
from makespan import Solution


def generate_feasible_solution():
    """
    Generates a random feasible solution.

    :return: a random feasible solution
    """

    # this will be replaced by what Jessica and Anthony come up with
    operation_list = []
    for job in range(Data.get_number_of_jobs()):
        for task in range(Data.jobs[job].get_number_of_tasks()):
            usable_machines = Data.jobs[job].get_task(task).get_usable_machines()
            operation_list.append(Operation(task=Data.jobs[job].get_task(task),
                                            machine=usable_machines[randint(0, len(usable_machines) - 1)]))

    return Solution(operation_list)


def get_test_operation():
    """
    This function is only for testing purposes.
    It returns a consistent feasible solution for the smallest problem instance in the data directory.

    :return: Consistent feasible solution
    """
    return Solution([Operation(task=Data.get_job(0).get_task(0), machine=0),
                     Operation(task=Data.get_job(0).get_task(1), machine=1),
                     Operation(task=Data.get_job(1).get_task(0), machine=1),
                     Operation(task=Data.get_job(2).get_task(0), machine=0),
                     Operation(task=Data.get_job(1).get_task(1), machine=0),
                     ])
