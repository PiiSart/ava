#!/usr/bin/python3
'''
Created on 25.10.2016
Start all nodes as a child process.

@author: Viktor Werle
'''


import multiprocessing as mp
from logger.logger import NodeLogger
from node.node import Node
from node.voter_node import Voter
from node.candidate_node import Candidate
from node.node_submitter import Submitter
from util.settings import Settings
from aptdaemon.utils import deprecated
from node.candidate_node import Candidate



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
    __LOGGER.info(__IDENT + " start nodes ...")
    
    if __pref.getElection() == False:
        for i in range(0, len(__NODES)):
            node = Node(str(i))
            process_list.append(mp.Process(target=node.start))#, args=(str(i), )))
            process_list[i].start()
    else:
        for i in range(0, len(__NODES)):
            if i in __pref.getCandidateList():
                node = Candidate(str(i))
            else:
                node = Voter(str(i))
                
            process_list.append(mp.Process(target=node.start))#, args=(str(i), )))
            process_list[i].start()
  
if __name__ == '__main__':
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




