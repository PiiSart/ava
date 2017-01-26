#!/usr/bin/python3
'''
Created on 24.01.2017

@author: Viktor Werle
'''
from node.node import Node
from node.node_message import Message, MsgType
import random
from node.node_submitter import Submitter

class Voter(Node):
    '''
    Voter node.
    '''


    def __init__(self, node_id):
        '''
        Constructor
        '''
        super().__init__(node_id)
        self.__c_levels = {} # {"cand_id": level, "cand_id":level}
        
        # set confidence level
        self.__setConfLevel()           
    
    def getCandidates(self):
        '''
        Retunr a list with candidates id's
        
        @return: list with candidates id's
        @type self.__cand_list: list[string]
        '''
        return self.__cand_list
    
               
    def __setConfLevel(self): 
        '''
        Set the confidence level for either candidates.
        '''
               
        # candidate 1 is my neighbor        
        cand_list = self._pref.getCandidateList()              
        for cand_id in cand_list:            
            if cand_id in self.getNeighbors():
                self.__c_levels[cand_id] = 100
        
        candidate_one = False
        candidate_two = False
        
        # check first candidate
        if cand_list[0] in self.getNeighbors():
            candidate_one = True
        # check second candidate
        if cand_list[1] in self.getNeighbors():
            candidate_two = True
        
        # either candidates are in the neighbors list  
        if candidate_one == True and candidate_two == True:
            self.__c_levels[cand_list[0]] = 50 
            self.__c_levels[cand_list[1]] = 50
        # candidate one is in the neighbors list
        elif candidate_one == True:
            self.__c_levels[cand_list[0]] = 100 
            self.__c_levels[cand_list[1]] = 0
        # candidate two is in the neighbors list
        elif candidate_two == True:
            self.__c_levels[cand_list[0]] = 0 
            self.__c_levels[cand_list[1]] = 100
        # either candidates are not in the the neighbors list
        else:
            self.__c_levels[cand_list[0]] = random.randint(0,100)
            self.__c_levels[cand_list[1]] = random.randint(0,100) 
    
    def __getCandIdWithMaxCLevel(self):
        '''
        Return candidate id who has the max confidence level.
        
        @return: candidate id with max confidence level. If max not exist, None will be returned
        '''
        c_values = self.__c_levels.values()        
        max_value = max(c_values)  
        true_max_value = False      
        trust_cand_id = None
        
        # check whether max_value is true max_value c1 < > c2
        for cand_id in self.__c_levels:
            if self.__c_levels[cand_id] < max_value:                
                true_max_value = True
                break
        
        if true_max_value == True:
            trust_cand_id = max(self.__c_levels, key=lambda candidate_id: self.__c_levels[candidate_id])
        
        return trust_cand_id
               
        
    def incCLevelVoteForMe(self, msg):
        '''
        Increase confidence level from candidate by c/10. c is the confidence level
        from submitter.
        
        @param msg: received message
        @type msg: node.Message 
        
        @return: True: if the node confide the candidate (c_level is greater as c_level from another candidate), otherwise False
        ''' 
        # who is the candidate
        cand_id = msg.getCandId()
        # which c_level has the candidate by submitter
        # if the message is from candidate self, than is the c_level 100
        if cand_id == msg.getSubmId():
            c_level_subm = 100
        else:
            c_level_subm = msg.getCLevel(cand_id)
        # adjust c_level
        if self.__c_levels[cand_id] < 100:
            self.__c_levels[cand_id] += int(c_level_subm) / 10             
            self._LOGGER.debug("%s new confidence level candidate[%s]: %s %s"
                               % (self.getIdent(), cand_id, str(self.__c_levels[cand_id]),
                                  str(msg)) )
            # max. 100 exceeded
            if self.__c_levels[cand_id] > 100:
                self.__c_levels[cand_id] = 100
        
        # confide the candidate
        #trust_cand = max(self.__c_levels, key=lambda candidate_id: self.__c_levels[candidate_id])
        trust_cand = self.__getCandIdWithMaxCLevel(msg)
        
        if trust_cand != None:
            return True
        else:
            return False
        
    
    def incCLevelCampaign(self, msg):
        '''
        Increase the confidence level of candidate from the message, if the local confidence level of candidate
        greater than confidence level of candidate from the message. The local confidence level of the opponent
        will be decrease by 1 at the same time. 
        And vice versa, if the local confidence level of candidate smaller as the confidence level of candidate 
        from the message.
          
        
        @param msg: received message
        @type msg: node.Message  
        '''  
        # who is the candidate
        cand_id = msg.getCandId()
        
        # get candidate with max c_level
        trust_cand_id = self.__getCandIdWithMaxCLevel(msg)
        
        if trust_cand_id != None:
            # get candidate id with min c_level
            not_trust_cand = min(self.__c_levels, key=lambda candidate_id: self.__c_levels[candidate_id])
            # confirm campaign
            if cand_id == trust_cand_id:                
                self.__c_levels[cand_id] += 1
                self.__c_levels[not_trust_cand] -= 1
            # deny campaign
            else:
                self.__c_levels[cand_id] -= 1
                self.__c_levels[not_trust_cand] += 1
        
        # adjust c_level values
        for c_id in self.__c_levels:
            if self.__c_levels[c_id] < 0:
                self.__c_levels[c_id] = 0
            if self.__c_levels[c_id] > 100:
                self.__c_levels[c_id] = 100
    
    def notifyNeighbours(self, msg, message = ""):
        '''
        Notify all Neighbours expect the one from whom it has received.
        
        @param message: message to send
        @type messsage: string
        '''
        
        neighbors = self.getNeighbors()
        node_infos = self.getNodeInfos()
        
        for neighbor_id in neighbors:
            if neighbor_id != self.getID():
                msg_buf = Message()
                msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                msg_buf.setRecv(
                    node_infos[str(neighbor_id)]["id"], 
                    node_infos[str(neighbor_id)]["ip"], 
                    node_infos[str(neighbor_id)]["port"]
                    )
                msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())   
                msg_buf.create(self.getVectorTime(), MsgType.VOTE_FOR_ME, message)
                Submitter().send_message(self.getID(), msg_buf)
    
    def explorer(self, msg):
        '''
        Handle explorer messages
        '''
        cand_id = msg.getCandId()
        # explorer exist
        if self.getExplorerState(cand_id) == True:
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
            msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
            msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
            msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
            Submitter().send_message(self, msg_buf)
            
            #echo counter + 1
            self.incEchoCounter(cand_id)
        else: # explorer doesn't exist
            # set first link
            self.setFirstLinkId(cand_id, msg.getSubmId())            
            # notify neighbors
            neighbors = self.getNeighbors()
            node_infos = self._pref.getNodeInfos()
            for n_id in neighbors:
                msg_buf = Message()
                msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                msg_buf.setRecv(node_infos[n_id]["id"], node_infos[n_id]["ip"], node_infos[n_id]["port"])
                msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort)
                msg_buf.create(self.getVectorTime(), MsgType.ECHO_EXPLORER)
                Submitter().send_message(self, msg_buf)
            
        
        
    def echo(self, msg):
        '''
        Handle echo messages
        '''
        cand_id = msg.getCandId()
        self.incEchoCounter(cand_id)
        
        # received echo from all neighbors
        if self.getReadyState(cand_id) == True:            
            # notify first link
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
            first_link = self.getFirstLinkId(cand_id)
            node_infos = self._pref.getNodeInfos()
            msg_buf.setRecv(node_infos[first_link]["id"], node_infos[first_link]["ip"], node_infos[first_link]["port"])
            msg_buf.setCand(msg.getCandId, msg.getCandIp(), msg.getCandPort())
            msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
            Submitter().send_message(self, msg_buf)
            
            # reset echo counter
            self.resetEchoCounter(cand_id)
            # delete first link
            self.deleteFirstLinkId(cand_id)
        
        
        
        
        
        
        
        