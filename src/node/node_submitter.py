#!/usr/bin/python3
'''
Created on 05.12.2016

@author: Viktor Werle
'''

import zmq
from zmq.backend.cython.constants import LINGER, PUSH
from logger.logger import NodeLogger
from node import node_message
from util.settings import Settings


class Submitter(object):
    '''
    Simple node submitter for sending messages to node receiver.
    Implements with 0MQ library
    '''
    
    def __init__(self):
        '''
        Constructor
        '''   
        self.__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.SUBMITTER)
        self.__settings = Settings()
        self.__settings.loadSettings()        
        
    
    def send_message(self, message, subm_id, subm_ip, subm_port, recv_id, recv_ip, recv_port): 
        '''
        Send message to receiver.
        
        @param message: message to be send
        @type message: string
        @param id: node id from sender
        @type id: string
        @param ip: destination ip
        @type ip: string
        @param port: destination port
        @type port: string 
        
        @return: -1: if the receiver not reachable, 0: if the receiver confirmed the message
        '''  
        
        __send_successful = -1
             
        # create ZMQ context
        __context = zmq.Context()
        # set max time for send a message
        __context.setsockopt(LINGER, int(self.__settings.getLingerTime()))#node_message.LINGER_TIME)
        # set max time for receive a response
        #__context.setsockopt(RCVTIMEO, node_message.RCVTIMEO_TIME)
        # create ZMQ_PUSH Socket        
        __socket = __context.socket(PUSH)
        #self.__context.setsockopt(LINGER, 0)        
        self.__LOGGER.debug(subm_id + " connect to: ip - " + str(recv_ip) + " port - " + str(recv_port))
        # bind socket to ip and port        
        __socket.connect("tcp://" + str(recv_ip) + ":" + str(recv_port))
        self.__LOGGER.info(subm_id + " send message an [" + recv_id + "]: " + message)        
        # send message
        __socket.send_string(node_message.createMessageStr(subm_id, subm_ip, subm_port, recv_id, recv_ip, recv_port, message))
        __socket.close()
        __context.destroy()
            
    def __del__(self):
        pass
    
    
        