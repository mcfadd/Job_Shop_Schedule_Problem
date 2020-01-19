import os
import random
import unittest

from JSSP.data import Data
from JSSP.exception import InfeasibleSolutionException
from JSSP.solution import SolutionFactory
from tests import project_root, get_all_fjs_files


class TestHeap(unittest.TestCase):

    def setUp(self) -> None:
        Data.initialize_data_from_csv(
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
            project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')

    def test_min_heap_class(self):
        task1 = Data.jobs[0].get_task(0)
        task2 = Data.jobs[0].get_task(1)

        min_heap_obj_task1 = SolutionFactory._MinHeapObj(task1)
        min_heap_obj_task2 = SolutionFactory._MinHeapObj(task2)
        self.assertGreater(min_heap_obj_task1, min_heap_obj_task2)

    def test_max_heap_class(self):
        task1 = Data.jobs[0].get_task(0)
        task2 = Data.jobs[0].get_task(1)

        max_heap_obj_task1 = SolutionFactory._MaxHeapObj(task1)
        max_heap_obj_task2 = SolutionFactory._MaxHeapObj(task2)
        self.assertLess(max_heap_obj_task1, max_heap_obj_task2)

    def test_min_heap(self):
        heap = SolutionFactory._JobTaskHeap(maxheap=False)
        for job in Data.jobs:
            for task in job.get_tasks():
                heap.push_task(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop_task()
            task_index = Data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertLessEqual(tmp_list[i][1], tmp_list[i + 1][1])

    def test_max_heap(self):
        heap = SolutionFactory._JobTaskHeap(maxheap=True)
        for job in Data.jobs:
            for task in job.get_tasks():
                heap.push_task(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop_task()
            task_index = Data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in Data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertGreaterEqual(tmp_list[i][1], tmp_list[i + 1][1])


class TestGenSolution(unittest.TestCase):

    def setUp(self) -> None:
        self.fjs_data = get_all_fjs_files()

    def test_generate_feasible_solution(self):
        try:
            Data.initialize_data_from_csv(
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'sequenceDependencyMatrix.csv',
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'machineRunSpeed.csv',
                project_root + os.sep + 'data' + os.sep + 'given_data' + os.sep + 'jobTasks.csv')
            SolutionFactory.get_n_solutions(500)

        except InfeasibleSolutionException:
            self.assertTrue(False, "Infeasible solution was generated")

    def test_generate_feasible_solution_spt(self):  # Note this test fails on data/given_data
        for fjs_instance in random.choices(self.fjs_data, k=10):
            try:
                print("test_generate_feasible_solution_spt with fjs data: " + fjs_instance)
                Data.initialize_data_from_fjs(fjs_instance)
                SolutionFactory.get_n_shortest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.assertTrue(False, "Infeasible solution was generated")

    def test_generate_feasible_solution_lpt(self):  # Note this test fails on data/given_data
        for fjs_instance in random.choices(self.fjs_data, k=10):
            try:
                print("test_generate_feasible_solution_lpt with fjs data: " + fjs_instance)
                Data.initialize_data_from_fjs(fjs_instance)
                SolutionFactory.get_n_longest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.assertTrue(False, "Infeasible solution was generated")


if __name__ == '__main__':
    unittest.main()
