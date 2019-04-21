import numpy as np

from data import Data
from solution import Solution

'''
This file contains three solutions for the small problem instance in the data folder.
They should be small enough to draw out by hand to verify the machine makespans are correct.
'''
Data.initialize_data(f'../data/data_set1/sequenceDependencyMatrix.csv',
                     f'../data/data_set1/machineRunSpeed.csv',
                     f'../data/data_set1/jobTasks.csv')

# machine makespans = [12, 13, 12]
sol1 = Solution(np.array([[0, 0, 0, 0, 2],
                         [1, 0, 0, 1, 5],
                         [1, 1, 0, 2, 8],
                         [1, 2, 1, 0, 4],
                         [1, 3, 1, 1, 5],
                         [2, 0, 0, 2, 4]], dtype=np.intc))

# machine makespans = [13, 9, 14]
sol2 = Solution(np.array([[0, 0, 0, 0, 2],
                          [2, 0, 0, 0, 4],
                          [1, 0, 0, 1, 9],
                          [1, 1, 0, 2, 8],
                          [1, 2, 1, 0, 4],
                          [1, 3, 1, 2, 5]], dtype=np.intc))

# machine makespans = [23, 18, 23]
sol3 = Solution(np.array([[0, 0, 0, 1, 10],
                          [0, 1, 0, 0, 5],
                          [2, 0, 0, 0, 8],
                          [1, 0, 0, 1, 8],
                          [1, 1, 1, 0, 5],
                          [1, 3, 1, 2, 5]], dtype=np.intc))

sol1.pprint()
sol2.pprint()
sol3.pprint()
