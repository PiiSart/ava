#!/usr/bin/python3
'''
Created on 25.10.2016

Node

@author: Viktor Werle
'''

import os
import threading
from .node_receiver import Receiver
from .node_submitter import Submitter
from logger.logger import NodeLogger
from util.settings import Settings
from node.node_message import Message, MsgType
from queue import PriorityQueue
from os import path
import time

class Node(object):
    """
    Local node. 
    """
    
    __FILE = "../../conf/ts_id.txt"
    __FILE_ACCESS_MODE = "rb+"
             
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
        self._LOGGER.debug(node_id + " My PID is: " + str(os.getpid()))
        self._pref = Settings()
        self._pref.loadSettings()
        
        self.__im_down = False
        self.__neighbours = []                
        self.__node_infos = self._pref.getNodeInfos()
        self.__total_nodes = self._pref.getNumberOfNodes()
        # vector time
        #self.__vector_time = self.__initVectorTime()
        self.__lamport_time = 0  
        self.__number_of_ack = 0
        self.__zero_counter = 0
        # queue
        self.__request_queue = PriorityQueue()
         
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
            self._LOGGER.error("not suported!")
            #self.__neighbours = self.__defineNeighbours(int(self._pref.getMaxNeighbors()));
            
        self._LOGGER.debug(self.__ident + "selected neighbors: " + str(self.__neighbours));
        
        if self._pref.getElection() == False:        
            self.__receiver = Receiver(self) 
            self.__start()              
                        
               
    def __start(self):
        '''
        Start node receiver in a thread.
        '''
        receiver_t = threading.Thread(target=self.__receiver.start, args=(self.__ip, self.__port))   
        self._LOGGER.debug(self.__ident + "starterd ...")     
        receiver_t.start() 
        # send own ID on all neighbours
        self.requestWriteAccess()
          
        receiver_t.join()
   
    
    #################################################################
    # public methods
    #################################################################
    def getID(self):
        return self.__id;
    
    def getIdent(self):
        return self.__ident
    
    def getPort(self):
        return self.__port;
    
    def getIP(self):
        return self.__ip; 
    
    def getLock(self):
        return self.__lock
    
    def getImDown(self):
        return self.__im_down
    
    def setImDown(self, vlaue):
        self.__im_down = vlaue
 
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
            
    def getLamportTime(self):
        '''
        Return the local lamport time.
        
        @return: local lamport time
        @type __lemport_time: integer
        '''
        return self.__lamport_time    
                 
    def incLamportTime(self, received_time=-1):
        '''
        Increment lamport time.
        
        @param received_time: received lamport time
        @type received_time: integer
        '''
        #self.__lock_time.acquire()
        if self.__lamport_time < received_time:
            self.__lamport_time = received_time
            
        self.__lamport_time += 1
        #self.__lock_time.release()
        return self.__lamport_time
    
       
    def requestWriteAccess(self):
        '''
        Send on all processes a request. 
        
        @param message: message to send
        @type message: compare node_message
        '''
        
        ts_list = []        
        time_copy = self.incLamportTime() 
        ts_list.append(time_copy)
        ts_list.append(int(self.__id))        
        self.__addWriteRequest(ts_list)        
            
        #for i in range(0, int(self._pref.getNumberOfNodes())):
        for node_id in self.__node_infos:
            #print("%s WWWW: %s " % (self.__ident, node_id))
            if int(node_id) != int(self.__id):
                self.send(node_id, MsgType.REQUEST, time_copy)
                
    
    def handleRequest(self, msg):
        '''
        Handle message type REQUEST.
        
        @param msg: received message
        @type msg: node_message.Message
        '''
        # add request to the queue 
        ts_pid_list = []       
        pid = int(msg.getSubmId())
        ts = int(msg.getLamportTime())        
        ts_pid_list.append(ts)
        ts_pid_list.append(pid)        
        self.__addWriteRequest(ts_pid_list)
                
        # send acknowledge
        l_time = self.incLamportTime()
        self.send(pid, MsgType.ACKNOWLEDGE, l_time)
        
        self.checkWriteAccess()
    
    def handleAcknowledge(self, msg):
        '''
        Count received acknowledges and check the write access.
        
        @param msg: received message object
        @type msg: node_message.Message
        '''  
        self.__number_of_ack += 1     
        self.checkWriteAccess()
        
    def handleRelease(self, msg):
        '''
        Remove fist element from queue.
        
        @param msg: received message object
        @type msg: node_message.Message
        '''
        if self.__zero_counter != 3:
            print("%s QUEUE FOR RELeASE: %s" % (self.__ident, list(self.__request_queue.queue)))
            # remove first element
            print("%s RELEASE: %s" % (self.getIdent(), self.__request_queue.get()))
            self.checkWriteAccess()
        
    def checkWriteAccess(self): 
        '''
        Check if node can write.
        '''   
        total_nodes = len(self.__node_infos)        
        q_size = int(self.__request_queue.qsize())
        self._LOGGER.info("%s TOTAL NODES: %s QUEUE_SIZE: %s ACK: %s" % (self.__ident, str(total_nodes), str(q_size), str(self.__number_of_ack)))
        if q_size == total_nodes and self.__number_of_ack == total_nodes - 1:
            self._LOGGER.warning("%s REQUEST QUEUE: %s" % (self.getIdent(), list(self.__request_queue.queue)))    
            
            ts_pid_list = self.__request_queue.get()            
                     
            if(ts_pid_list[1] == int(self.__id)):
                self.write(ts_pid_list)
            else:
                self.__addWriteRequest(ts_pid_list) 
            
    def write(self, ts_pid_list):
        '''
        Write in a file. Send release after writing.
        @param ts_pid_list: list with two values <lamport time> <process id>
        @type ts_pid_list: list<integer>
        '''
        PATH = path.join(path.dirname(path.abspath(__file__)), self.__FILE)
        file = open(PATH, self.__FILE_ACCESS_MODE)
        
        bytess = file.readline()
        str_buf = bytess.decode(encoding='utf_8', errors='strict')        
        number = int(str_buf)
        
        if number == 0:
            self.__zero_counter += 1
            
              
        if ts_pid_list[1] % 2 == 0:
            number -= 1
        else:
            number += 1
            
        if self.__zero_counter != 3:   
            file.seek(0,0)
            str_buf = str(number) + "\n"
            file.write(str_buf.encode(encoding='utf_8', errors='strict'))
            
        file.seek(0,2)
        str_buf = "ID: " + str(ts_pid_list[1]) + " Value: " + str(number)
        file.write(str_buf.encode(encoding='utf_8', errors='strict'))
        file.write(b"\n")
        file.close()
        
        if self.__zero_counter == 3:            
            # shutdown neighbor
            neighbor_id = self.__neighbours[0]
            self.send(str(neighbor_id), MsgType.QUIT, self.incLamportTime())
            self.__removeDownNodesFromNodeInfos(neighbor_id)
            self.__removeDownNodesFromQueue(neighbor_id)  
                                    
            # shutdown me
            self.send(self.__id, MsgType.QUIT, self.incLamportTime())
            self.__im_down = True

        if self.__zero_counter != 3:
            # send release        
            self.__number_of_ack = 0       
            for node_id in self.__node_infos:
                #print("%s WWWW: %s " % (self.__ident, node_id))
                if int(node_id) != int(self.__id):
                    self.send(node_id, MsgType.RELEASE, self.incLamportTime())
            # check write access
            self.requestWriteAccess()
        
    
    def handleImDown(self, msg):
        if self.__im_down == False:
            self.__removeDownNodesFromQueue(msg.getSubmId())
            self.__removeDownNodesFromNodeInfos(msg.getSubmId())
            print("%s QUEUE after REMOVE: %s" % (self.__ident, list(self.__request_queue.queue)))
            print("%s NODE_INFO after REMOVE: %s" % (self.__ident, self.__node_infos)) 
            self.__number_of_ack -= 1       
            self.checkWriteAccess()
    
        
    #################################################################      
    # private methods
    #################################################################
    
    def send(self, node_id, msg_type, l_time, msg_str=""):
        '''
        Send a message.
        
        @param node_id: id from received node
        @type node_id: string
        @param msg_type: message type
        @type msg_type: MsgType
        @param l_time: lamport time
        @type l_time: integer        
        @param msg_str: message string
        @type msg_str: string
        '''        
        msg_buf = Message() 
        msg_buf.setSubm(self.__id, self.__ip, self.__port)
        msg_buf.setRecv(str(self.__node_infos[str(node_id)]["id"]), 
                        str(self.__node_infos[str(node_id)]["ip"]), 
                        str(self.__node_infos[str(node_id)]["port"]))
        msg_buf.create(l_time, msg_type, msg_str)
        Submitter().send_message(self, msg_buf)
    
    
    def __removeDownNodesFromQueue(self, node_id):
        '''
        Remove from request queue all down processes.
        
        @param node_id: node id to be remove
        @type noed_id: integer
        '''
        tmp_pq = PriorityQueue()
        ts_pid_list = []
        # remove all processes from queue
        for index in range(self.__request_queue.qsize()):
            ts_pid_list = self.__request_queue.get()
            if int(node_id) != ts_pid_list[1]:
                tmp_pq.put(ts_pid_list)
        
        for index in range(tmp_pq.qsize()):
            ts_pid_list = tmp_pq.get()
            self.__request_queue.put(ts_pid_list)
        
    
    def __removeDownNodesFromNodeInfos(self, node_id):
        '''
        Remove  down node from node_info.
        
        @param node_id: node id to be remove
        @type noed_id: integer
        '''
        self.__node_infos.pop(str(node_id))
    
    def __addWriteRequest(self, ts_pid_list):
        '''
        Add to the request queue a request.
        
        @param ts_pid_list: a list with two values [ts, process id]
        @type ts_pid_list: integer list
        '''        
        self.__request_queue.put(ts_pid_list)
        
    def __del__(self):
        """
        Destroy Node object
        """
        pass     
