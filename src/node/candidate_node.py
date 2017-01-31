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
    
    
    def __sendExplorer(self, recv_id, msg=None, initiator=True, message_str=""):
        '''
        Send an explorer message. If initiator is True, candidate will be set
        itself. In another case the candidate is from received message.
        
        @param recv_id: node id from receiver
        @type recv_id: string      
        @param msg: received message
        @type msg: node_message.Message       
        @param i_am_candidate: True if the node is initiator, False if another node is initiator
        @type i_am_candidate: boolean
        '''
        node_infos = self.getNodeInfos()
        msg_buf = Message()
        msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
        msg_buf.setRecv(node_infos[recv_id]["id"], 
                        node_infos[recv_id]["ip"], 
                        node_infos[recv_id]["port"]
                        )  
        # initiator
        if initiator == True:
            # set candidate itself              
            msg_buf.setCand(self.getID(), self.getIP(), self.getPort())
        # not initiator
        else:
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
        msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
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
        # reset voter response counter
        self.__count_voters_responses = 0
        
        if voting_type == -1:
            choose = random.randint(0,1)
        else:
            choose = voting_type
                              
        self._LOGGER.info("%s ***************************", self.getIdent())
       
        # vote for me
        if choose == 0:
            self._LOGGER.info("%s **** START VOTE FOR ME ****", self.getIdent())
            self._LOGGER.info("%s ***************************", self.getIdent())
            # notify neighbors
            for neighbor in self.getNeighbors():
                msg = Message()
                msg.setSubm(self.getID(), self.getIP(), self.getPort())
                msg.setRecv(neighbor, 
                            self.getNodeInfos()[neighbor]["ip"], 
                            self.getNodeInfos()[neighbor]["port"]
                            )
                msg.setCand(self.getID(), self.getIP(), self.getPort())               
                msg.create(self.getVectorTime(), MsgType.VOTE_FOR_ME, " i am super, vote for me!")
                Submitter().send_message(self, msg)
        
        # campaign      
        if choose == 1 and self.__is_campaign_run == False:
            self.__is_campaign_run = True
            self._LOGGER.info("%s **** START CAMPAIGN    ****", self.getIdent()) 
            self._LOGGER.info("%s ***************************", self.getIdent())
            # notify neighbors
            for neighbor in self.getNeighbors():
                self.__sendExplorer(neighbor, " i am super, support my campaign!")
                '''
                msg = Message()
                msg.setSubm(self.getID(), self.getIP(), self.getPort())
                msg.setRecv(n, self.getNodeInfos()[n]["ip"], self.getNodeInfos()[n]["port"])
                msg.setCand(self.getID(), self.getIP(), self.getPort())               
                msg.create(self.getVectorTime(), MsgType.ECHO_EXPLORER, " i am super, support my campaign!")
                Submitter().send_message(self, msg)
                # increase echo counter
                self.incEchoCounter(self.getID())
                '''
        else:
            self._LOGGER.info("%s can't start new campaign, while another campaign is running!")
        
    def explorer(self, msg):
        '''
        Handle explorer messages.
        '''
        cand_id = msg.getCandId()
        
        # explorer from foreign candidate
        if self.getID() != cand_id:
            pass
        # explorer is mine
        else:
            self.__sendEcho(msg, msg.getSubmId())
        
        '''
        # explorer exist, echo on submitter
        if self.getFirstLinkId(cand_id) != None:
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
            msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
            msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
            msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
            Submitter().send_message(self, msg_buf)   
        else: # explorer doesn't exist
            # set first link
            self.setFirstLinkId(cand_id, msg.getSubmId())          
            # notify neighbors
            neighbors = self.getNeighbors()
            node_infos = self._pref.getNodeInfos()
            
            # check if node is a leaf, if yes, than send echo on first link
            if len(neighbors) - 1 == 0:
                msg_buf = Message()
                msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
                msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
                msg_buf.setCand(self.getID(), self.getIP(), self.getPort())
                msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
                Submitter().send_message(self, msg_buf)
            else:    
                # send explorer on neighbors except first link            
                for n_id in neighbors:
                    if str(n_id) != str(self.getFirstLinkId(cand_id)):
                        msg_buf = Message()
                        msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
                        msg_buf.setRecv(node_infos[n_id]["id"], node_infos[n_id]["ip"], node_infos[n_id]["port"])                
                        msg_buf.setCand(self.getID(), self.getIP(), self.getPort())
                        msg_buf.create(self.getVectorTime(), MsgType.ECHO_EXPLORER)                
                        Submitter().send_message(self, msg_buf)
        '''
            
    def echo(self, msg):
        '''
        Increase the echo counter and check whether the campaign is over. Notify
        submitter.
        '''        
        cand_id = msg.getCandId()
        
        # explorer from foreign candidate
        if self.getID() != cand_id:
            pass
        # explorer is mine
        else:
            # increase my echo counter
            self.incEchoCounter(cand_id)
            # check if ready
            number_of_neighbors = len(self.getNeighbors())
            if  number_of_neighbors == self.getEchoCounter(cand_id):
                # campaign is ends
                print("%s ECHO: anzahl echos: %s Kandidat: %s VON: %s" %(self.getIdent(), self.getEchoCounter(cand_id), cand_id, msg.getSubmId()))
                self._LOGGER.info("%s my campaign is over! Try to notify observer!" % (self.getIdent()))
                # delete counter
                self.delEchoCounter(cand_id)
                # stop campaign
                self.__is_campaign_run = False
            
        '''   
        self.incEchoCounter(cand_id)
        print("%s ECHO: anzahl echos: %s Kandidat: %s VON: %s" %(self.getIdent(), self.getEchoCounter(cand_id), cand_id, msg.getSubmId()))
        # received echo from all neighbors
        if cand_id != self.getID() and self.getEchoCounter(cand_id) == len(self.getNeighbors() - 1):
            print("%s ECHO: anzahl echos: %s Kandidat: %s VON: %s" %(self.getIdent(), self.getEchoCounter(cand_id), cand_id, msg.getSubmId()))            
            # notify first link
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort())
            first_link = self.getFirstLinkId(cand_id)
            node_infos = self._pref.getNodeInfos()
            msg_buf.setRecv(node_infos[first_link]["id"], node_infos[first_link]["ip"], node_infos[first_link]["port"])
            msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
            msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
            Submitter().send_message(self, msg_buf)
            
            # reset echo counter
            self.resetEchoCounter(cand_id)
            # delete first link
            self.deleteFirstLinkId(cand_id)
        # campaign ends
        if cand_id == str(self.getID()) and self.getEchoCounter(cand_id) == len(self.getNeighbors()):
            print("%s ECHO: anzahl echos: %s Kandidat: %s VON: %s" %(self.getIdent(), self.getEchoCounter(cand_id), cand_id, msg.getSubmId()))
            self._LOGGER.info("%s my campaign is over! Try to notify observer!" % (self.getIdent()))
            self.__is_campaign_run = False
        '''   