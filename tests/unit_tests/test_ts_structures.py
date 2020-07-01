import unittest

from JSSP.solution import SolutionFactory
from JSSP.tabu_search.ts import _SolutionSet, _TabuList
from JSSP.util import Heap
from tests.util import csv_data


class TestTSStructures(unittest.TestCase):

    def test_solution_set_add(self):
        solution_set = _SolutionSet()

        # add a Solution
        solution_obj1 = SolutionFactory(csv_data).get_solution()
        solution_set.add(solution_obj1)

        # make sure Solution was added
        self.assertTrue(solution_obj1 in solution_set)
        self.assertEqual(solution_set.size, 1)

        # add another Solution
        solution_obj2 = SolutionFactory(csv_data).get_solution()
        solution_set.add(solution_obj2)

        # make sure last Solution was added
        self.assertTrue(solution_obj2 in solution_set)
        self.assertEqual(solution_set.size, 2)

    def test_solution_set_remove(self):
        solution_set = _SolutionSet()

        # add a Solution
        solution_obj1 = SolutionFactory(csv_data).get_solution()
        solution_set.add(solution_obj1)

        # make sure Solution was added
        self.assertTrue(solution_obj1 in solution_set)

        # remove the Solution
        solution_set.remove(solution_obj1)

        # make sure solution was removed
        self.assertFalse(solution_obj1 in solution_set)
        self.assertEqual(solution_set.size, 0)

    def test_tabu_list_enqueue(self):
        # add solutions to tabu list
        tabu_list = _TabuList()
        size = 100
        while tabu_list.solutions.size < size:
            sol = SolutionFactory(csv_data).get_solution()
            tabu_list.put(sol)
            self.assertTrue(sol in tabu_list)

        self.assertEqual(len(tabu_list), size)

    def test_tabu_list_dequeue(self):
        initial_solution = SolutionFactory(csv_data).get_solution()

        # build tabu_list and solutions list
        tabu_list = _TabuList()
        tabu_list.put(initial_solution)
        lst = [initial_solution]
        size = 100
        while tabu_list.solutions.size < size:
            solution_obj = SolutionFactory(csv_data).get_solution()
            tabu_list.put(solution_obj)
            lst.append(solution_obj)

        # check that solutions are dequeued in correct order
        i = 0
        while 0 < tabu_list.solutions.size:
            self.assertTrue(lst[i] in tabu_list)
            self.assertEqual(lst[i], tabu_list.get())
            self.assertFalse(lst[i] in tabu_list)
            i += 1

    def test_max_heap(self):

        heap_size = 50
        heap = Heap(max_heap=True)
        for _ in range(heap_size):
            heap.push(SolutionFactory(csv_data).get_solution())

        self.assertEqual(heap_size, len(heap), f"The max heap size should be equal to {heap_size}")

        while len(heap) > 1:
            sol = heap.pop()
            self.assertGreaterEqual(sol, heap[0],
                                    "The max heap solutions should be organized with the worst solutions (greatest) at the top")


if __name__ == '__main__':
    unittest.main()
