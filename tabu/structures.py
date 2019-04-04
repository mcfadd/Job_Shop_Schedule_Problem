
class Node:
    def __init__(self, data_val=None):
        self.data_val = data_val
        self.next_node = None


class TabuList:
    """
    This class is a set ADT that provides enqueue and dequeue behaviors.
    """

    def __init__(self):
        self.head = self.tail = None        # use linked list to keep FIFO property
        self.solutions = SolutionSet()

    def enqueue(self, solution):
        """
        Adds a solution to the end of this TabuList.

        :param solution: The solution to add.
        :return: True if the solution was added.
        """

        if self.solutions.add(solution):
            new_node = Node(data_val=solution)
            if self.head is None:
                self.head = self.tail = new_node
            else:
                self.tail.next_node = new_node
                self.tail = new_node
            return True

        return False

    def dequeue(self):
        """
        Removes the solution at the beginning of this TabuList

        :return: True if a solution was dequeued.
        """

        if self.solutions.size > 0:
            head_node = self.head
            self.head = self.head.next_node
            self.solutions.remove(head_node.data_val)
            return True

        return False


class SolutionSet:
    """
    This class is a simple set ADT for containing Solution objects.
    """

    def __init__(self):
        self.size = 0
        self.solutions = {}

    def add(self, solution):
        """
        Adds a solution and increments size if the solution is not already in this SolutionSet.

        :param solution: The solution to add.
        :return: True if solution was added.
        """
        result = False
        if solution.makespan not in self.solutions:
            self.solutions[solution.makespan] = [solution]
            self.size += 1
            result = True
        elif solution not in self.solutions[solution.makespan]:
            self.solutions[solution.makespan].append(solution)
            self.size += 1
            result = True

        return result

    def remove(self, solution):
        """
        Removes a solution and decrements size if the solution is in this SolutionSet.

        :param solution: The solution to remove.
        :return: None
        """
        self.solutions[solution.makespan].remove(solution)
        self.size -= 1

        if len(self.solutions[solution.makespan]) == 0:
            del self.solutions[solution.makespan]

        return

    def contains(self, solution):
        """
        Returns True if the solution is in this SolutionSet.

        :param solution: The solution to look for.
        :return: True if the solution is in this SolutionSet.
        """
        return solution.makespan in self.solutions and solution in self.solutions[solution.makespan]

    def pprint_makespans(self):
        """
        Prints a list of make spans for the solutions in this SolutionSet.

        :return: None
        """
        print([sol.makespan for sol in self.solutions])

    def pprint(self):
        """
        Prints all of the solutions in this SolutionSet in a pretty way.

        :return: None
        """
        for lst in self.solutions.values():
            for sol in lst:
                sol.pprint()



