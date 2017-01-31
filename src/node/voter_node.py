#!/usr/bin/python3
'''
Created on 24.01.2017

@author: Viktor Werle
'''
from node.node import Node
from node.node_message import Message, MsgType
import random
from node.node_submitter import Submitter
from node.node_type import NodeType
import threading
from node.node_receiver import Receiver
from util.graphgen import getNeighbor

class Voter(Node):
    '''
    Voter node.
    '''


    def __init__(self, node_id):
        '''
        Constructor
        '''
        super().__init__(node_id)
        self.__cand_list = self._pref.getCandidateList()
        self.__c_levels = {} # {"cand_id": level, "cand_id":level}
        # set confidence level
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
        
    
    def getNodeType(self):
        '''
        Return the node type.
        
        @return: type of the node
        @type self.__node_type: NodeType
        '''
        return NodeType.VOTER#self.__node_type
    
    def getCandidates(self):
        '''
        Retunr a list with candidates id's
        
        @return: list with candidates id's
        @type self.__cand_list: list[string]
        '''
        return self.__cand_list
    
    def getCLevels(self):
        '''
        Return a candidate confidence levels
        
        @return: candidate confidence levels
        @type __c_levels: dictionary{"cand_id": level, "cand_id":level}
        '''
        return self.__c_levels
    
    def getReadyState(self, cand_id):
        '''
        Get a state of echo algorithm related to candidate.
        
        @param cand_id: candidate id from the candidate who initiate a campaign
        @type cand_id: string
        
        @return: state of campaign. True if the campaign is over or not exists and False if the campaign is still run. 
        @type __ready[cand_id]: boolean
        '''
        try:
            if len(self.getNeighbors()) - 1 == int(self.__echo_counts[cand_id]):
                return True
            else: # if cand_id not in the first link, than campaign doesn't exist
                return False
        except KeyError:
            return True
               
    def __setCLevels(self): 
        '''
        Set the confidence level for candidates.
        '''
        direct_cand_list = []
        
        # select direct candidates
        for neighbor in self.getNeighbors():
            if neighbor in self.__cand_list:
                direct_cand_list.append(neighbor)
        
        # number of direct candidates
        numb_of_direct_cand = len(direct_cand_list)
        numb_of_not_direct_cand = len(self.__cand_list) - numb_of_direct_cand
                
        # c_level of direct candidates  
        if len(direct_cand_list) != 0:
            # if the voter has more than one candidate as neighbor
            c_level_direct_cand = round(100 / numb_of_direct_cand, 2)
            remain = 100 - c_level_direct_cand * numb_of_direct_cand 
        else:
            if numb_of_not_direct_cand == 1:
                remain = random.randint(0, 100)
            else:
                remain = 100
               
        c_level = 0
        
        # set c_level by direct candidates
        for cand in direct_cand_list:
            self.__c_levels[cand] = c_level_direct_cand
            
        # set c_level not direct candidates
        for cand in self.__cand_list:
            if cand not in direct_cand_list:
                if numb_of_not_direct_cand > 1:
                    c_level = random.randint(0, remain)
                    self.__c_levels[cand] = c_level
                else:
                    self.__c_levels[cand] = remain
                
                remain -= c_level
                numb_of_not_direct_cand -= 1        
        
        self._LOGGER.debug("%s my confidence levels: %s" % (self.getIdent(), self.__c_levels))
        #print("%s my confidence levels: %s:" % (self.getIdent(), self.__c_levels))
              
    
    def __getCandIdWithMaxCLevel(self):
        '''
        Return candidate id who has the max confidence level.
        
        @return: candidate id with max confidence level. If max not exist, None will be returned
        '''
        # one candidate is not a task!
        # if only one candidate
        #if len(self.__cand_list) == 1:
        #    return self.__cand_list[0]
        
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
        
        print("%s c_levels: %s" % (self.getIdent(), self.__c_levels))
        self._LOGGER.debug("%s i trust the candidate [%s]!" % (self.getIdent(), trust_cand_id))
        
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
        
        self._LOGGER.info("%s my confidence level for candidate[%s]: %s [MSG]:%s"
                               % (self.getIdent(), cand_id, str(self.__c_levels[cand_id]),
                                  str(msg)) )        
        # adjust c_level for candidate with cand_id
        if self.__c_levels[cand_id] < 100:
            self.__c_levels[cand_id] += int(c_level_subm) / 10             
            self._LOGGER.info("%s new confidence level for candidate[%s]: %s [MSG]:%s"
                               % (self.getIdent(), cand_id, str(self.__c_levels[cand_id]),
                                  str(msg)) )
            # max. 100 exceeded
            if self.__c_levels[cand_id] > 100:
                self.__c_levels[cand_id] = 100
        
        # confide the candidate
        #trust_cand = max(self.__c_levels, key=lambda candidate_id: self.__c_levels[candidate_id])
        trust_cand = self.__getCandIdWithMaxCLevel()
        
        if trust_cand != None and int(trust_cand) == int(cand_id):
            return True
        else:
            return False
     
    def sendVoteForMeOnNeighbors(self, msg):
        '''
        Send on all neighbors his own node id
        
        @param message: full message (with header and data)
        @type message: compare node_message
        '''
        self._LOGGER.debug(self.getIdent() + "my neighbours: " + str(self.getNeighbors()))
        node_infos = self.getNodeInfos()
        msg_buf = Message()        
        for i in self.getNeighbors():
            if str(i) != msg.getSubmId():
                msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                msg_buf.setRecv(str(node_infos[str(i)]["id"]), str(node_infos[str(i)]["ip"]), 
                             str(node_infos[str(i)]["port"]))
                msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
                msg_buf.create(self.getVectorTime(), MsgType.VOTE_FOR_ME)
                Submitter().send_message(self, msg_buf)   
    
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
        trust_cand_id = self.__getCandIdWithMaxCLevel()
        
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
    
    
    
    def __sendExplorer(self, msg, recv_id):
        '''
        Send an explorer message.
                
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
        msg_buf.create(self.getVectorTime(), MsgType.ECHO_EXPLORER, msg.getMsg())                
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
    
    def explorer(self, msg):        
        '''
        Handle explorer messages
        '''
        cand_id = msg.getCandId()
        
        # check i'm leaf
        if len(self.getNeighbors()) == 1:
            # send echo on submitter
            self.__sendEcho(msg, msg.getSubmId())        
        # check first link
        elif self.getFirstLinkId(cand_id) == None:
            # fist link doesn't exist
            print("%s SET_FIRST_LINK TO: %s" % (self.getIdent(), msg.getSubmId()))
            self.setFirstLinkId(cand_id, msg.getSubmId())
            # send explorer on all neighbors except fist link and the candidate (if candidate is direct neighbor from node)
            for neighbor in self.getNeighbors():
                if neighbor != msg.getSubmId() and neighbor != cand_id:
                    self.__sendExplorer(msg, neighbor)
        # first link already exist
        else:
            # send echo on submitter
            self.__sendEcho(msg, msg.getSubmId())
            
        
        
        '''
        # explorer exist
        if self.getFirstLinkId(cand_id) != None:
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
            msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
            msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
            msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
            Submitter().send_message(self, msg_buf)   
        else: # explorer doesn't exist
            # set first link
            self.setFirstLinkId(cand_id, msg.getSubmId()) 
            # change confidence level
            self.incCLevelCampaign(msg)         
            # notify neighbors
            neighbors = self.getNeighbors()
            node_infos = self._pref.getNodeInfos()
            
            # check if node is a leaf, if yes, than send echo on first link
            if len(neighbors) - 1 == 0:
                msg_buf = Message()
                msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                msg_buf.setRecv(msg.getSubmId(), msg.getSubmIp(), msg.getSubmPort())
                msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
                msg_buf.create(self.getVectorTime(), MsgType.ECHO_ECHO)
                Submitter().send_message(self, msg_buf)
            else:    
                # send explorer on neighbors except first link            
                for n_id in neighbors:
                    if str(n_id) != str(self.getFirstLinkId(cand_id)) and str(n_id) != cand_id:
                        msg_buf = Message()
                        msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
                        msg_buf.setRecv(node_infos[n_id]["id"], node_infos[n_id]["ip"], node_infos[n_id]["port"])                
                        msg_buf.setCand(msg.getCandId(), msg.getCandIp(), msg.getCandPort())
                        msg_buf.create(self.getVectorTime(), MsgType.ECHO_EXPLORER)                
                        Submitter().send_message(self, msg_buf)
         '''               
    
    def echo(self, msg):
        '''
        Handle echo messages
        '''        
        cand_id = msg.getCandId()
        # increase echo counter for candidate
        self.incEchoCounter(cand_id)
        # number of neighbors
        number_of_neighbors = len(self.getNeighbors()) 
        
        # all echos from neighbors received (except first link)
        if self.getEchoCounter(cand_id) == number_of_neighbors - 1:
            print("%s CAND ID: %s" % (self.getIdent(), cand_id))
            # send echo on first link
            self.__sendEcho(msg, self.getFirstLinkId(cand_id))
            # delete first link
            self.delFirstLinkId(cand_id)
            # delete echo counter
            self.delEchoCounter(cand_id)
        
        '''
        
        
        # decrease echo counter
        self.incEchoCounter(cand_id)
        print("%s ECHO: anzahl echos: %s Kandidat: %s VON: %s" %(self.getIdent(), self.getEchoCounter(cand_id), cand_id, msg.getSubmId()))
        # received echo from all neighbors
        if self.getEchoCounter(cand_id) == len(self.getNeighbors()) - 1:            
            # notify first link
            msg_buf = Message()
            msg_buf.setSubm(self.getID(), self.getIP(), self.getPort(), self.__c_levels)
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
        '''
        
        
        
        
        
        
        