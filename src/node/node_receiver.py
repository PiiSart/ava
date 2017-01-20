#!/usr/bin/python3
'''
Created on 03.11.2016

Node receiver. Receive messages from another nodes.

@author: Viktor Werle
'''

import zmq
from zmq.backend.cython.constants import PULL

from logger.logger import NodeLogger
from node import node_message
#from node.node_submitter import Submitter
#import node


class Receiver(object):
    '''
    Simple node receiver for receiving the messages. 
    Implemnts with 0MQ library.
    '''
                   
    def __init__(self, ident, Node):
        '''
        Init receiver
        '''           
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.RECEIVER);
        self.__ident = str(ident) 
        self.__node = Node
        self.__knowWhisper = False
       
    def start(self, ip, port):
        '''
        Start the loop to receive the messages from client. The server will be 
        stopped by the message 'quit'!
        '''      
        self.__LOGGER.debug(self.__ident + "init receiver ...")
        self.__message = " "
        
        # create ZMQ context
        self.__context = zmq.Context()
        # send timeout for confirm a message
        #self.__context.setsockopt(LINGER, node_message.LINGER_TIME)
        #self.__context.setsockopt(RCVTIMEO, 5000)
        # create ZMQ_REP Socket (incoming strategie: Faire-queued)
        self.__socket = self.__context.socket(PULL)
        # bind socket to ip and port
        self.__socket.bind("tcp://" + str(ip) + ":" + str(port))
        
        self.__LOGGER.debug(self.__ident + "receiver is started: ip - " + str(ip) + " - port - " + str(port) + "\n")
        
        while True:
            # receive message
            self.__message = node_message.convMessageStrToObj(self.__socket.recv_string()) 
            self.__LOGGER.info(node_message.toReceivedStr(self.__ident, self.__message))
            
            # confirm message @deprecated is not necessary
            '''
            self.__LOGGER.debug(self.__ident +  "confirm message from " + self.__message[node_message.HEADER][node_message.SUBM_ID])
            self.__socket.send_string(node_message.createMessageStr(self.__node.getID(), self.__node.getIP(), 
                self.__node.getPort(), self.__message[node_message.HEADER][node_message.SUBM_ID], 
                self.__message[node_message.HEADER][node_message.SUBM_IP], 
                self.__message[node_message.HEADER][node_message.SUBM_PORT], node_message.OK))           
            '''
            # shutdown receiver, if message = node_message.QUIT
            if(str(self.__message[node_message.DATA][node_message.MSG]) == str(node_message.QUIT)):                
                self.__LOGGER.info(self.__ident + "i am down ... :-(")
                break
            # whisper
            if(str(self.__message[node_message.DATA][node_message.MSG]) == str(node_message.WHISPER)):
                if  self.__knowWhisper == False:
                    self.__LOGGER.debug(self.__ident + " im not know rumor!")
                    self.__knowWhisper = True
                    #self.__node.threadLock.acquire()
                    self.__node.incWhisperCount()
                    #self.__node.threadLock.release()
                    msg = self.__message
                    #self.__node.threadLock.acquire()
                    self.__node.tellWhisperToNeighbors(msg)
                    #self.__node.threadLock.release()
                
                else:
                    msg = self.__message
                    self.__node.appendWhisperer(msg[node_message.HEADER][node_message.SUBM_ID])                    
                    self.__node.incWhisperCount()
            # whisper state
            if(str(self.__message[node_message.DATA][node_message.MSG]) == str(node_message.WHISPER_STATE)):
                msg = self.__message
                self.__node.getWhisperState(msg)
            # reset
            if(str(self.__message[node_message.DATA][node_message.MSG]) == str(node_message.RESET_WHISPER)):
                self.__knowWhisper = False
                self.__node.resetWhisper()
        
        self.__LOGGER.debug(self.__ident + "shutdown receiver: ip - " + str(ip) + " port - " + str(port) + " ...")
        self.__clear()        
        self.__LOGGER.debug(self.__ident + "receiver is down!\n")
    
    def __clear(self):
        '''
        Close socket connection and destroy 0MQ context
        '''
        self.__LOGGER.debug(self.__ident + "close socket ...")
        self.__socket.close()
        self.__LOGGER.debug(self.__ident + "destroy context ...")
        self.__context.destroy()
    
    
    
    def __del__(self):
        '''        
        '''
        pass
        
    
        
            
            
            
