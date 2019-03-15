from random import randint
from data_set import Solution
from makespan import makespanCalculator

# TODO
# 1. make this class more efficient (e.g. implement AVL tree instead of list)
# 2. redo pprint()
class neighbor_set:

    def __init__(self):
        self.size = 0
        self.elems = []

    def add(self, elem):
        if elem not in self.elems:
            self.elems.append(elem)
            self.size += 1

    def pprint(self):
        for e in self.elems:
            print("({}, {})".format(e[0], e[1]).ljust(13, " "), end="")
            for operation in e[2]:
                print("[", operation.getString(), end=" ")
            print("]")


class TabuSearch:

    def generate_neighbor(self, operationsList, debug=False):

        lowerIndex = upperIndex = 0
        while lowerIndex == upperIndex:
            result = list(operationsList)
            randIndex = randint(0, len(operationsList) - 1)
            operation = result.pop(randIndex)
            jobId = operation.getTask().getJobId()
            sequence = operation.getTask().getSequence()

            if debug:
                print(f"randIndex = {randIndex}\n"
                      f"operation = \n{operation.getString()}\n"
                      f"result = \n{result}\n")

            lowerIndex = min(randIndex, len(result) - 1)
            while lowerIndex >= 0 and not (
                    result[lowerIndex].getTask().getJobId() == jobId and result[
                lowerIndex].getTask().getSequence() == sequence - 1):
                lowerIndex -= 1

            lowerIndex = 0 if lowerIndex < 0 else lowerIndex + 1

            upperIndex = min(randIndex, len(result) - 1)
            while upperIndex < len(result) and not (
                    result[upperIndex].getTask().getJobId() == jobId and result[
                upperIndex].getTask().getSequence() == sequence + 1):
                upperIndex += 1

            upperIndex = upperIndex - 1 if upperIndex > len(result) else upperIndex

        placementIndex = randIndex
        while placementIndex == randIndex:
            placementIndex = randint(lowerIndex, upperIndex)

        if debug:
            print(f"lowerIndex = {lowerIndex}\n"
                  f"upperIndex = {upperIndex}\n"
                  f"placementIndex = {placementIndex}\n")

        result.insert(placementIndex, operation)
        makespan_and_wait = makespanCalculator.compute_makespan_and_wait(result)

        # this should never happen
        assert makespan_and_wait != -1, "Error in tabuSearch.generate_neighbor()!" \
                               f"randIndex = {randIndex}\n" \
                               f"lowerIndex = {lowerIndex}\n" \
                               f"upperIndex = {upperIndex}\n" \
                               f"placementIndex = {placementIndex}\n" \
                               f"result = \n{result}\n"

        return (max(makespan_and_wait[0]), makespan_and_wait[1], result)

    def generate_neighborhood(self, size, solution, debug=False):
        result = neighbor_set()
        while result.size != size:
            result.add(self.generate_neighbor(solution, debug))

        return result
