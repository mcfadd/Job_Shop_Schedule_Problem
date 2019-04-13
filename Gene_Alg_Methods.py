import random

def cross_over(parent1,parent2):

    child_1=[]
    child_2=[]
    top = []
    bottom = []
    top_child2=[]
    bottom_child2=[]
    pop=[]
#Generates our top and bottom bounds from parent to be transerfed to our child
#Y will always generate a bound greater then x in order to make sure y isn't smaller then x
    x=random.randint(0,len(parent1))
    y=random.randint(x,len(parent1))
#In case we generate the same x and y this will generate a new number for y
    while(x==y):
        y=random.randint(0,len(parent1))
#Was added due to child sometimes being empty this checks and will keep generating x and y till child is not empty
    for i in range(x,y):
     child_1.append(parent1[i])
    while(len(child_1)==0):
        x = random.randint(0, len(parent1))
        y = random.randint(x, len(parent1))
        while (x == y):
            y = random.randint(0, len(parent1))
        for i in range(x, y):
            child_1.append(parent1[i])

    print("Child 1: ",child_1)

    x2=random.randint(0,len(parent2))
    y2=random.randint(x2,len(parent2))

    while (x2 == y2):
        y2 = random.randint(0, len(parent2))

    for i in range(x2, y2):
        child_2.append(parent2[i])
    while (len(child_2) == 0):
        x2 = random.randint(0, len(parent2))
        y2 = random.randint(x, len(parent2))
        while (x2 == y2):
            y2 = random.randint(0, len(parent2))
        for i in range(x2, y2):
            child_2.append(parent2[i])

    print("Child 2: ", child_2)
#Will itterate through the list and check each chromosome to make sure:
#1. Chromosome is not in child_1 already
#2. See if the sequence from the chromosome belongs in top list.
#If 1 is false and 2 is false then it will append the chromosome to the bottom list
#If 1 is false and 2 is true then it will append the chromosome to the top list
#It will combine the lists at the end and produce a solution
#NOTE: was thinking that if said job has no trace of previous or future jobs in child to append to child instead of adding to top and then appending as needed.
    for k in range(0,len(parent2)):
        if (chromosome_check(child_1, parent2[k])==False):
            if(top_checker(child_1,parent2[k])==False):
                bottom.append(parent2[k])
            else:
                top.append(parent2[k])
    solution = top+child_1+bottom
    pop.append(solution)
    print("Top: ", top)
    print("Bottom: ", bottom)

    for k in range(0,len(parent1)):
        if(chromosome_check(child_2, parent1[k])==False):
            if(top_checker(child_2,parent1[k])==False):
                bottom_child2.append(parent1[k])
            else:
                top_child2.append(parent1[k])
    soultion2 = top_child2+child_2+bottom_child2
    pop.append(soultion2)
    print("Top2: ", top)
    print("Bottom2: ", bottom)
    return pop


#checks to make sure that parent_chromosome isn't in childs list from [x,y]
def chromosome_check(child,parent_chromosome):
    for j in range(0,len(child)):
        if(child[j][0]==parent_chromosome[0]):
            if(child[j][1]==parent_chromosome[1]):
                if(child[j][2]==parent_chromosome[2]):
                    return True
    return False


#will take bottom list and correctly place the desired chromosome in bottom list
def top_checker(child,chromosome):
    for j in range(0,len(child)):
        if(child[j][0]==chromosome[0]):
            if(child[j][2]<=chromosome[2]):
                return False

