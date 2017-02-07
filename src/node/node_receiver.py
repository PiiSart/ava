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
from node.node_type import NodeType
from node.node_submitter import Submitter



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
            MsgType.RUMOR_STATE : self.__rumorStateHandler,
            MsgType.START_VOTE_FOR_ME : self.__startVoteForMeHandler,
            MsgType.START_CAMPAIGN : self.__startCampaignHandler,
            MsgType.KEEP_IT_UP : self.__keepItUpHandler,
            MsgType.I_DONT_CHOOSE_YOU : self.__iDontChooseYouHandler,
            MsgType.VOTE_FOR_ME : self.__voteForMeHandler,
            MsgType.CAMPAIGN : self.__campaignHandler,
            MsgType.ECHO_EXPLORER : self.__explorerHandler,
            MsgType.ECHO_ECHO : self.__echoEchoHandler,
            MsgType.SNAPSHOT : self.__snapshotHandler,
            MsgType.UNMARK : self.__unmarkHandler,
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
        #self.__socket.connect("tcp://" + str(ip) + ":" + str(port))
        
        self.__LOGGER.debug(self.__node.getIdent() + "receiver is started: ip - " + str(ip) + " - port - " + str(port) + "\n")
        
                
        while self.__quit == False:
            # receive message
            msg_str = self.__socket.recv_string()
            
            # create message obj
            msg = Message()
            # import values from json string
            msg.toMessage(msg_str)
            # update vector time
            msg.setVectorTime(self.__node.setVectorTimeByReceive(msg.getVectorTime()))
            # print message to STDOUT
            self.__LOGGER.info(self.__getLogString(msg))
            # check termination time
            #self.__checkTermTime(msg)
            # handle message
            #try:                       
            self.__receiverHandler(msg)
            #ecept KeyError as e:
            #   self.__LOGGER.error(self.__node.getIdent() + " unknown message type [" + str(e) + "]")
                
                    
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
    
    def __checkTermTime(self, msg):
        '''
        Check if the termination time is reach, than notify the observer and
        set vote_over flag of True.
        '''
        if self.__node.isVoteOver() == False and self.__node.getNodeType() != NodeType.CANDIDATE:
            vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
            term_time = int(self.__node._pref.getVecTimeTermination())
            
            if vector_time > term_time:
                self.__node.myVote()
                self.__node.setVoteOver(True)
    
    
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
        #print(msg.getMsgType())
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
        #if NodeType.CANDIDATE != self.__node.getNodeType():
        self.__node.handleSnapshot(msg)
    
    def __rumorHandler(self, msg):
        '''
        Handle MsgType.RUMOR
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        if  self.__knowRumor == False:
            self.__LOGGER.debug(self.__node.getIdent() + " i'm not know rumor!")
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
    
    def __startVoteForMeHandler(self, msg):
        '''
        Handle MsgType.START_VOTE_FOR_ME <CANDIDATE>
        Initiate a vote for me message
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__LOGGER.debug(self.__node.getID() + " NodeType: " + self.__node.getNodeType() + str(msg))
        # only candidate can start voting
        if self.__node.getNodeType() == NodeType.CANDIDATE:
            self.__LOGGER.info(self.__node.getID() + " i start voting!" +  str(msg))
            self.__node.startVoting(0)
            
    def __startCampaignHandler(self, msg):
        '''
        Handle MsgType.START_CAMPAIGN <CANDIDATE>
        Initiate a campaign message.
        
        @param msg: received message
        @type msg: NodeMessage
        '''
        self.__LOGGER.debug(self.__node.getID() + " NodeType: " + self.__node.getNodeType() + str(msg))
        # only candidate can start voting
        if self.__node.getNodeType() == NodeType.CANDIDATE:
            self.__LOGGER.info(self.__node.getID() + " i start voting!" +  str(msg))
            self.__node.startVoting(1)
       
    def __keepItUpHandler(self, msg):
        '''
        Handle MsgType.KEEP_IT_UP. <CANDIDATE NODE>
        
        @param msg: received message
        @type msg: node.Message
        '''
        vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        if  vector_time > term_time:
            self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
            return
        self.__node.incCountVotersResponses()
    
    def __iDontChooseYouHandler(self, msg):
        '''
        Handle MsgType.I_DONT_CHOOSE_YOU. <CANDIDATE NODE>
        
        @param msg: received message
        @type msg: node.Message
        '''
        vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        if  vector_time > term_time:
            self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
            return
        self.__node.incCountVotersResponses()
        
    def __voteForMeHandler(self, msg):
        '''
        Handle MsgType.VOTE_FOR_ME. <VOTER NODE>.
        If the node confide the candidate, it notify all neighbors and response
        the candidate : keep it up.
        In another case it response only the candidate : i don't choose you.
        
        @param msg: received message
        @type msg: node.Message
        '''
        
        # message only for voter's
        if self.__node.getNodeType() == NodeType.CANDIDATE:
            self.__LOGGER.info("%s I am candidate too! I don't vote! <cand_id:%s>" %(self.__node.getIdent(), msg.getCandId()))
            return
        
        vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        if  vector_time > term_time:
            self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
            return
        
        self.__node.voteForMe(msg)
        
    
    def __campaignHandler(self, msg):
        '''
        Handle MsgType.CAMPAIGN. <CANDIDATE>
        Init message. Starts CAMPAIGN with echo algorithm!
        
        @param msg: received message
        @type msg: node.Message
        '''  
        
        # only candidate can do this
        if self.__node.getNodeType() != NodeType.CANDIDATE:
            return
        
        vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        if  vector_time > term_time:
            self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
            return
        
        # start campaign
        self.__node.startVoting(1)
        
            
    def __explorerHandler(self, msg):
        '''
        Handle MsgType.ECHO_EXPLORER. <VOTER + CANDIDATE>
               
        @param msg: received message
        @type msg: node.Message
        '''
        
        #vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        #term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        #if  vector_time > term_time:
        #    self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
        #   return
        
        self.__node.explorer(msg)
    
    def __echoEchoHandler(self, msg):
        '''
        Handle MsgType.ECHO_ECHO. <VOTER + CANDIDATE>
               
        @param msg: received message
        @type msg: node.Message
        '''
        #vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        #term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        #if  vector_time > term_time:
        #    self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
        #    return
        
        self.__node.echo(msg)
    
    def __snapshotHandler(self, msg):
        '''
        Handle MsgType.SNAPSHOT. <VOTER>
        
               
        @param msg: received message
        @type msg: node.Message
        '''
        
        #vector_time = int(self.__node.getVectorTime()[int(self.__node.getID())])
        #term_time = int(self.__node._pref.getVecTimeTermination())
        
        # time exceeded
        #if  vector_time > term_time:
        #    self.__LOGGER.debug("%s vector time: %s <--> termination time: %s" % (self.__node.getIdent(), vector_time, term_time))
        #    return
        
        self.__node.initSnapshot(msg)
        
        
    def __unmarkHandler(self, msg):
        '''
        Handle MsgType.UNMARK. <VOTER, CANDIDATE>
        
               
        @param msg: received message
        @type msg: node.Message
        '''
        self.__node.unmark(msg)        
    
    
       
    def __del__(self):
        '''        
        '''
        pass
        
    
        
            
            
            
