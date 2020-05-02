import random
import unittest

from JSSP import data
from JSSP.exception import InfeasibleSolutionException
from JSSP.genetic_algorithm._ga_helpers import crossover
from JSSP.genetic_algorithm.ga import _tournament_selection, _fitness_proportionate_selection, _random_selection
from JSSP.solution import SolutionFactory
from tests.util import project_root, csv_data, get_files_with_suffix


class TestGASelection(unittest.TestCase):
    population_size = 100

    def test_tournament_selection(self):

        selection_size = 5
        population = [SolutionFactory(csv_data).get_solution() for _ in range(self.population_size)]

        while len(population) > selection_size:
            parent = _tournament_selection(population, 5)
            self.assertNotIn(parent, population)

    def test_fitness_proportionate_selection(self):

        population = [SolutionFactory(csv_data).get_solution() for _ in range(self.population_size)]

        while len(population) > 0:
            parent = _fitness_proportionate_selection(population)
            self.assertNotIn(parent, population)

    def test_random_selection(self):

        population = [SolutionFactory(csv_data).get_solution() for _ in range(self.population_size)]

        while len(population) > 0:
            parent = _random_selection(population)
            self.assertNotIn(parent, population)


class TestGACrossover(unittest.TestCase):

    def test_crossover(self):

        fjs_data = get_files_with_suffix(project_root / 'data/fjs_data', '.fjs')
        num_choices = 10
        probability_mutation = 0.5

        for i, fjs_instance in enumerate(random.choices(fjs_data, k=num_choices)):
            print(f"testing GA crossover function for fjs instance {fjs_instance} ({i + 1} of {num_choices})")
            instance_data = data.FJSData(fjs_instance)
            try:
                for _ in range(50):
                    parent1 = SolutionFactory(instance_data).get_solution()
                    parent2 = SolutionFactory(instance_data).get_solution()
                    crossover(parent1, parent2, probability_mutation,
                              instance_data.job_task_index_matrix, instance_data.usable_machines_matrix)
                    crossover(parent2, parent1, probability_mutation,
                              instance_data.job_task_index_matrix, instance_data.usable_machines_matrix)
            except InfeasibleSolutionException:
                self.fail("Infeasible child created")


if __name__ == '__main__':
    unittest.main()
