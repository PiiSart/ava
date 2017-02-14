#!/usr/bin/python3
'''
Created on 25.10.2016
Start all nodes as a child process.

@author: Viktor Werle
'''


import multiprocessing as mp
from logger.logger import NodeLogger
from node.node import Node
from util.settings import Settings
from os import path


__NODES = {}
__FILE_ACCESS_MODE = "r"
__LOGGER = NodeLogger().getLoggerInstance("root");
__IDENT = "Starter -> "



def __readNodeInfos(fileName):
    '''
    Read node infos from a file, store these in a dictionary and start Nodes in a separate process.
    
    @param fileName: file, contains node informations on form <id> <ip:port> ex. 0 127.0.0.1:5000
    '''
    __LOGGER.debug(__IDENT + " read file: %s" %fileName)
    file = open(str(fileName), __FILE_ACCESS_MODE)
    
    for line in iter(lambda: file.readline(), ''):
        # split id
        buffer = line.split()
        node_id = buffer[0]
        
        # split ip and port
        buffer = buffer[1].split(":")
        node_ip = buffer[0]
        node_port = buffer[1]
    
        # save node in a list 
        __NODES[node_id] = {"id":node_id, "ip":node_ip, "port":node_port}
    
    #close file    
    file.close()    
    __LOGGER.debug(__IDENT + " readed nodes: %s" % __NODES)
   
def __startNodes():
    '''
    Start nodes as a child process
    '''
    if __pref.getElection() == False:
        __LOGGER.info(__IDENT + " start normal nodes ...")
        for i in range(0, len(__NODES)):
            process_list.append(mp.Process(target=Node, args=(str(i), )))
            process_list[i].start()
    else:
        __LOGGER.info(__IDENT + " start voter/candidate nodes ...")
        for i in range(0, len(__NODES)):
            process_list.append(mp.Process(target=Node, args=(str(i), )))                                    
            process_list[i].start()


def __createFile():
    FILE = "../conf/ts_id.txt"
    FILE_ACCESS_MODE = "w"
    
    PATH = path.join(path.dirname(path.abspath(__file__)), FILE)
    file = open(PATH, FILE_ACCESS_MODE)
    
    file.write("0")
    file.close()
    
  
if __name__ == '__main__':
    __createFile()
    __pref = Settings()
    __pref.loadSettings()
    # read node information
    __NODES = __pref.getNodeInfos()
    process_list = []
    # create nodes
    __startNodes()
         
    # wait for join        
    for i in range(0, len(process_list)):
        process_list[i].join()    




