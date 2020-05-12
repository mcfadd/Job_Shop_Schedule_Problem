import heapq
import time


def get_stop_condition(time_condition, runtime, max_iterations):
    """
    TODO

    :type time_condition: bool
    :param time_condition:

    :type runtime: int
    :param runtime:

    :type max_iterations: int
    :param max_iterations:

    :rtype: function
    :return:
    """
    if time_condition:
        stop_time = time.time() + runtime

        def stop_condition(iterations):
            return time.time() >= stop_time
    else:
        def stop_condition(iterations):
            return iterations >= max_iterations

    return stop_condition


class Heap:
    """
    TODO
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
        return heapq.heappop(self._heap).val

    def __getitem__(self, i):
        return self._heap[i].val

    def __len__(self):
        return len(self._heap)


class MaxHeapObj:
    """
    TODO
    """
    def __init__(self, val):
        self.val = val

    def __lt__(self, other):
        return self.val > other.val

    def __gt__(self, other):
        return self.val < other.val

    def __eq__(self, other):
        return self.val == other.val
