import heapq
import time


def get_stop_condition(time_condition, runtime, max_iterations):
    """
    Gets a function for checking the stopping condition of an optimization function.

    :type time_condition: bool
    :param time_condition: If True then runtime is used as the stopping condition

    :type runtime: float
    :param runtime: number of seconds that the optimization function should run for

    :type max_iterations: int
    :param max_iterations: maximum number of iterations that the optimization function should execute

    :rtype: function
    :return: function which returns True if the stopping condition is met
    """
    if time_condition:
        stop_time = time.time() + runtime

        def stop_condition(_):
            return time.time() >= stop_time
    else:
        def stop_condition(iterations):
            return iterations >= max_iterations

    return stop_condition


class Heap:
    """
    Heap data structure.
    """

    def __init__(self, max_heap=False):
        self._heap = []
        self._is_max_heap = max_heap

    def push(self, obj):
        if self._is_max_heap:
            heapq.heappush(self._heap, MaxHeapObj(obj))
        else:
            heapq.heappush(self._heap, obj)

    def pop(self):
        if self._is_max_heap:
            return heapq.heappop(self._heap).val
        else:
            return heapq.heappop(self._heap)

    def __getitem__(self, i):
        return self._heap[i].val

    def __len__(self):
        return len(self._heap)


class MaxHeapObj:
    """
    Wrapper class used for max heaps.
    """
    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return self.val > other.val

    def __gt__(self, other):
        return self.val < other.val

    def __eq__(self, other):
        return self.val == other.val
