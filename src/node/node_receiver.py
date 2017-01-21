#!/usr/bin/python3
'''
Created on 03.11.2016

Node receiver. Receive messages from another nodes.

@author: Viktor Werle
'''

import zmq
from zmq.backend.cython.constants import PULL

from logger.logger import NodeLogger
from node.node_message import Message, MsgType



class Receiver(object):
    '''
    Simple node receiver for receiving the messages. 
    Implemnts with 0MQ library.
    '''
                 
    def __init__(self, Node):
        '''
        Init receiver
        '''           
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.RECEIVER);
        self.__node = Node
        self.__knowWhisper = False
       
    def start(self, ip, port):
        '''
        Start the loop to receive the messages from client. The server will be 
        stopped by the message 'quit'!
        '''      
        self.__LOGGER.debug(self.__node.getIdent() + "init receiver ...")
        self.__message = " "
        
        # create ZMQ context
        self.__context = zmq.Context()
        
        # create ZMQ_REP Socket (incoming strategie: Faire-queued)
        self.__socket = self.__context.socket(PULL)
        # bind socket to ip and port
        self.__socket.bind("tcp://" + str(ip) + ":" + str(port))
        
        self.__LOGGER.debug(self.__node.getIdent() + "receiver is started: ip - " + str(ip) + " - port - " + str(port) + "\n")
        
        while True:
            # receive message
            msg_str = self.__socket.recv_string()
            
            # create message obj
            self.__msg = Message()
            # import values from json string
            self.__msg.toMessage(msg_str)
            # update vector time
            self.__msg.setVectorTime(self.__node.setVectorTimeByReceive(self.__msg.getVectorTime()))
             
            self.__LOGGER.info(self.__getLogString(self.__msg))
                        
            # shutdown receiver, if message = node_message.QUIT
            if self.__msg.getMsgType() == MsgType.QUIT:                
                self.__LOGGER.info(self.__node.getIdent() + "i am down ... :-(")
                break
            # whisper
            if(self.__msg.getMsgType() == MsgType.RUMOR):
                if  self.__knowWhisper == False:
                    self.__LOGGER.debug(self.__node.getIdent() + " im not know rumor!")
                    self.__knowWhisper = True
                    self.__node.incWhisperCount()
                    #msg = self.__message
                    self.__node.tellWhisperToNeighbors(self.__msg)
                
                else:
                    #msg = self.__message
                    self.__node.appendWhisperer(self.__msg.getSubmId())                    
                    self.__node.incWhisperCount()
            # rumor state
            if self.__msg.getMsgType() == MsgType.RUMOR_STATE:
                #msg = self.__message
                self.__node.getWhisperState(self.__msg)
                    
        self.__LOGGER.debug(self.__node.getIdent() + "shutdown receiver: ip - " + str(ip) + " port - " + str(port) + " ...")
        self.__clear()        
        self.__LOGGER.debug(self.__node.getIdent() + "receiver is down!\n")
    
    def __clear(self):
        '''
        Close socket connection and destroy 0MQ context
        '''
        self.__LOGGER.debug(self.__node.getIdent() + "close socket ...")
        self.__socket.close()
        self.__LOGGER.debug(self.__node.getIdent() + "destroy context ...")
        self.__context.destroy()
    
    def __getLogString(self, msg):
        ident = self.__node.getIdent()
        subm_id = msg.getSubmId()
        
        recv_str = ident + " receive message from [" + subm_id + "]: " + str(msg)
        return recv_str
        
        
        
    def __del__(self):
        '''        
        '''
        pass
        
    
        
            
            
            
