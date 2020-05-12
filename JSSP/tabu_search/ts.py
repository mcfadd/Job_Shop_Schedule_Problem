import pickle
import random
import time
from queue import Queue

import numpy as np

from ._generate_neighbor import generate_neighbor
from ..exception import InfeasibleSolutionException
from ..util import get_stop_condition, Heap


class TabuSearchAgent:
    """
    Tabu search optimization agent.

    :type stopping_condition: float
    :param stopping_condition: either the duration in seconds or the number of iterations to search

    :type time_condition: bool
    :param time_condition: if true TS is ran for stopping_condition number of seconds else it is ran for stopping_condition number of iterations

    :type initial_solution: Solution
    :param initial_solution: initial solution to start the tabu search from

    :type num_solutions_to_find: int
    :param num_solutions_to_find: number of best solutions to find

    :type tabu_list_size: int
    :param tabu_list_size: size of the Tabu list

    :type neighborhood_size: int
    :param neighborhood_size: size of neighborhoods to generate during each iteration

    :type neighborhood_wait: float
    :param neighborhood_wait: maximum time (in seconds) to wait while generating a neighborhood

    :type probability_change_machine: float
    :param probability_change_machine: probability of changing a chosen operations machine, must be in range [0, 1]

    :type reset_threshold: int
    :param reset_threshold: number of iterations to potentially force a worse move after if the best solution is not improved

    :type benchmark: bool
    :param benchmark: if true benchmark data is gathered
    """
    def __init__(self, stopping_condition, time_condition, initial_solution, num_solutions_to_find=1,
                 tabu_list_size=50, neighborhood_size=300, neighborhood_wait=0.1, probability_change_machine=0.8,
                 reset_threshold=100, benchmark=False):
        """
        Initializes an instance of TabuSearchAgent.

        See help(TabuSearchAgent)
        """
        self.runtime = None
        self.iterations = None
        self.time_condition = time_condition
        if time_condition:
            self.runtime = stopping_condition
        else:
            self.iterations = stopping_condition

        self.initial_solution = initial_solution
        self.num_solutions_to_find = num_solutions_to_find
        self.tabu_list_size = tabu_list_size
        self.neighborhood_size = neighborhood_size
        self.neighborhood_wait = neighborhood_wait
        self.probability_change_machine = probability_change_machine
        self.reset_threshold = reset_threshold
        self.benchmark = benchmark

        # uninitialized ts results
        self.all_solutions = []
        self.best_solution = None

        if benchmark:
            # uninitialized ts benchmark results
            self.benchmark_iterations = 0
            self.neighborhood_size_v_iter = []
            self.seed_solution_makespan_v_iter = []
            self.tabu_size_v_iter = []
            self.min_makespan_coordinates = (0, 0)

    def _generate_neighborhood(self, seed_solution, dependency_matrix_index_encoding, usable_machines_matrix):
        """
        Generates a neighborhood of Solutions instances that are neighbors of the seed_solution parameter.

        :type seed_solution: Solution
        :param seed_solution: The solution to generate a neighborhood of

        :type dependency_matrix_index_encoding: nparray
        :param dependency_matrix_index_encoding: Dependency matrix index encoding from static Data

        :type usable_machines_matrix: nparray
        :param usable_machines_matrix: Usable machines matrix from static Data

        :rtype: SolutionSet
        :returns: Neighboring Solutions
        """
        stop_time = time.time() + self.neighborhood_wait
        neighborhood = _SolutionSet()
        while neighborhood.size < self.neighborhood_size and time.time() < stop_time:
            try:
                neighbor = generate_neighbor(seed_solution, self.probability_change_machine,
                                             dependency_matrix_index_encoding, usable_machines_matrix)

                if neighbor not in neighborhood:
                    neighborhood.add(neighbor)

            except InfeasibleSolutionException:
                # this should not happen
                # if it does don't add the infeasible solution to the neighborhood
                pass
        return neighborhood

    def start(self, multi_process_queue=None):
        """
        Starts the search for this TabuSearchAgent.

        If the multi_process_queue parameter is not None, this function attempts to push this TabuSearchAgent to the multi processing queue.

        :type multi_process_queue: multiprocessing.Queue
        :param multi_process_queue: queue to put this TabuSearchAgent into

        :rtype: Solution
        :returns: best Solution found
        """

        # get static data
        dependency_matrix_index_encoding = self.initial_solution.data.job_task_index_matrix
        usable_machines_matrix = self.initial_solution.data.usable_machines_matrix

        # ts variables
        tabu_list = _TabuList()
        seed_solution = self.initial_solution
        best_solutions_heap = Heap(max_heap=True)
        for _ in range(self.num_solutions_to_find):
            best_solutions_heap.push(self.initial_solution)

        # variables used for restarts
        lacking_solution = seed_solution
        counter = 0

        iterations = 0

        # variables used for benchmarks
        neighborhood_size_v_iter = []
        tabu_size_v_iter = []
        seed_solution_makespan_v_iter = []
        absolute_best_solution_makespan = seed_solution.makespan
        absolute_best_solution_iteration = 0

        # create stopping condition function
        stop_condition = get_stop_condition(self.time_condition, self.runtime, self.iterations)
        # if self.time_condition:
        #     stop_time = time.time() + self.runtime
        #
        #     def stop_condition():
        #         return time.time() >= stop_time
        # else:
        #     stop_iter = self.iterations
        #
        #     def stop_condition():
        #         return iterations >= stop_iter

        while not stop_condition(iterations):
            neighborhood = self._generate_neighborhood(seed_solution,
                                                       dependency_matrix_index_encoding,
                                                       usable_machines_matrix)

            sorted_neighborhood = sorted(neighborhood.solutions.items())
            break_boolean = False

            for makespan, lst in sorted_neighborhood:  # sort neighbors in increasing order by makespan
                for neighbor in sorted(lst):  # sort subset of neighbors with the same makespans
                    if neighbor not in tabu_list:
                        # if new seed solution is not better than current seed solution add it to the tabu list
                        if neighbor >= seed_solution:
                            tabu_list.put(seed_solution)
                            if len(tabu_list) > self.tabu_list_size:
                                tabu_list.get()

                        seed_solution = neighbor
                        break_boolean = True
                        break

                if break_boolean:
                    break

            if seed_solution < best_solutions_heap[0]:
                best_solutions_heap.pop()  # remove the worst best solution from the heap
                best_solutions_heap.push(seed_solution)  # add the new best solution to the heap
                if self.benchmark and seed_solution.makespan < absolute_best_solution_makespan:
                    absolute_best_solution_makespan = seed_solution.makespan
                    absolute_best_solution_iteration = iterations

            # if solution is not being improved after a number of iterations, force a move to a worse one
            counter += 1
            if counter > self.reset_threshold:
                if not lacking_solution > seed_solution and len(sorted_neighborhood) > 10:
                    # add the seed solution to the tabu list
                    tabu_list.put(seed_solution)
                    if len(tabu_list) > self.tabu_list_size:
                        tabu_list.get()
                    # choose a worse solution from the neighborhood
                    seed_solution = sorted_neighborhood[random.randint(1, int(0.2 * len(sorted_neighborhood)))][1][0]

                counter = 0
                lacking_solution = seed_solution

            if self.benchmark:
                iterations += 1
                neighborhood_size_v_iter.append(neighborhood.size)
                seed_solution_makespan_v_iter.append(seed_solution.makespan)
                tabu_size_v_iter.append(len(tabu_list))
            elif not self.time_condition:
                iterations += 1

        # convert best_solutions_heap to a sorted list
        best_solutions_list = []
        while len(best_solutions_heap) > 0:
            sol = best_solutions_heap.pop()
            sol.machine_makespans = np.asarray(sol.machine_makespans)
            best_solutions_list.append(sol)

        self.all_solutions = best_solutions_list
        self.best_solution = min(best_solutions_list)

        if self.benchmark:
            self.benchmark_iterations = iterations
            self.neighborhood_size_v_iter = neighborhood_size_v_iter
            self.seed_solution_makespan_v_iter = seed_solution_makespan_v_iter
            self.tabu_size_v_iter = tabu_size_v_iter
            self.min_makespan_coordinates = (absolute_best_solution_iteration, absolute_best_solution_makespan)

        if multi_process_queue is not None:
            # pickle results and add to Queue
            self.initial_solution.machine_makespans = np.asarray(self.initial_solution.machine_makespans)
            multi_process_queue.put(pickle.dumps(self, protocol=-1))

        return self.best_solution


'''
TS data structures
'''


# class _MaxHeapObj:
#     """
#     Wrapper class for Solution used in _MaxHeap.
#     """
#     def __init__(self, val):
#         self.val = val
#
#     def __lt__(self, other):
#         return self.val > other.val
#
#     def __eq__(self, other):
#         return self.val == other.val


# class _MaxHeap:
#     """
#     Heap for containing Solution instances.
#     """
#     def __init__(self):
#         self.h = []
#
#     def push(self, solution):
#         """
#         Pushes a solution onto this _MaxHeap.
#
#         :type solution: Solution
#         :param solution: solution to push
#
#         :return: None
#         """
#         heapq.heappush(self.h, _MaxHeapObj(solution))
#
#     def pop(self):
#         """
#         Pops a solution from the top of this _MaxHeap.
#
#         :rtype: Solution
#         :return: solution at the top of this heap
#         """
#         return heapq.heappop(self.h).val
#
#     def __getitem__(self, i):
#         return self.h[i].val
#
#     def __len__(self):
#         return len(self.h)


# class _Node:
#     """
#     Single linked list node ADT used in _TabuList.
#     """
#     def __init__(self, data_val=None):
#         self.data_val = data_val
#         self.next_node = None


class _TabuList(Queue):
    """
    Queue for containing Solution instances.
    """
    def __init__(self, max_size=0):
        super().__init__(max_size)
        self.solutions = _SolutionSet()

    def put(self, solution, block=True, timeout=None):
        super().put(solution, block, timeout)
        self.solutions.add(solution)

    def get(self, block=True, timeout=None):
        result = super().get(block, timeout)
        self.solutions.remove(result)
        return result

    def __contains__(self, solution):
        return solution in self.solutions

    def __len__(self):
        return self.solutions.size

# class _TabuList:
#     """
#     Queue for containing Solution instances.
#     """
#     def __init__(self, initial_solution):
#         self.head = self.tail = _Node(data_val=initial_solution)  # use linked list to keep FIFO behavior
#         self.solutions = _SolutionSet()
#         self.solutions.add(initial_solution)
#
#     def enqueue(self, solution):
#         """
#         Adds a solution to the end of this _TabuList.
#
#         :type solution: Solution
#         :param solution: solution to add
#
#         :returns: None
#         """
#         self.solutions.add(solution)
#         new_node = _Node(data_val=solution)
#         self.tail.next_node = new_node
#         self.tail = new_node
#
#     def dequeue(self):
#         """
#         Removes the solution at the beginning of this _TabuList.
#
#         :rtype: Solution
#         :returns: Solution that was removed
#         """
#         head_node = self.head
#         self.head = self.head.next_node
#         self.solutions.remove(head_node.value)
#         return head_node.value
#
#     def __contains__(self, solution):
#         return solution in self.solutions
#
#     def __len__(self):
#         return self.solutions.size


class _SolutionSet:
    """
    Set for containing Solution instances.
    """
    def __init__(self):
        self.size = 0
        self.solutions = {}

    def add(self, solution):
        """
        Adds a solution and increments size.

        :type solution: Solution
        :param solution: solution to add

        :returns: None
        """
        if solution.makespan not in self.solutions:
            self.solutions[solution.makespan] = [solution]
        else:
            self.solutions[solution.makespan].append(solution)

        self.size += 1

    def remove(self, solution):
        """
        Removes a solution and decrements size.

        :type solution: Solution
        :param solution: solution to remove

        :returns: None
        """
        if len(self.solutions[solution.makespan]) == 1:
            del self.solutions[solution.makespan]
        else:
            self.solutions[solution.makespan].remove(solution)

        self.size -= 1

    def __contains__(self, solution):
        """
        Returns true if the solution is in this _SolutionSet.

        :type solution: Solution
        :param solution: solution to look for

        :rtype: bool
        :returns: true if the solution is in this _SolutionSet
        """
        return solution.makespan in self.solutions and solution in self.solutions[solution.makespan]
