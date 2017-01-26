#!/usr/bin/python3
'''
Created on 24.01.2017

@author: Viktor Werle
'''

from node.node import Node
from node.node_submitter import Submitter
from node.node_message import Message, MsgType
from node.node_type import NodeType
import random

class Candidate(Node):
    '''
    Candidate node.
    '''


    def __init__(self, node_id):
        '''
        Constructor
        '''
        super().__init__(node_id)
        self.__node_type = NodeType.CANDIDATE
        self.__count_voters_responses = 0
        #self.__campaign_count = 0
        #self.__campaign_state = True    
    
    
    #def getCampaignCount(self):
    #    return self.__campaign_count
    
   # def incCampaignCount(self):
    #    self.__campaign_count += 1
    
    #def resetCampaignCount(self):
    #    self.__campaign_count = 0
    
    #def getCampaignState(self):
    #    return self.__campaign_state
    
    #def setCampaignState(self, ready):
    #    self.__campaign_state = ready
    
    def getNodeType(self):
        '''
        Return the node type.
        
        @return: type of the node
        @type self.__node_type: NodeType
        '''
        return self.__node_type
    
    def incCountVotersResponses(self):
        '''
        Increment the counter for voters responses. Start new
        voting, if the counter reach certain value.
        '''
        self.__count_voters_responses += 1
        # time for new voting
        if self.__count_voters_responses >= self._pref.getTrust():
            # reset counter
            self.__count_voters_responses = 0
            # start voting
            self.startVoting()
        
    def getCountVotersResponse(self):
        '''
        Return a number of responses from voters after VOTE_FOR_ME or CAMPAIGN message.
        
        @return: number of responses from votres
        @type self.__count_voters_responses: integer
        '''
        return self.__count_voters_responses
    
    
    def startVoting(self, voting_type = -1):
        '''
        Start random either voting or campaign
        0 - start vote for me
        1 - start campaign
        @param voting_type: define voting type
        @type voting_type: 0: VOTE_FOR_ME, 1: CAMPAIGN
        '''
        # reset voter response counter
        self.__count_voters_responses = 0
        
        if voting_type == -1:
            choose = random.randint(0,1)
        else:
            choose = voting_type
        
        # start voting
        self._LOGGER.debug("%s start voting", self.getIdent())
        for n in self.getNeighbors():
            msg = Message()
            msg.setSubm(self.getID(), self.getIP(), self.getPort())
            msg.setRecv(n, self.getNodeInfos()[n]["ip"], self.getNodeInfos()[n]["port"])
            msg.setCand(self.getID(), self.getIP(), self.getPort())
            if choose == 0:                
                msg.create(self.getVectorTime(), MsgType.VOTE_FOR_ME, " i am super, vote for me!")
            if choose == 1 and self.getReadyState(self.getID()) == True:
                self.resetEchoCounter(self.getID())
                self.setReadyState(self.getID(), False)
                msg.create(self.getVectorTime(), MsgType.ECHO_EXPLORER, " i am super, support my campaign!")
                
            Submitter().send_message(self, msg)
            
    def echo(self):
        '''
        Increase the echo counter and check whether the campaign is over. Notify
        submitter.
        '''
        # increase echo counter
        self.incEchoCounter(self.getID())
        # campaign ready?
        if self.getReadyState(self.getID()) == True:
            # TODO: send result on Observer!
            self._LOGGER.info(self.getIdent() + " campaign is over!")
            # reset echo counter
            self.resetEchoCounter(self.getID())
            