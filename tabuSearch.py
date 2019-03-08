from random import randint


# TODO
# make this set more efficient (e.g. implement AVL tree instead of list)
# redo pprint()
class myset:

    def __init__(self, ):
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


class tabuSearch:

    def __init__(self, solver):
        self.solver = solver

    def generate_neighbor(self, solution, debug=False):

        lowerIndex = upperIndex = 0
        while lowerIndex == upperIndex:
            result = list(solution)
            randIndex = randint(0, len(solution) - 1)
            operation = result.pop(randIndex)
            jobId = operation.getTask().getJobId()
            sequence = operation.getTask().getSequence()

            if debug:
                print("randIndex = {}\noperation = {}\nresult = {}".format(randIndex, operation.getString(), result))

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
            print("lowerIndex = {}\nupperIndex = {}\nplacementIndex = {}".format(lowerIndex, upperIndex,
                                                                                 placementIndex))

        result.insert(placementIndex, operation)
        makespan = self.solver.compute_makespan(result)

        # this should never happen
        assert makespan != -1, "\nsolution = {}\nrandIndex = {}\nlowerIndex = {}\nupperIndex = {}\nplacementIndex = {}\nresult = {}".format(
            solution, randIndex, lowerIndex, upperIndex, placementIndex, result)

        return (max(makespan[0]), makespan[1], result)

    def generate_neighborhood(self, size, solution, debug=False):
        result = myset()
        while result.size != size:
            result.add(self.generate_neighbor(solution, debug))

        return result
