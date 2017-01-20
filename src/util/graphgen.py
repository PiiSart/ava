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
    #nodes = int(sys.argv[1])
    #edges = int(sys.argv[2])
    graph = {}
    file = open("../conf/graphviz.txt", "w")
    file.write("graph G{\n")
    e = 0
    while e < edges:
        print("while")
        for n in range(0, nodes) :                    
            if n in graph.keys():
                # search for neighbor
                random_node = getNeighbor(graph, n, nodes)
                graph.get(n).append(random_node)
                file.write(str(n) + " -- " + str(random_node) + ";\n")
            else:   
                random_node = None  
                # node can not have herself as neighbors                   
                while random_node == n or random_node is None:                            
                    random_node = randint(0,nodes - 1)
                    # skip dual edges
                    if random_node in graph.keys():
                        if n in graph.get(random_node):
                            random_node = None
                
                graph[n] = [random_node]
                file.write(str(n) + " -- " + str(random_node) + ";\n")                   
            
            
            e +=  1
            if(e >= edges):
                break
            
            
    file.write("}")
    file.close()
    print(graph)

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
        
        
