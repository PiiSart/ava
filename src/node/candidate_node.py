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
from node.node_receiver import Receiver
import threading
import time

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
        self.__is_campaign_run = False
        self.__c_levels = {}
        self.__setCLevels()
        self.__receiver = Receiver(self) 
        self.__start()         
    
    def __start(self):
        '''
        Start node receiver in a thread.
        '''
        receiver_t = threading.Thread(target=self.__receiver.start, args=(self.getIP(), self.getPort()))   
        self._LOGGER.debug(self.getIdent() + "starterd ...")     
        receiver_t.start() 
        # send own ID on all neighbours
        self.notifyNeighbours("my id is " + self.getID())
          
        receiver_t.join()
    
    #def isMarked(self):
    #   return False
    
    def getNodeType(self):
        '''
        Return the node type.
        
        @return: type of the node
        @type self.__node_type: NodeType
        '''
        return NodeType.CANDIDATE#self.__node_type      
        
    def incCountVotersResponses(self):
        '''
        Increment the counter for voters responses. Start new
        voting, if the counter reach certain value.
        '''
        self.__count_voters_responses += 1
        # time for new voting
        if self.__count_voters_responses >= int(self._pref.getTrust()):
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
    
    def getReadyState(self, cand_id):
        '''
        Get a state of echo algorithm related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        
        @return: state of campaign. True if the campaign is over or not exists and False if the campaign is still run. 
        @type __ready[cand_id]: boolean
        '''
        try:
            if len(self.getNeighbors()) - 1 == int(self.getEchoCounter(cand_id)):
                return True
            else: # if cand_id not in the first link, than campaign doesn't exist
                return False
        except KeyError:
            return True
    
    def __setCLevels(self):
        for cand in self._pref.getCandidateList():
            if cand == self.getID():
                self.__c_levels[cand] = 100
            else:
                self.__c_levels[cand] = 0
    
    def __sendExplorer(self, recv_id, msg=None, initiator=True, message_str=""):
        '''
        Send an explorer message. If initiator is True, candidate will be set
        itself. In another case the candidate is from received message.
        
        @param recv_id: node id from receiver
        @type recv_id: string      
        @param msg: received message
        @type msg: node_message.Message       
        @param initiator: True if the node is initiator, False if another node is initiator
        @type initiator: boolean
        '''
        node_infos = self.getNodeInfos()
        msg_buf = Message()        
        msg_buf.setRecv(node_infos[recv_id]["id"], 
                        node_infos[recv_id]["ip"], 
                        node_infos[recv_id]["port"]
                        )  
        # initiator
        if initiator == True:
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
            # set candidate itself              
            msg_buf.setCand(self.getID(), self.getIP(), self.getPort())
        # not initiator
        else:
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), msg.getCLevels())
            print("CANDIDATE: %s call-through C_LEVELS: %s" %(self.getIdent(), msg.getCLevels()))
            # set candidate from the received message
            msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
            
        msg_buf.create(self.getVectorTime(), MsgType.ECHO_EXPLORER, message_str)                
        Submitter().send_message(self, msg_buf)
    
    def __sendEcho(self, msg, recv_id):
        '''
        Send an echo message.
        
        @param msg: received message
        @type msg: node_message.Message
        @param recv_id: node id from receiver
        @type recv_id: string
        '''
        node_infos = self.getNodeInfos()
        
        msg_buf = Message()
        msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), msg.getCLevels())
        msg_buf.setRecv(node_infos[recv_id]["id"],
                        node_infos[recv_id]["ip"], 
                        node_infos[recv_id]["port"]
                        )
        msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
        msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO, msg.getMsg())
        Submitter().send_message(self, msg_buf)
    
    
    def startVoting(self, voting_type = -1):
        '''
        Start random either voting or campaign
        0 - start vote for me
        1 - start campaign
        @param voting_type: define voting type
        @type voting_type: 0: VOTE_FOR_ME, 1: CAMPAIGN
        '''
        
        if self.isVoteOver() == True:
            return
        
        # reset voter response counter
        self.__count_voters_responses = 0
                 
        if voting_type == -1:
            choose = random.randint(0,1)
        else:
            choose = voting_type
                              
        self._LOGGER.info("%s ***************************", self.getIdent())        
        
        
        # vote for me
        if choose == 0:
            # reset voter response counter
            #self.__count_voters_responses = 0
            self._LOGGER.info("%s **** START VOTE FOR ME ****", self.getIdent())
            self._LOGGER.info("%s ***************************", self.getIdent())
            # notify neighbors
            for neighbor in self.getNeighbors():
                msg = Message()
                msg.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                msg.setRecv(neighbor, 
                            self.getNodeInfos()[neighbor]["ip"], 
                            self.getNodeInfos()[neighbor]["port"]
                            )
                msg.setCand(self.getID(), self.getIP(), self.getPort())               
                msg.create(self.getVectorTime(), MsgType.VOTE_FOR_ME, " i am super, vote for me!")
                Submitter().send_message(self, msg)
        
        # campaign      
        if choose == 1 and self.__is_campaign_run == False:
            # reset voter response counter
            #self.__count_voters_responses = 0
            self.__is_campaign_run = True
            self._LOGGER.info("%s **** START CAMPAIGN    ****", self.getIdent()) 
            self._LOGGER.info("%s ***************************", self.getIdent())
            # notify neighbors
            for neighbor in self.getNeighbors():
                self.__sendExplorer(neighbor, " i am super, support my campaign!")                
        elif choose == 1: # dirty !!! must be change!
            self._LOGGER.info("%s can't start new campaign, while another campaign is running!")
        
    def explorer(self, msg):
        '''
        Handle explorer messages.
        '''
        # snapshot 
        self.handleSnapshot(msg)
        
        cand_id = msg.getCandId()
        
        # explorer from foreign candidate
        if self.getID() != cand_id:
            # check i'm leaf
            if len(self.getNeighbors()) == 1:
                # send echo on submitter
                self.__sendEcho(msg, msg.getSubmId())        
            # check first link
            elif self.getFirstLinkId(cand_id) == None:
                # fist link doesn't exist
                self.setFirstLinkId(cand_id, msg.getSubmId())
                # send explorer on all neighbors except fist link
                for neighbor in self.getNeighbors():
                    if neighbor != msg.getSubmId():
                        self.__sendExplorer(neighbor, msg, False, msg.getMsg())
            # first link already exist
            else: # explorer already received
                # increase echo counter and check ready state
                self.echo(msg)
                
        # explorer is mine
        else:
            self.echo(msg)
        
                    
    def echo(self, msg):
        '''
        Increase the echo counter and check whether the campaign is over. Notify
        submitter.
        '''
        # snapshot 
        self.handleSnapshot(msg)
        
        cand_id = msg.getCandId()
        # increase echo counter for candidate
        self.incEchoCounter(cand_id)
        # number of neighbors
        number_of_neighbors = len(self.getNeighbors()) 
        # echo or explorer from foreign candidate
        if cand_id != self.getID():
            # all echos from neighbors received (except first link)
            if self.getEchoCounter(cand_id) == number_of_neighbors - 1:
                # send echo on first link
                self.__sendEcho(msg, self.getFirstLinkId(cand_id))                              
                # delete first link
                self.delFirstLinkId(cand_id)
                # delete echo counter
                self.delEchoCounter(cand_id)
        else:
            self.incCountVotersResponses()
            # all echos from neighbors received (except first link)
            if self.getEchoCounter(cand_id) == number_of_neighbors:                
                # send echo on observer
                #self.__sendEcho(msg, self.getFirstLinkId(cand_id)) # TODO: implement observer                              
                # delete first link
                self.delFirstLinkId(cand_id)
                # delete echo counter
                self.delEchoCounter(cand_id)
                self._LOGGER.info("%s my campaign is over! Try to notify observer!" % (self.getIdent()))
                #  end campaign
                self.__is_campaign_run = False
