
class Node:
    def __init__(self, data_val=None):
        self.data_val = data_val
        self.next_node = None


class TabuList:
    """
    This class is a set ADT that provides enqueue and dequeue behaviors.
    """

    def __init__(self, initial_solution):
        self.head = self.tail = Node(data_val=initial_solution)        # use linked list to keep FIFO property
        self.solutions = SolutionSet()
        self.solutions.add(initial_solution)

    def enqueue(self, solution):
        """
        Adds a solution to the end of this TabuList.

        :param solution: The solution to add.
        :return: None
        """

        self.solutions.add(solution)
        new_node = Node(data_val=solution)
        self.tail.next_node = new_node
        self.tail = new_node

    def dequeue(self):
        """
        Removes the solution at the beginning of this TabuList

        :return: Solution that was dequeued
        """

        head_node = self.head
        self.head = self.head.next_node
        self.solutions.remove(head_node.data_val)
        return head_node.data_val


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
        if solution.makespan not in self.solutions:
            self.solutions[solution.makespan] = [solution]
        else:
            self.solutions[solution.makespan].append(solution)

        self.size += 1

    def remove(self, solution):
        """
        Removes a solution and decrements size if the solution is in this SolutionSet.

        :param solution: The solution to remove.
        :return: None
        """
        if len(self.solutions[solution.makespan]) == 1:
            del self.solutions[solution.makespan]
        else:
            self.solutions[solution.makespan].remove(solution)

        self.size -= 1

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
