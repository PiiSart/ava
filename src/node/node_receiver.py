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
        self.__quit = False
        self.__knowRumor = False
        
        # message handler
        self.__MSG_HANDLER = {
            MsgType.QUIT : self.__shutdownHandler,
            MsgType.MESSAGE : self.__messageHandler,
            MsgType.RUMOR : self.__rumorHandler,
            MsgType.RUMOR_STATE : self.__rumorStateHandler
        }
       
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
        
        while self.__quit == False:
            # receive message
            msg_str = self.__socket.recv_string()
            
            # create message obj
            self.__msg = Message()
            # import values from json string
            self.__msg.toMessage(msg_str)
            # update vector time
            self.__msg.setVectorTime(self.__node.setVectorTimeByReceive(self.__msg.getVectorTime()))
            # print message to STDOUT
            self.__LOGGER.info(self.__getLogString(self.__msg))
            # handle message
            try:                       
                self.__receiverHandler(self.__msg)
            except KeyError:
                self.__LOGGER.error(self.__node.getIdent() + " unknown message type [" + self.__msg.getMsgType() + "]")
                    
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
        
    
    def __receiverHandler(self, msg):
        '''
        Handle incoming messages based on MsgType's
        
        @param msg: receivd message
        @type msg: NodeMessage
        '''   
        # call handler based on MsgType
        handler = self.__MSG_HANDLER[msg.getMsgType()]
        handler(msg)
    
    def __shutdownHandler(self, msg):
        '''
        Handle MsgType.QUIT
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__quit = True
        self.__LOGGER.info(self.__node.getIdent() + "i am down ... :-(")
           
    def __messageHandler(self, msg):
        '''
        Handle MsgType.MESSAGE
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        # is nothing to do ;-)
        pass
    
    def __rumorHandler(self, msg):
        '''
        Handle MsgType.RUMOR
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        if  self.__knowRumor == False:
            self.__LOGGER.debug(self.__node.getIdent() + " im not know rumor!")
            self.__knowRumor = True
            self.__node.incRumorCount()
            self.__node.tellRumorToNeighbors(msg)
        
        else:
            self.__node.appendWhisperer(msg.getSubmId())                    
            self.__node.incRumorCount()
            
    def __rumorStateHandler(self, msg):
        '''
        Handle MsgType.RUMOR_STATE
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__node.getRumorState(msg)
    
    def __del__(self):
        '''        
        '''
        pass
        
    
        
            
            
            
