#!/usr/bin/python3
'''
Created on 25.10.2016

Node

@author: Viktor Werle
'''

import os
import random
import threading
from .node_receiver import Receiver
from .node_submitter import Submitter
from logger.logger import NodeLogger
from util.settings import Settings
from node.node_message import Message, MsgType
from node.node_type import NodeType



class Node():
    """
    Local node. 
    """
    
             
    def __init__(self, node_id):
        """
        Init Node
        
        @type node_list: dictionary
        @param node_list: avalable nodes
        
        @type id: string
        @param id: my node id
        """
        
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.NODE) 
        self.__ident = ("Node-ID-" + str(node_id) + " [PID:" + str(os.getpid()) + "] -> ")
        self.__pref = Settings()
        self.__pref.loadSettings()
        self.__rumor_count = 0
        self.__count_voters_responses = 0
        self.__nodeType = " "
        self.__whisperer = []                
        self.__config = self.__pref.getNodeInfos()
        self.__vector_time = self.__initVectorTime()        
        self.__LOGGER.debug(self.__ident + " Vector time: " + str(list(self.__vector_time)))
        
                   
        # apply node data
        self.__LOGGER.debug(self.__ident + "save id: " + node_id);           
        self.__id = node_id;
        # set node type (voter or candidate)
        self.__setNodeType()
        
        self.__LOGGER.debug(self.__ident + "save port: " + str(self.__config[node_id]["port"]));
        self.__port = self.__config[node_id]["port"]
        
        self.__LOGGER.debug(self.__ident + "save ip: " + self.__config[node_id]["ip"]);
        self.__ip = self.__config[node_id]["ip"];
        
        # define neighbors        
        if self.__pref.isGraphviz() == True:
            self.__neighbors_map = self.__pref.getNeigborsMap()
            try:                            
                self.__neighbours = self.__neighbors_map[self.__id]
                self.__LOGGER.debug(self.__ident + " my neighbors are: " + str(self.__neighbours))
            except KeyError:
                self.__neighbours = []
                self.__LOGGER.warning(self.__ident + " has no neighbors!")
        else:
            self.__LOGGER.debug(self.__ident + " max number of neighbors: " + str(self.__pref.getMaxNeighbors()))
            self.__neighbours = self.__defineNeighbours(int(self.__pref.getMaxNeighbors()));
            
        self.__LOGGER.debug(self.__ident + "selected neighbors: " + str(self.__neighbours));
        
        # who i am? candidate/voter
        if self.__id in self.__pref.getCandidateList():
            # i am candidate
            pass
        else:
            # i am voter
            pass
        
        self.__receiver = Receiver(self) 
        #self.__start()              
                        
               
    def start(self):
        '''
        Start node receiver in a thread.
        '''
        receiver_t = threading.Thread(target=self.__receiver.start, args=(self.__ip, self.__port))   
        self.__LOGGER.debug(self.__ident + "starterd ...")     
        receiver_t.start() 
        # send own ID on all neighbours
        self.notifyNeighbours("my id is " + self.__id)
               
        receiver_t.join()
    
   
    def __del__(self):
        """
        Destroy Node object
        """
        pass
    
    # public methods
    def getID(self):
        return self.__id;
    
    def getIdent(self):
        return self.__ident
    
    def getPort(self):
        return self.__port;
    
    def getIP(self):
        return self.__ip; 
    
    def getNeighbors(self):
        return self.__neighbours  
    
    def getNodeInfos(self):
        return self.__config
    
    def getVectorTime(self):
        return self.__vector_time
    
    def getNodeType(self):
        return self.__nodeType
    
    def getCountVotersResponse(self):
        return self.__count_voters_responses
    
    def incRumorCount(self):
        '''
        Counts rumors
        '''
        self.__rumor_count += 1
    
    def appendWhisperer(self, whisperer):
        '''
        Append node id to the rumor list from the node, who told the rumor
        '''
        self.__whisperer.append(whisperer)
             
    def incLocalTime(self):
        '''
        Increments in time-vector his own time
        '''
        self.__vector_time[int(self.__id)] += 1
    
    def setVectorTimeByReceive(self, new_time):
        '''
        Adjust vector time by receive.
        Own time: + 1
        Other: max.(local time, received time)
        
        @param new_time: received time
        @type new_time: list [1, 2, ....]
        '''
        # set local time
        self.incLocalTime()
        # change time another nodes, except own local time
        for i in range(int(self.__pref.getNumberOfNodes())):
            if i != int(self.__id):
                self.__vector_time[i] = max(self.__vector_time[i], new_time[i])
        return self.__vector_time
    
    def notifyNeighbours(self, message):
        '''
        Send on all neighbors his own node id
        
        @param message: full message (with header and data)
        @type message: compare node_message
        '''
        self.__LOGGER.debug(self.__ident + "my neighbours: " + str(self.__neighbours))
        msg_buf = Message()        
        for i in self.__neighbours:
            msg_buf.init(self, self.__vector_time, str(self.__config[str(i)]["id"]), str(self.__config[str(i)]["ip"]), 
                         str(self.__config[str(i)]["port"]), MsgType.MESSAGE, message)
            Submitter().send_message(self, msg_buf)
            
    
    def delNeighbours(self, node_id):
        try:
            self.__LOGGER.debug(self.__ident + "del node[" + node_id + "] ...")
            index = self.__neighbours.index(int(node_id), )
            self.__neighbours.pop(index)
            self.__LOGGER.debug(self.__ident + "remaining neighbours: " + self.__neighbours)
        except TypeError:
            self.__LOGGER.info(self.__ident + "node[" + node_id + "]: not exist ...")
        except ValueError:
            self.__LOGGER.debug(self.__ident + "node[" + node_id + "]: is not my neighbours ...")
    
    def getRumorState(self, msg):
        '''
        Response a rumor state on requester.
        cm_true: if the node trust rumor
        cm_false: if the node not trust rumor
        
        @param msg: full message (with header and data)
        @type msg: compare node_message
        '''
        
        self.__LOGGER.info(self.__ident + " my whisperer: " + str(self.__whisperer))
        msg_buf = Message()
        # trust them rumor ?
        if self.__rumor_count >= int(self.__pref.getTrust()):
            self.__LOGGER.debug(self.__ident + " i'm trust rumor: rumor_count " + str(self.__rumor_count) + " trust value " + self.__pref.getTrust())            
            msg_buf.init(self, self.__vector_time, msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort(), MsgType.RUMOR_STATE, MsgType.TRUE)            
        else:
            self.__LOGGER.debug(self.__ident + " i'm not trust rumor: whisper_count " + str(self.__rumor_count) + " trust value " + self.__pref.getTrust())
            msg_buf.init(self, self.__vector_time, msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort(), MsgType.RUMOR_STATE, MsgType.FALSE)            
        Submitter().send_message(self, msg_buf)       
    
    def tellRumorToNeighbors(self, message):
        '''
        Send on his neighbors a rumor.
        '''
        
        self.__whisperer.append(message.getSubmId()) 
        self.__LOGGER.debug(self.__ident + " my neighbours " + str(self.__neighbours))
        for n in self.__neighbours: 
            if str(n) != message.getSubmId() and (str(n) not in self.__whisperer):
                self.__LOGGER.debug(self.__ident + "tell whisper on [" + n + "]")
                msg_buf = Message()
                msg_buf.init(self, self.__vector_time, n, self.__config[n]["ip"], self.__config[n]["port"], MsgType.RUMOR, message.getMsg())
                Submitter().send_message(self, msg_buf)
    
    def incCountVotersResponses(self):
        self.__count_voters_responses += 1
    
    def startVoting(self):
        '''
        Start random either voting or campaign
        0 - start vote for me
        1 - start campaign
        '''
        # reset voter response counter
        self.__count_voters_responses = 0
        
        choose = random.randint(0,1)
        
        # start voting
        self.__LOGGER.debug("%s start voting", self.__ident)
        for n in self.__neighbours:
            msg = Message()
            if choose == 0:
                msg.init(Node, self.__vector_time, n, self.__config[n]["ip"], self.__config[n]["port"], MsgType.VOTE_FOR_ME, " i am super, vote for me!")
            else:
                msg.init(Node, self.__vector_time, n, self.__config[n]["ip"], self.__config[n]["port"], MsgType.CAMPAIGN, " i am super, vote for me!")
                
            Submitter().send_message(Node, msg)
 
    
    # private methods
       
    def __initVectorTime(self):
        vector = []
        for i in range(0, int(self.__pref.getNumberOfNodes())):
            vector.append(i - i) # init with zero
        return vector
    
    def __checkID(self, node_id): 
        """
        Check if node id is in node list.
        
        @param node_id: node id
        @type node_id: int 
        @return: true if node list contain the node id, false in the oder case
        """       
        return str(node_id) in self.__config.keys();
    
    def __defineNeighbours(self, maxNeighbours):
        """
        Select random neighbors id's from a list.
        
        @param maxNeighbours: max number of neighbors
        @type maxNeighbours: int
        @return: random list of neighbors id's
        """
        counter = 0;
        neighbourList = [];
        
        # suche in der List nach zufaelligen Nachbarn-Ids
        while counter < maxNeighbours:
            neighbourId = "".join(random.choice(list(self.__config.keys())));            
            self.__LOGGER.debug(self.__ident + "random neighbor id: " + neighbourId);
            
            # Nachbar-Id muessen untereinander unterschiedlich sein, sowie ungleich eigner ID
            # Konvertierung zum String, damit der Vergleich korrekt funktioniert!
            if neighbourId not in neighbourList and str(neighbourId) != str(self.__id):
                neighbourList.append(neighbourId);
                counter += 1;
                
        return neighbourList;
    
    def __setNodeType(self):
        '''
        Set node type.
        
        candidate node - if node id is in candidate list
        voter node - if node id is not in candidate list       
        '''
        
        if int(self.__id) in self.__pref.getCandidateList():
            self.__nodeType = NodeType.CANDIDATE
        else:
            self.__nodeType = NodeType.VOTER
    
    
    def __initVoter(self):
        
        # candidate is my neighbor
        pass 
    
    def __initCandidate(self):
        pass