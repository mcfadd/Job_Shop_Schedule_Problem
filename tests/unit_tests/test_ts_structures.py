import os
import unittest

from JSSP import solution
from JSSP.data import Data
from JSSP.tabu_search.ts import _SolutionSet, _TabuList, _MaxHeap
from tests import project_root

"""
Test the following:

1. ts.SolutionSet.add() function
2. ts.SolutionSet.remove() function
3. ts.SolutionSet.contains() function
4. ts.TabuList.enqueue() function
5. ts.TabuList.dequeue() function

"""


class TestTSStructures(unittest.TestCase):

    def setUp(self) -> None:
        Data.initialize_data_from_csv(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def test_solution_set_add(self):
        solution_set = _SolutionSet()

        # add a Solution
        solution_obj1 = solution.SolutionFactory.get_solution()
        solution_set.add(solution_obj1)

        # make sure Solution was added
        self.assertTrue(solution_set.contains(solution_obj1))
        self.assertEqual(solution_set.size, 1)

        # add another Solution
        solution_obj2 = solution.SolutionFactory.get_solution()
        solution_set.add(solution_obj2)

        # make sure last Solution was added
        self.assertTrue(solution_set.contains(solution_obj2))
        self.assertEqual(solution_set.size, 2)

    def test_solution_set_remove(self):
        solution_set = _SolutionSet()

        # add a Solution
        solution_obj1 = solution.SolutionFactory.get_solution()
        solution_set.add(solution_obj1)

        # make sure Solution was added
        self.assertTrue(solution_set.contains(solution_obj1))

        # remove the Solution
        solution_set.remove(solution_obj1)

        # make sure solution was removed
        self.assertFalse(solution_set.contains(solution_obj1))
        self.assertEqual(solution_set.size, 0)

    def test_tabu_list_enqueue(self):
        # add solutions to tabu list
        tabu_list = _TabuList(solution.SolutionFactory.get_solution())
        size = 100
        while tabu_list.solutions.size < size:
            tabu_list.enqueue(solution.SolutionFactory.get_solution())
        self.assertNotEqual(tabu_list.head.data_val, tabu_list.tail.data_val)

        # count the number of solutions in tabu_list
        cnt = 0
        tmp_node = tabu_list.head
        while tmp_node is not None:
            tmp_node = tmp_node.next_node
            cnt += 1

        self.assertEqual(cnt, size)

    def test_tabu_list_dequeue(self):
        initial_solution = solution.SolutionFactory.get_solution()

        # build tabu_list and solutions list
        tabu_list = _TabuList(initial_solution)
        lst = [initial_solution]
        size = 100
        while tabu_list.solutions.size < size:
            solution_obj = solution.SolutionFactory.get_solution()
            tabu_list.enqueue(solution_obj)
            lst.append(solution_obj)

        # check that solutions are dequeued in correct order
        i = 0
        while 0 < tabu_list.solutions.size:
            self.assertTrue(tabu_list.solutions.contains(lst[i]))
            self.assertEqual(lst[i], tabu_list.dequeue())
            self.assertFalse(tabu_list.solutions.contains(lst[i]))
            i += 1

    def test_max_heap(self):

        heap_size = 50
        heap = _MaxHeap()
        for _ in range(heap_size):
            heap.heappush(solution.SolutionFactory.get_solution())

        self.assertEqual(heap_size, len(heap), "The max heap size should be equal to heap_size")

        while len(heap) > 1:
            sol = heap.heappop()
            self.assertGreaterEqual(sol, heap[0],
                                    "The max heap items should be organized with the worst solutions (greatest) at h[0]")


if __name__ == '__main__':
    unittest.main()
