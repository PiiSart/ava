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
            MsgType.REQUEST : self.__requestHandler,
            MsgType.ACKNOWLEDGE : self.__acknowledgeHandler, 
            MsgType.RELEASE : self.__releaseHandler,   
            MsgType.IM_DOWN : self.__imDownHandler,     
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
        
        # create ZMQ_PULL Socket
        self.__socket = self.__context.socket(PULL)
        # bind socket to ip and port
        self.__socket.bind("tcp://" + str(ip) + ":" + str(port))
                
        self.__LOGGER.debug(self.__node.getIdent() + "receiver is started: ip - " + str(ip) + " - port - " + str(port) + "\n")
        
                
        while self.__quit == False:
            # receive message
            msg_str = self.__socket.recv_string()
            
            # create message obj
            msg = Message()
            # import values from json string
            msg.toMessage(msg_str)
            # update vector time
            self.__node.incLamportTime(int(msg.getLamportTime()))
            # print message to STDOUT
            self.__LOGGER.info(self.__getLogString(msg))
                        
            self.__receiverHandler(msg)
                    
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
    
    
    def shutdown(self):        
        self.__quit = True
    
    ###################################
    # HANDLER   
    ###################################
    
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
        subm_id = int(msg.getSubmId())
        # notify another nodes: i'm down!   
        for node_id in self.__node.getNodeInfos():
            if int(node_id) != int(self.__node.getID()) and int(node_id) != subm_id:
                self.__node.send(node_id, MsgType.IM_DOWN, self.__node.incLamportTime())
                
        self.__quit = True
        self.__LOGGER.info(self.__node.getIdent() + "i am down ... :-(")
           
    def __messageHandler(self, msg):
        '''
        Handle MsgType.MESSAGE
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        pass
    
    def __requestHandler(self, msg):
        '''
        Handle MsgType.REQUEST
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__node.handleRequest(msg)
        
    def __acknowledgeHandler(self, msg):
        '''
        Handle MsgType.ACKNOWLEDGE
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__node.handleAcknowledge(msg)
    
    def __releaseHandler(self, msg):
        '''
        Handle MsgType.RELEASE
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__node.handleRelease(msg)
    
    
    def __imDownHandler(self, msg):
        '''
        Handle MsgType.IM_DOWN
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__node.handleImDown(msg)
    
      
    def __del__(self):
        '''        
        '''
        pass
        
    
        
            
            
            
