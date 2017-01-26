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
from abc import abstractmethod



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
        
        self._LOGGER = NodeLogger().getLoggerInstance(NodeLogger.NODE) 
        self.__ident = ("Node-ID-" + str(node_id) + " [PID:" + str(os.getpid()) + "] -> ")
        self._pref = Settings()
        self._pref.loadSettings()
        self.__rumor_count = 0
        self.__whisperer = []
        self.__neighbours = []                
        self.__node_infos = self._pref.getNodeInfos()
        # vector time
        self.__vector_time = self.__initVectorTime()        
        self._LOGGER.debug(self.__ident + " Vector time: " + str(list(self.__vector_time)))
        # echo algorithm
        self.__echo_counts = {} # {"cand_id": <integer>, ...}
        self.__first_link = {}  # {"cand_id": <node_id as a string>, ...}
        #self.__explorer = {}    # {"cand_id": <boolean>, ...}
        #self.__ready = {}       # {"cand_id": <boolean>, ...}
        
                   
        # apply node data
        self._LOGGER.debug(self.__ident + "save id: " + node_id);           
        self.__id = node_id;
        
        self._LOGGER.debug(self.__ident + "save port: " + str(self.__node_infos[node_id]["port"]));
        self.__port = self.__node_infos[node_id]["port"]
        
        self._LOGGER.debug(self.__ident + "save ip: " + self.__node_infos[node_id]["ip"]);
        self.__ip = self.__node_infos[node_id]["ip"];
        
        # define neighbors        
        if self._pref.isGraphviz() == True:
            neighbors_map = self._pref.getNeigborsMap()
            try:                            
                self.__neighbours = neighbors_map[self.__id]
                self._LOGGER.debug(self.__ident + " my neighbors are: " + str(self.__neighbours))
            except KeyError:
                #self.__neighbours = []
                self._LOGGER.warning(self.__ident + " has no neighbors!")
        else:
            self._LOGGER.debug(self.__ident + " max number of neighbors: " + str(self._pref.getMaxNeighbors()))
            self.__neighbours = self.__defineNeighbours(int(self._pref.getMaxNeighbors()));
            
        self._LOGGER.debug(self.__ident + "selected neighbors: " + str(self.__neighbours));
        
        # who i am? candidate/voter
        if self.__id in self._pref.getCandidateList():
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
        self._LOGGER.debug(self.__ident + "starterd ...")     
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
    
    def getExplorerState(self, cand_id):
        '''
        Get state of the explorer.
        True: node has the explorer message already received
        False: in another case
        
        @param cand_id: candidaten id, who initiate a campaign
        @type cand_id: string
        
        @return: True, if the node received an explorer. False in another case.
        @type __explorer[cand_id]: boolean 
        '''
        if cand_id in self.__first_link:
            return True
        else:
            return False
    
    #def setExplorerState(self, cand_id, state):
        '''
        Set the explorer state.
                
        @param state: explorer state
        @type state: boolean
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        '''
    #    self.__explorer[cand_id] = state
    
    def getFirstLinkId(self, cand_id):
        '''
        Get a first link (is a node id of which the node get a first explorer message) 
        related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @param cand_id: string
        
        @return: first link id or None if the candidate is not in the dictionary
        @type __first_link_id[cand_id]: string or None
        '''
        if cand_id in self.__first_link:
            return self.__first_link[cand_id]
        else:
            return None
    
    def setFirstLinkId(self, cand_id, f_link):
        '''
        Set a first link (is a node id of which the node get a first explorer message)
        related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        @param f_link_id: first link id
        @type f_link_id: string
        '''
        self.__first_link[cand_id] = f_link
        
    def deleteFirstLinkId(self, cand_id):
        '''
        Delete first link id.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        '''
        if cand_id in self.__first_link:
            self.__first_link.pop(cand_id)
        
    def getReadyState(self, cand_id):
        '''
        Get a state of echo algorithm related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        
        @return: state of campaign. True if the campaign is over or not exists and False if the campaign is still run. 
        @type __ready[cand_id]: boolean
        '''
        if cand_id in self.__ready:
            return False#return self.__ready[cand_id]
        else: # if cand_id not in the first link, than campaign doesn't exist
            return True
    
    #def setReadyState(self, cand_id, ready_state):
        '''
        Set a state of echo algorithm related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        @param ready: state of echo algorithm
        @type ready: boolean
        '''
    #    self.__ready[cand_id] = ready_state
    
    #def getEchoCounts(self, cand_id):
        '''
        Get a number of received echo's related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        
        @return: number echo's or None if the cand_id not in the dictionary
        @type __echo_counts[cand_id]: integer
        '''
    #    if cand_id in self.__echo_counts:
    #        return self.__echo_counts[cand_id]
    #    else:
    #        return None
    
    def incEchoCounter(self, cand_id):
        '''
        Increase a number of received echo's related to candidate.
        If the echo counter equals to number of neighbors, ready state will be set
        of True.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        '''      
        if cand_id in self.__echo_counts:
            self.__echo_counts[cand_id] += 1
            if self.__echo_counts[cand_id] == len(self.getNeighbors()):
                self.setReadyState(cand_id, True)
        else:
            self.__echo_counts[cand_id] = 1
            
    
    def resetEchoCounter(self, cand_id):
        '''
        Reset a number of received echo's from candidate with cand_id to 0.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        '''
        if cand_id in self.__echo_counts:
            self.__echo_counts[cand_id] = 0
        
    def getNeighbors(self):
        '''
        Return a list with neighbors.
        
        @return: List with neighbors
        @type self.__neighbours: list[string]
        '''
        return self.__neighbours  
    
    def getNodeInfos(self):
        '''
        Return a list with nodes informations (id, ip, port)
        
        @return: List whti nodes informations
        @type self.__node_infos: list[string]
        '''
        return self.__node_infos
    
    def getVectorTime(self):
        '''
        Return local vector time
        
        @return: local vector time
        @type self.__vector_time: list[integer]
        '''
        return self.__vector_time      
    
    def getEchoCounter(self):
        '''
        Return number of echo's
        
        @return: number of received echo's
        @type self.__echo_counter: integer
        '''
        return self.__echo_counter
                    
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
        for i in range(int(self._pref.getNumberOfNodes())):
            if i != int(self.__id):
                self.__vector_time[i] = max(self.__vector_time[i], new_time[i])
        return self.__vector_time
    
    def notifyNeighbours(self, message):
        '''
        Send on all neighbors his own node id
        
        @param message: full message (with header and data)
        @type message: compare node_message
        '''
        self._LOGGER.debug(self.__ident + "my neighbours: " + str(self.__neighbours))
        msg_buf = Message()        
        for i in self.__neighbours:
            msg_buf.setSubm(self.__id, self.__ip, self.__port)
            msg_buf.setRecv(str(self.__node_infos[str(i)]["id"]), str(self.__node_infos[str(i)]["ip"]), 
                         str(self.__node_infos[str(i)]["port"]))
            msg_buf.create(self.__vector_time, MsgType.MESSAGE, message)
            Submitter().send_message(self, msg_buf)
       
    def getRumorState(self, msg):
        '''
        Response a rumor state on requester.
        cm_true: if the node trust rumor
        cm_false: if the node not trust rumor
        
        @param msg: full message (with header and data)
        @type msg: compare node_message
        '''
        
        self._LOGGER.info(self.__ident + " my whisperer: " + str(self.__whisperer))
        msg_buf = Message()
        msg_buf.setSubm(self.__id, self.__ip, self.__port)
        msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
        
        # trust them rumor ?
        if self.__rumor_count >= int(self._pref.getTrust()):
            self._LOGGER.debug(self.__ident + " i'm trust rumor: rumor_count " + str(self.__rumor_count) + " trust value " + self._pref.getTrust())            
            msg_buf.create(self.__vector_time, MsgType.RUMOR_STATE, MsgType.TRUE)            
        else:
            self._LOGGER.debug(self.__ident + " i'm not trust rumor: whisper_count " + str(self.__rumor_count) + " trust value " + self._pref.getTrust())
            msg_buf.create(self.__vector_time, MsgType.RUMOR_STATE, MsgType.FALSE)            
        Submitter().send_message(self, msg_buf)       
    
    def tellRumorToNeighbors(self, message):
        '''
        Send on his neighbors a rumor.
        '''        
        self.__whisperer.append(message.getSubmId()) 
        self._LOGGER.debug(self.__ident + " my neighbours " + str(self.__neighbours))
        for n in self.__neighbours: 
            if str(n) != message.getSubmId() and (str(n) not in self.__whisperer):
                self._LOGGER.debug(self.__ident + "tell whisper on [" + n + "]")
                msg_buf = Message()
                msg_buf.setSubm(self.__id, self.__ip, self.__port)
                msg_buf.setRecv(n, self.__node_infos[n]["ip"], self.__node_infos[n]["port"])
                msg_buf.init(self.__vector_time, MsgType.RUMOR, message.getMsg())
                Submitter().send_message(self, msg_buf)
    
    
    @abstractmethod
    def echo(self, msg = None):
        '''
        Handle echo messages.
        '''
        pass
    
       
    # private methods
       
    def __initVectorTime(self):
        '''
        Initialized local vector time with 0.
        
        @return: local vector time
        @type vector: list[integer]
        '''
        vector = []
        for i in range(0, int(self._pref.getNumberOfNodes())):
            vector.append(i - i) # init with zero
        return vector
    
    def __checkID(self, node_id): 
        """
        Check if node id is in node list.
        
        @param node_id: node id
        @type node_id: int 
        @return: true if node list contain the node id, false in the oder case
        """       
        return str(node_id) in self.__node_infos.keys();
    
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
            neighbourId = "".join(random.choice(list(self.__node_infos.keys())));            
            self._LOGGER.debug(self.__ident + "random neighbor id: " + neighbourId);
            
            # Nachbar-Id muessen untereinander unterschiedlich sein, sowie ungleich eigner ID
            # Konvertierung zum String, damit der Vergleich korrekt funktioniert!
            if neighbourId not in neighbourList and str(neighbourId) != str(self.__id):
                neighbourList.append(neighbourId);
                counter += 1;
                
        return neighbourList;
    
    def __setNodeType(self):
        '''
        Set and initialized the node type.
        
        candidate node - if node id is in candidate list
        voter node - if node id is not in candidate list       
        '''
        
        # node is a candidate
        if int(self.__id) in self._pref.getCandidateList():
            self.__nodeType = NodeType.CANDIDATE
        # node is a voter
        else:
            self.__nodeType = NodeType.VOTER
            self.__initVoter()
    
    
    
        
    
    