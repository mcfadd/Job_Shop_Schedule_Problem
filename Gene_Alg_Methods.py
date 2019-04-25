import random
import numpy as np
import data
import solution
"""
This function will generate a child solution using 2 parents as its list of operations
:param parent_1: np.array solution used for cross_over operator
:param parent_2: " "
:return: Solution as array
"""
def cross_over(parent_1,parent_2):

    p_1 = np.ndarray.tolist(parent_1)
    p_2 = np.ndarray.tolist(parent_2)
    top = []
    bottom = []

#Generates our top and bottom bounds from parent to be transerfed to our child
    x=random.randint(0,len(p_1)-1)
    y=random.randint(x+1,len(p_1))

#Will itterate through the list and check each chromosome to make sure:
#1. Chromosome is not in child_1 already
#2. See if the sequence from the chromosome belongs in top list.
#If 1 is false and 2 is false then it will append the chromosome to the bottom list
#If 1 is false and 2 is true then it will append the chromosome to the top list
#It will combine the lists at the end and produce a solution
    for k in range(0,len(p_2)):
        result = check(p_1[x:y],p_2[k])
        if(result== -1):
            top.append(p2[k])
        elif(result== 1):
            bottom.append(p2[k])

    return Solution(np.asarray(top+p_1[x:y]+bottom),dtype=np.intc)


"""
This function checks to make sure that a operation isn't in the child already
:param child: a list of operations that are already in the final solution
:param parent_chromosome: a operation from a parent
:return: 0 (if operation is already in the child solution), 1 (if child sequence number is smaller 
         then parent_chromosome seqeunce #), -1 (if niether is returned)
"""
def check(child,parent_chromosome):
    for row in range(0,len(child)):
        if(child[row][0]==parent_chromosome[0]):
            if(child[row][1]==parent_chromosome[1]):
                    return 0
    for row in range(0,len(child)):
        if(child[row][2]<parent_chromosome[2]):
            return 1
        else:
            return -1
    return -1
"""
This function using generic selection method will generate a new population
:param population: a set of solutions passed through to act as our initial population
:timer: a set time passed for how long we want to generate generations
:return: best solution makespan
"""
def generate_generation(population,timer):
    best_solution = 0
    mutation_probability = .2
#loop that will run until we run out of time
    while(timer != 0):
        tracker = range(0,np.ndarray.size(population))
        #organizes population based on makespan size [best,worst]
        for i in range(len(tracker)):
            minimum = i
            for j in range(i+1,len(tracker)):
                if (population[j].It(population[i])):
                    minimum = j
            population[minimum], population[i] = population[i], population[minimum]
        #adds up all the makespan in population to be used as our normalizer
        total_makespan_sum = 0
        for i in range(len(tracker)):
            total_makespan_sum+=population[i].makespan
        #creates fitness list that is organized just like the population
        fitness_list = []
        for i in range(0,len(tracker)):
            fitness_value = population[i].makespan/total_makespan_sum
            fitness_list[i]=fitness_value
        #loop that will run until our tracker list is empty
        while(len(tracker)!=0):
        #chooses a random number between 0,1 and will pick the first biggest fitness value
        #from our fitness list that will then be our parent that we will pass over to be
        #crossed over. It will also remove position from tracker and fitness valus from fitness list
            r_1 = random.random()
            for i in range(0,len(fitness_list)):
                if(fitness_list[i]>=r_1):
                    parent_1=population[tracker[i]]
                    fitness_list.remove(fitness_list[i])
                    position_1=tracker.pop(i)
                    break

            r_2 = random.random()
            for i in range(0,len(fitness_list)):
                if(fitness_list[i]>=r_2):
                    parent_2=Population[tracker[i]]
                    fitness_list.remove(fitness_list[i])
                    position_2=tracker.pop(i)
                    break
        #crosses parent 1 and 2 and will pass the child the child for mutation and then place child
        #in the place of either parent 1 or 2
            child_1 = cross_over(parent_1,parent_2)
            population[position_1]= mutation(child_1,mutation_probability)
            if(population[position_1].makespan<best_solution):
                best_solution=population[position_1].makespan

            child_2 = cross_over(parent_2,parent_1)
            population[position_2]=mutation(child_1,mutation_probability)
            if (population[position_2].makespan < best_solution):
                best_solution = population[position_2].makespan

    return best_solution
"""
This function takes a child and will change a random machine operation in the soultion list 
:param child: a solution that might be changed
:param probability: the chance of said child to undergo mutation
:return: child after mutation
"""
def mutation(child,probability):
    if(probability<random.random()):
        position = random.randint(0,len(np.ndarray.size(child)))
        machine_list_position =random.randint(0,len(child[position].get_usable_machines))
        child[position][3]=child[position].get_usable_machines[machine_list_position]
        return Solution(child,dtype=np.intc)
    return child

