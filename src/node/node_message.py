#!/usr/bin/python3
'''
Created on 20.12.2016
Message protocol (JSON)


{
    header: {
        timestamp: <string>
        vector_time: <list []>
        subm : <dict {"id", "ip", "port", "c_levels":{"id":, "id":}>,
        recv : <dict {"id", "ip", "port"}>,
        cand : <dict {"id", "ip", "port"}>,   
    }
    data: {
        message: <string>
    }
}

@author: Viktor Werle
'''

from datetime import datetime
import json


class Message(object):
    '''
    Node Message.
    '''
    def __init__(self):        
        self.__header = {}
        self.__data = {}
        self.__candidate = {MsgParts.CAND_ID:"", MsgParts.CAND_IP:"", MsgParts.CAND_PORT:""}
        self.__submitter = {}
        self.__receiver = {}
        
    def create(self, vector_time, msg_type, message = ""):
        '''
        Init message components
        '''
        # create header
        self.__header[MsgParts.TIME_STAMP] = self.__time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        self.__header[MsgParts.VECTOR_TIME] = vector_time        
        self.__header[MsgParts.SUBM] = self.__submitter
        self.__header[MsgParts.RECV] = self.__receiver        
        self.__header[MsgParts.CAND] = self.__candidate
        self.__header[MsgParts.MSG_TYPE] = msg_type
                
        # create data
        self.__data[str(MsgParts.MSG)] = message
        
    
    def setSubm(self, subm_id, subm_ip, subm_port, c_levels = {}):
        '''
        Initialized submitter header.
        
        @param subm_id: node id
        @type subm_id: string
        @param c_levels: confidence level of candidates
        @type c_levels: dictionary{"id":level, "id":level}      
        '''
        self.__submitter[MsgParts.SUBM_ID] = subm_id
        self.__submitter[MsgParts.SUBM_IP] = subm_ip
        self.__submitter[MsgParts.SUBM_PORT] = subm_port
        self.__submitter[MsgParts.C_LEVELS] = c_levels 
    
    def setRecv(self, recv_id, recv_ip, recv_port):
        '''
        Initialized submitter header.
        
        @param subm_id: node id
        @type subm_id: string        
        '''
        self.__receiver[MsgParts.RECV_ID] = recv_id
        self.__receiver[MsgParts.RECV_IP] = recv_ip
        self.__receiver[MsgParts.RECV_PORT] = recv_port
    
    def setCand(self, cand_id = "", cand_ip = "", cand_port = ""):
        '''
        Initialized submitter header. Will be set if the 
        submitter is a candidate.
        
        @param cand_id: node
        @type cand_id: string        
        '''
        self.__candidate[MsgParts.CAND_ID] = cand_id
        self.__candidate[MsgParts.CAND_IP] = cand_ip
        self.__candidate[MsgParts.CAND_PORT] = cand_port
        
    
    def toJson(self):
        # create MSG_OBJ to send
        __msg_obj = {MsgParts.HEADER:self.__header, MsgParts.DATA:self.__data}
        
        return json.dumps(__msg_obj)
    
    def toMessage(self, json_str):
        '''
        Export message values from json string
        '''
        __msg_obj = json.loads(json_str)
        self.__header = __msg_obj[MsgParts.HEADER]
        self.__data = __msg_obj[MsgParts.DATA]
        self.__candidate = __msg_obj[MsgParts.HEADER][MsgParts.CAND]
        self.__submitter = __msg_obj[MsgParts.HEADER][MsgParts.SUBM]
        self.__receiver = __msg_obj[MsgParts.HEADER][MsgParts.RECV]
    
    #def __repr__(self):
    #    str_buf = (" " + self.getMsg() + " | [MSG_TYPE]: " + self.getMsgType() +
    #               " [TIMESTAMP]: " + self.getTimestamp() + 
    #               " [VECTOR_TIME]: " + str(self.getVectorTime())) 
                    
    #    return str_buf
    
    def __str__(self):
        str_buf = (" " + self.getMsg() + " | [MSG_TYPE]: " + self.getMsgType() +
                   " [TIMESTAMP]: " + self.getTimestamp() + 
                   " [VECTOR_TIME]: " + str(self.getVectorTime())) 
                    
        return str_buf
            
    # getters
    
    def getHeader(self):
        return self.__header
    
    def getData(self):
        return self.__data
    
    def getTimestamp(self):
        return self.__header[MsgParts.TIME_STAMP]
    
    def getVectorTime(self):
        return self.__header[MsgParts.VECTOR_TIME]
    
    def getMsgType(self):
        return self.__header[MsgParts.MSG_TYPE]
    
    def getMsg(self):
        return self.__data[MsgParts.MSG]
    
    def getSubmId(self):
        return self.__header[MsgParts.SUBM][MsgParts.SUBM_ID]
    
    def getSubmIp(self):
        return self.__header[MsgParts.SUBM][MsgParts.SUBM_IP]
    
    def getSubmPort(self):
        return self.__header[MsgParts.SUBM][MsgParts.SUBM_PORT]
    
    def getSubmConfLevelOne(self):
        return self.__header[MsgParts.SUBM][MsgParts.CONF_LEVEL_1]
    
    def getSubmConfLevelTwo(self):
        return self.__header[MsgParts.SUBM][MsgParts.CONF_LEVEL_2]
    
    def getRecvId(self):
        return self.__header[MsgParts.RECV][MsgParts.RECV_ID]
    
    def getRecvIp(self):
        return self.__header[MsgParts.RECV][MsgParts.RECV_IP]
    
    def getRecvPort(self):
        return self.__header[MsgParts.RECV][MsgParts.RECV_PORT]
    
    def getCandId(self):
        tmp = self.__header[MsgParts.CAND][MsgParts.CAND_ID]
        return tmp#self.__header[MsgParts.CAND][MsgParts.CAND_ID]
    
    def getCandIp(self):
        return self.__header[MsgParts.CAND][MsgParts.CAND_IP]
    
    def getCandPort(self):
        return self.__header[MsgParts.CAND][MsgParts.CAND_PORT]
    
    def getCLevels(self):
        return self.__header[MsgParts.SUBM][MsgParts.C_LEVELS]
    
    def getCLevel(self, cand_id):
        try:
            return self.__header[MsgParts.SUBM][MsgParts.C_LEVELS][cand_id]
        except KeyError:
            return None   
    
    def setVectorTime(self, vector_time):
        self.__header[MsgParts.VECTOR_TIME] = vector_time
   
class MsgParts:
    '''
    Message components
    '''
    HEADER = "header"
    TIME_STAMP = "timestamp"
    SUBM = "subm"
    SUBM_ID = "subm_id"
    SUBM_IP = "subm_ip"
    SUBM_PORT = "subm_port"
    RECV = "recv"
    RECV_ID = "recv_id"
    RECV_IP = "recv_ip"
    RECV_PORT = "recv_port"
    VECTOR_TIME = "vector_time"
    DATA = "data"
    MSG_TYPE = "message_type"
    MSG = "message"
    CAND = "cand"
    CAND_ID = "cand_id"
    CAND_IP = "cand_ip"
    CAND_PORT = "cand_port"
    C_LEVELS= "c_levels"
    
    
class MsgType:
    '''
    Controll messages
    '''
    QUIT = "cm_quit"
    IM_DOWN = "cm_down"
    RUMOR = "cm_rumor"
    RUMOR_STATE = "cm_rumor_state"
    TRUE = "cm_true"
    FALSE = "cm_false"
    I_DONT_CHOOSE_YOU = "cm_i_dont_choose_you"
    KEEP_IT_UP = "cm_keep_it_up"
    VOTE_FOR_ME = "cm_vote_for_me"
    CAMPAIGN = "cm_campaign"
    MESSAGE = "cm_message"
    ECHO_EXPLORER = "cm_exploer"
    ECHO_ECHO = "cm_echo"
    START_VOTE_FOR_ME = "cm_start_vote_for_me"
    START_CAMPAIGN = "cm_start_campaign"