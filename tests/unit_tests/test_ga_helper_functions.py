import os
import unittest

from JSSP.data import Data
from JSSP.genetic_algorithm.ga import _tournament_selection, _fitness_proportionate_selection, _random_selection
from JSSP.genetic_algorithm._ga_helpers import crossover
from JSSP.solution import SolutionFactory, InfeasibleSolutionException
from tests import project_root

"""
Test GA functions  

"""

population_size = 100


class TestGASelection(unittest.TestCase):

    def setUp(self) -> None:
        Data.initialize_data_from_csv(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def test_tournament_selection(self):

        selection_size = 5
        population = [SolutionFactory.get_solution() for _ in range(population_size)]

        while len(population) > selection_size:
            parent = _tournament_selection(population, 5)
            self.assertNotIn(parent, population)

    def test_fitness_proportionate_selection(self):

        population = [SolutionFactory.get_solution() for _ in range(population_size)]

        while len(population) > 0:
            parent = _fitness_proportionate_selection(population)
            self.assertNotIn(parent, population)

    def test_random_selection(self):

        population = [SolutionFactory.get_solution() for _ in range(population_size)]

        while len(population) > 0:
            parent = _random_selection(population)
            self.assertNotIn(parent, population)


def get_all_fjs_files(path):
    """
    Gets a list of all the absolute file paths of all the .fjs files that are below the path in the directory tree.

    :param path: The root path of the directory tree to search
    :returns: A list of all the absolute file paths of all the .fjs files
    """
    result = []
    for dirpath, dirs, files in os.walk(path):
        for filename in files:
            fname = os.path.join(dirpath, filename)
            if fname.endswith('.fjs'):
                result.append(fname)

    return result


class TestGACrossover(unittest.TestCase):

    def setUp(self) -> None:
        self.fjs_data = get_all_fjs_files(project_root + os.sep + 'data' + os.sep + 'fjs_data')
        self.total_instances = len(self.fjs_data)

    def test_crossover(self):

        probability_mutation = 0.5
        for i, fjs_instance in enumerate(self.fjs_data):
            print(f"testing GA crossover function for fjs instance {fjs_instance} ({i + 1} of {self.total_instances})")
            Data.initialize_data_from_fjs(fjs_instance)
            try:
                for _ in range(50):
                    parent1 = SolutionFactory.get_solution()
                    parent2 = SolutionFactory.get_solution()
                    crossover(parent1.operation_2d_array, parent2.operation_2d_array, probability_mutation,
                              Data.job_task_index_matrix, Data.usable_machines_matrix)
                    crossover(parent2.operation_2d_array, parent1.operation_2d_array, probability_mutation,
                              Data.job_task_index_matrix, Data.usable_machines_matrix)
            except InfeasibleSolutionException:
                self.fail("Infeasible child created")


if __name__ == '__main__':
    unittest.main()
