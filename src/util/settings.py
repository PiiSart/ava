#!/usr/bin/python3
'''
Created on 14.01.2017

Node settings, save all Setting.

@author: Viktor Werle
'''

from os import path
import re
from logger.logger import NodeLogger


class Settings(object):
    '''
    Administered settings
    '''
    
    __FILE = "../../conf/settings.txt"
    __FILE_ACCESS_MODE = "r"
    
    __IDENT = "Settings -> "
    
    def __init__(self):
        '''
        Constructor
        '''      
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.ROOT)
        self.__NEIGHBORS_MAP = {}
        self.__NODES_INFOS = {}
        self.__OPTIONS = {
            "GRAPHVIZ": self.__setGraphviz,
            "GRAPHVIZ_FILE": self.__setGraphvizFile,
            "NODE_FILE": self.__setNodeFile,
            "MAX_NEIGHBORS": self.__setMaxNeighbors,
            "TRUST" : self.__setTrust,
            "NODES" : self.__setNumberOfNodes,
            "EDGES" : self.__setNumberOfEdges,
            "LINGER_TIME" : self.__setLingerTime,
            "RCVTIMEO_TIME" : self.__setRcvtimeoTime,
            "CANDIDATE" : self.__addCandidate,
            "ELECTION"  : self.__setElection,
            "VEC_TIME_TERMINATION" : self.__setVecTimeTermination,       
        }
        self.__TRUST = 0
        self.__NUMBER_OF_NODES = 0
        self.__NUMBER_OF_EDGES = 0
        self.__LINGER_TIME = -1
        self.__RCVTIMEO_TIME = -1
        self.__CANDIDATE = []
        self.__ELECTION = 0
        self.__VEC_TIME_TERMINATION = 0
               
        
    def loadSettings(self):
        '''
        Load setting from settin-file
        '''
        PATH = path.join(path.dirname(path.abspath(__file__)), self.__FILE)#path.abspath(self.__FILE)
        
        file = open(PATH, self.__FILE_ACCESS_MODE)
        for line in iter(lambda: file.readline(), ''):
            self.__parse(line)
        file.close()
        
        self.__readNodeInfosGraphviz()
        self.__readNodeInfos()
        
            
    def __parse(self, line):
        '''
        Parse the line and save settings values
        '''
        # skip comment and empty lines
        line = line.strip()
        if line and (line[0] != '#'):
            buf = line.split()
            if len(buf) >= 2 and buf[1].strip():
                opt = self.__OPTIONS[buf[0]]
                opt(buf[1])                         
            
              
    def __setGraphviz(self, value):
        if str(value) == "0":
            self.__graphviz = False
        else:
            self.__graphviz = True
    
    def isGraphviz(self):
        try:
            return self.__graphviz
        except AttributeError:
            return None
    
    def __setGraphvizFile(self, value):
        self.__graphviz_file = path.join(path.dirname(path.abspath(__file__)), value)
        
    def getGraphvizFile(self):
        try:
            return self.__graphviz_file
        except AttributeError:
            return None
    
    def __setNodeFile(self, value):
        self.__node_file = path.join(path.dirname(path.abspath(__file__)), value)    
        
    def getNodeFile(self):
        try:
            return self.__node_file
        except AttributeError:
            return None 
    
    def getNodeInfos(self):
        return self.__NODES_INFOS
    
    def delNodeInfo(self, node_id):
        print("NODE_ID: " + str(node_id))
        self.__NODES_INFOS.pop(str(node_id))
        self.__NUMBER_OF_NODES -= 1
        print("NUM OF N: "+ str(self.__NUMBER_OF_NODES))
    
    def getNeigborsMap(self):
        return self.__NEIGHBORS_MAP
    
    
    def __setMaxNeighbors(self, value):
        self.__max_neighbors = value
        
    def getMaxNeighbors(self):
        try:
            return self.__max_neighbors
        except AttributeError:
            return 3
         
    def __setTrust(self, value):
        self.__TRUST = value
    
    def getTrust(self):
        return self.__TRUST
    
    def __setNumberOfNodes(self, value):
        self.__NUMBER_OF_NODES = int(value)
        
    def getNumberOfNodes(self):
        return self.__NUMBER_OF_NODES
    
    def __setNumberOfEdges(self, value):
        self.__NUMBER_OF_EDGES = value
        
    def getNumberOfEdges(self):
        return self.__NUMBER_OF_EDGES
    
    def __setLingerTime(self, value):
        self.__LINGER_TIME = value
    
    def getLingerTime(self):
        return self.__LINGER_TIME
    
    def __setRcvtimeoTime(self, value):
        self.__RCVTIMEO_TIME = value
    
    def getRcvtimeoTime(self):
        return self.__RCVTIMEO_TIME
    
    def __addCandidate(self, value):
        self.__CANDIDATE.append(value)
    
    def __setElection(self, value):
        self.__ELECTION = int(value)
    
    def getElection(self):
        if self.__ELECTION == 0:
            return False
        return True
    
    def __setVecTimeTermination(self, value):
        self.__VEC_TIME_TERMINATION = value
        
    def getVecTimeTermination(self):
        return self.__VEC_TIME_TERMINATION
    
    def getCandidateList(self):
        '''
        Return a candidate list with two candidates.
        
        @return: candidate list
        @type self.__CANDIDATE: list[string] list size 2
        '''
        return self.__CANDIDATE
                 
    def __readNodeInfosGraphviz(self):    
        '''
        Read node infos from a graphviz file, store these in a dictionary.
        
        @param fileName: file, contains node informations on form <id> <ip:port> ex. 0 127.0.0.1:5000
        '''
        
        file = open(str(self.getGraphvizFile()), self.__FILE_ACCESS_MODE)
        
        for line in iter(lambda: file.readline(), ''):
            # split line
            buffer = line.split()
             
            # check needed line (first sign must be a number)
            prog = re.compile("[0-9]")
            result = prog.match(buffer[0])
            if result:
                self.__LOGGER.debug(self.__IDENT + " readed line: " + str(buffer))
                neighbour = str(buffer[2])
                neighbour = neighbour.split(";")
                # 1 -- 2: 2 is neighbor of 1 and 1 is neighbor of 2
                self.__addNeighbor(buffer[0], neighbour[0])
                self.__addNeighbor(neighbour[0], buffer[0])          
        
        #close file    
        file.close()  
        self.__LOGGER.debug(self.__IDENT + " node neighbors map: " + str(  self.__NEIGHBORS_MAP))
    
    def __addNeighbor(self, node, neighbor): 
        '''
        Add a neighbor in the neighbor map
        '''       
        self.__LOGGER.debug(self.__IDENT + "node: " + node + " neighbor: " + neighbor)
        # node is in the dictionary
        if str(node) in self.__NEIGHBORS_MAP.keys():
            if str(neighbor) not in self.__NEIGHBORS_MAP[node]:
                self.__NEIGHBORS_MAP[node].append(neighbor)
        # node is not in the dictionary
        else:
            self.__NEIGHBORS_MAP[node] = [neighbor]
        
    def __readNodeInfos(self):    
        '''
        Read node infos from a file, store these in a dictionary and start Nodes in a separate process.
        
        @param fileName: file, contains node informations on form <id> <ip:port> ex. 0 127.0.0.1:5000
        '''
        
        file = open(str(self.getNodeFile()), self.__FILE_ACCESS_MODE)
        
        for line in iter(lambda: file.readline(), ''):
            # split id
            buffer = line.split()
            node_id = buffer[0]
            
            # split ip and port
            buffer = buffer[1].split(":")
            node_ip = buffer[0]
            node_port = buffer[1]
        
            # save node in a list
            self.__NODES_INFOS[node_id] = {"id":node_id, "ip":node_ip, "port":node_port}
        
        #close file    
        file.close() 
        self.__LOGGER.debug(self.__IDENT + " node informations: " + str(self.__NODES_INFOS))
        
    def resetSettings(self):
        self.__NODES_INFOS = {}
        self.__NEIGHBORS_MAP = {}
    