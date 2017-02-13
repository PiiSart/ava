#!/usr/bin/python3
'''
Created on 13.01.2017

Create a input file for graphviz.

@author: Viktor Werle
'''

import sys
from random import randint

def getNeighbor(graph, node_id, number_of_nodes):
    '''
    Decide a neighbor for node
    '''
    found = False;
    # search neighbor
    while found == False:        
        neighbor_id = randint(0,number_of_nodes - 1)
        # exclude dual edges and node loops
        print("Neighbor ID: "  + str(neighbor_id) + " Node ID: " + str(node_id))
        if neighbor_id not in graph.get(node_id) and neighbor_id != node_id:
            print(graph)
            if node_id not in graph[neighbor_id]:                
                found = True;
    return neighbor_id



def __createGraphviz(nodes, edges):
    '''
    '''
    file = open("../conf/graphviz.txt", "w")
    file.write("graph G{\n")
    for n in range(0, nodes) :
        if n % 2 == 0:   
            file.write(str(n) + " -- " + str(n + 1) + ";\n")
        else:
            file.write(str(n) + " -- " + str(n - 1) + ";\n")
    file.write("}")
    file.close()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[2] <= sys.argv[1]:
            print("Number of edges must be greater as number of nodes!")
        else:
            nodes = int(sys.argv[1])
            edges = int(sys.argv[2])
            __createGraphviz(nodes, edges)
    else:
        print("Usage: graphgen [number of nodes] [number of edges]")
        
        
