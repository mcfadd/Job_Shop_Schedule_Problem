import random
import unittest

from JSSP import data
from JSSP.exception import InfeasibleSolutionException
from JSSP.solution.factory import TaskWrapper, _JobTaskHeap, SolutionFactory
from tests.util import project_root, csv_data, get_files_with_suffix


class TestHeap(unittest.TestCase):

    def test_task_wrapper_class(self):
        task1 = csv_data.jobs[0].get_task(0)
        task2 = csv_data.jobs[0].get_task(1)

        max_heap_obj_task1 = TaskWrapper(csv_data, task1)
        max_heap_obj_task2 = TaskWrapper(csv_data, task2)
        self.assertGreater(max_heap_obj_task1, max_heap_obj_task2)

    def test_min_heap(self):
        heap = _JobTaskHeap(csv_data, max_heap=False)
        for job in csv_data.jobs:
            for task in job.get_tasks():
                heap.push(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop()
            task_index = csv_data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in
                                csv_data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertLessEqual(tmp_list[i][1], tmp_list[i + 1][1])

    def test_max_heap(self):
        heap = _JobTaskHeap(csv_data, max_heap=True)
        for job in csv_data.jobs:
            for task in job.get_tasks():
                heap.push(task)

        tmp_list = []
        while len(heap) > 0:
            task = heap.pop()
            task_index = csv_data.job_task_index_matrix[task.get_job_id(), task.get_task_id()]

            processing_times = [processing_time for processing_time in
                                csv_data.task_processing_times_matrix[task_index] if
                                processing_time != -1]

            avg_processing_time = sum(processing_times) / len(processing_times)
            tmp_list.append((task, avg_processing_time))

        for i in range(len(tmp_list) - 1):
            self.assertGreaterEqual(tmp_list[i][1], tmp_list[i + 1][1])


class TestGenSolution(unittest.TestCase):

    def test_generate_feasible_solution(self):
        try:
            SolutionFactory(csv_data).get_n_solutions(500)

        except InfeasibleSolutionException:
            self.fail("Infeasible solution was generated")

    def test_generate_feasible_solution_spt(self):  # Note this test fails on data/given_data
        fjs_data = get_files_with_suffix(project_root / 'data/fjs_data', '.fjs')
        for fjs_instance in random.choices(fjs_data, k=10):
            try:
                print(f"test_generate_feasible_solution_spt with fjs data: {fjs_instance}")
                SolutionFactory(data.FJSData(fjs_instance)).get_n_shortest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.fail("Infeasible solution was generated")

    def test_generate_feasible_solution_lpt(self):  # Note this test fails on data/given_data
        fjs_data = get_files_with_suffix(project_root / 'data/fjs_data', '.fjs')
        for fjs_instance in random.choices(fjs_data, k=10):
            try:
                print(f"test_generate_feasible_solution_lpt with fjs data: {fjs_instance}")
                SolutionFactory(data.FJSData(fjs_instance)).get_n_longest_process_time_first_solution(50)

            except InfeasibleSolutionException:
                self.fail("Infeasible solution was generated")


if __name__ == '__main__':
    unittest.main()
