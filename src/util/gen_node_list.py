#!/usr/bin/python3
'''
Created on 13.12.2016
Create a file with node informations.

@author: Viktor Werle
'''

import sys


__FILE_NAME = "../conf/node_list.txt"
__FILE_ACCESS_MODE = "w+"
__NODE_IP = "127.0.0.1"
__START_PORT = 5000

def __generate(count):
    file = open(__FILE_NAME, __FILE_ACCESS_MODE)
    for i in range(0, int(count)):
        file.write(str(i) + " " + __NODE_IP + ":" + str(__START_PORT + i) + "\n")
    file.close()   

if __name__ == '__main__':
    if len(sys.argv) > 1:
        __generate(int(sys.argv[1]))       
        
    else:
        print("Usage: gen_node_list [number of nodes]")
        
        
