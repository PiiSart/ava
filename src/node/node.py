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
from node import node_message
from threading import Lock



class Node():
    """
    Local node. 
    """
    
             
    def __init__(self, node_list, node_id):
        """
        Init Node
        
        @type node_list: dictionary
        @param node_list: avalable nodes
        
        @type id: string
        @param id: my node id
        """
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.NODE) 
        self.__pref = Settings()
        self.__pref.loadSettings()
        self.__whisper_count = 0
        self.__whisperer = []
        self.threadLock = Lock()                
        self.__config = node_list#json.loads(open(fileName).read());
        
        # eingegebene ID vorhanden?
        if not self.__checkID(node_id):
            pass # TODO: raise NodeException("ID " + str(node_id) + " ist nicht vorhanden! Verfuegbare IDs: " + str(self.__config.keys()));
        
        self.__ident = ("Node-ID-" + str(node_id) + " [PID:" + str(os.getpid()) + "] -> ")
                
        # uebernehme Node-Daten
        self.__LOGGER.debug(self.__ident + "save id: " + node_id);           
        self.__id = node_id;
        
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
        
        self.__receiver = Receiver(self.__ident, self)
        #self.__submitter = Submitter() 
        self.__start()              
                        
               
    def __start(self):
        '''
        Start node receiver in a thread.
        '''
        receiver_t = threading.Thread(target=self.__receiver.start, args=(self.__ip, self.__port))   
        self.__LOGGER.debug(self.__ident + "starterd ...")     
        receiver_t.start() 
        # send own ID on all neighbours
        self.notifyNeighbours("Meine id " + self.__id)
               
        receiver_t.join()
    
   
    def __del__(self):
        """
        Destroy Node object
        """
        pass
    
    def getID(self):
        return self.__id;
    
    def getPort(self):
        return self.__port;
    
    def getIP(self):
        return self.__ip; 
    
    def incWhisperCount(self):
        self.__whisper_count += 1
    
    def appendWhisperer(self, whisperer):
        self.__whisperer.append(whisperer)
        
    def resetWhisper(self):
        self.__whisper_count = 0
        self.__whisperer.clear()
    
    def __checkID(self, node_id): 
        """
        Check if Node id is in set.
        
        @param node_id: Node id
        @type node_id: int 
        @return: true if node_id in set, false if node_id not in set
        """       
        return str(node_id) in self.__config.keys();
    
    def __defineNeighbours(self, maxNeighbours):
        """
        Select random neighbours ids from a list.
        
        @param maxNeighbours: max number of neighbours
        @type maxNeighbours: int
        @return: random list of neighbours ids
        """
        counter = 0;
        neighbourList = [];
        
        # suche in der List nach zufaelligen Nachbarn-Ids
        while counter < maxNeighbours:
            neighbourId = "".join(random.choice(list(self.__config.keys())));            
            self.__LOGGER.debug(self.__ident + "random neighbour id: " + neighbourId);
            
            # Nachbar-Id muessen untereinander unterschiedlich sein, sowie ungleich eigner ID
            # Konvertierung zum String, damit der Vergleich korrekt funktioniert!
            if neighbourId not in neighbourList and str(neighbourId) != str(self.__id):
                neighbourList.append(neighbourId);
                counter += 1;
                
        return neighbourList;
    
    def notifyNeighbours(self, message):
        '''
        Send all neighbors his node id
        
        @param message: full message (with header and data)
        @type message: compare node_message
        '''
        self.__LOGGER.debug(self.__ident + "my neighbours: " + str(self.__neighbours))
        for i in self.__neighbours:
            Submitter().send_message(message, self.__id, self.__ip, self.__port, 
                str(self.__config[str(i)]["id"]), str(self.__config[str(i)]["ip"]), 
                str(self.__config[str(i)]["port"]))
    
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
    
    def getWhisperState(self, msg):
        '''
        Response a whisper state on requester.
        cm_true: if the node trust whisper
        cm_false: if the node not trust whisper
        
        @param msg: full message (with header and data)
        @type msg: compare node_message
        '''
        
        self.__LOGGER.info(self.__ident + " my whisperer: " + str(self.__whisperer))
        # trust them rumor ?
        if self.__whisper_count >= int(self.__pref.getTrust()):
            self.__LOGGER.debug(self.__ident + " im trust whisper: whisper_count " + str(self.__whisper_count) + " trust value " + self.__pref.getTrust())
            Submitter().send_message(node_message.TRUE, self.__id, self.__ip, self.__port,
                    msg[node_message.HEADER][node_message.SUBM_ID],
                    msg[node_message.HEADER][node_message.SUBM_IP],
                    msg[node_message.HEADER][node_message.SUBM_PORT])
        else:
            self.__ident + " im not trust whisper: whisper_count " + str(self.__whisper_count) + " trust value " + self.__pref.getTrust()
            Submitter().send_message(node_message.FALSE, self.__id, self.__ip, self.__port,
                    msg[node_message.HEADER][node_message.SUBM_ID],
                    msg[node_message.HEADER][node_message.SUBM_IP],
                    msg[node_message.HEADER][node_message.SUBM_PORT])
               
    
    def tellWhisperToNeighbors(self, message):
        '''
        Send on his neighbors a rumor.
        '''
        
        self.__whisperer.append(message[node_message.HEADER][node_message.SUBM_ID]) 
        self.__LOGGER.debug(self.__ident + " my neighbours " + str(self.__neighbours))
        for n in self.__neighbours: 
            if str(n) != str(message[node_message.HEADER][node_message.SUBM_ID]) and (str(n) not in self.__whisperer):
                self.__LOGGER.debug(self.__ident + "tell whisper on [" + n + "]")
                Submitter().send_message(node_message.WHISPER, 
                            message[node_message.HEADER][node_message.RECV_ID],
                            message[node_message.HEADER][node_message.RECV_IP],
                            message[node_message.HEADER][node_message.RECV_PORT],
                            n, self.__config[n]["ip"], self.__config[n]["port"])
        
    
    
    def getNeighbors(self):
        return self.__neighbours  
    
    def getNodeInfos(self):
        return self.__config
            
        

          
    
    