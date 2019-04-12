import random

def cross_over(parent1,parent2):

    child_1=[]
    child_2=[]
    top = []
    bottom = []

    x=random.randint(0,len(parent1))
    y=random.randint(x,len(parent1)+1)

    while(x==y):
        y=random.randint(0,len(parent1)+1)

    for i in range(x,y+1):
     child_1.insert(i,parent1[i])
    for k in range(0,len(parent2)+1):
        if (chromosome_check(child_1, parent2[k], x, y)==false):

#checks to make sure that parent_chromosome isn't in childs list from [x,y]
def chromosome_check(child,parent_chromosome,x,y):
    flag=false
    for j in range(x,y+1):
            if(child_1[j]==parent_chromosome):
                flag=true
    return flag
#will take bottom list and correctly place the desired chromosome in bottom list
def bottom_insert(bottom,job,sequence,chromosome):
    smallest_sequence=0
    larget_sequence=0
#if list is empty from the start it will just append the list
    if (len(bottom)==0):
        return bottom.append(chromosome)
    for j in range(0,len(bottom)+1):
        if(bottom[j][3]<=smallest_sequence & bottom[j][0]==job ):
            smallest_sequence=bottom[j][3]
        if(bottom[j][3]>=larget_sequence & bottom[j][0]==job):
            larget_sequence=bottom[j][3]




