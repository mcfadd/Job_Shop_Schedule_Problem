import pickle

import os
import sys

path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

from JSSP.data import Data
from JSSP.genetic_algorithm import search
from JSSP.solution import generate_feasible_solution

Data.initialize_data('../data/data_set2/sequenceDependencyMatrix.csv', '../data/data_set2/machineRunSpeed.csv',
                     '../data/data_set2/jobTasks.csv')

pop_size = 100
# random_population = []
# get best solutions found by TS
with open("/home/mcfadd/Job_Shop_Schedule_Problem/JSSP/test_population.pkl", 'rb') as file:
    random_population = pickle.load(file)

# add randomly generated solutions to population
for _ in range(abs(pop_size - len(random_population))):
    random_population.append(generate_feasible_solution())

print("best sol before:")
min(random_population).pprint()

result = search(30, random_population, 0.1, verbose=True)

print("best sol after:")
result.pprint()
