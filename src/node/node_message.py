#!/usr/bin/python3
'''
Created on 20.12.2016
Message protocol (JSON)


{
    header: {
        timestamp: <string>
        vector_time: <list []>
        subm : <dict {"id", "ip", "port", "MsgType">,
        recv : <dict {"id", "ip", "port"}>,
        cand : <dict {"id", "ip", "port"}>  
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
        self.__submitter = {}
        self.__receiver = {}
        
    def create(self, lamport_time, msg_type, message=""):
        '''
        Init message components
        '''
        # create header
        self.__header[MsgParts.TIME_STAMP] = self.__time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        self.__header[MsgParts.LAMPORT_TIME] = lamport_time        
        self.__header[MsgParts.SUBM] = self.__submitter
        self.__header[MsgParts.RECV] = self.__receiver
        self.__header[MsgParts.MSG_TYPE] = msg_type
                        
        # create data
        self.__data[str(MsgParts.MSG)] = message
        
    
    def setSubm(self, subm_id, subm_ip, subm_port):
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
    
    def setRecv(self, recv_id, recv_ip, recv_port):
        '''
        Initialized submitter header.
        
        @param subm_id: node id
        @type subm_id: string        
        '''
        self.__receiver[MsgParts.RECV_ID] = recv_id
        self.__receiver[MsgParts.RECV_IP] = recv_ip
        self.__receiver[MsgParts.RECV_PORT] = recv_port
    
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
        self.__submitter = __msg_obj[MsgParts.HEADER][MsgParts.SUBM]
        self.__receiver = __msg_obj[MsgParts.HEADER][MsgParts.RECV]
    
    #def __repr__(self):
    #    str_buf = (" " + self.getMsg() + " | [MSG_TYPE]: " + self.getMsgType() +
    #               " [TIMESTAMP]: " + self.getTimestamp() + 
    #               " [LAMPORT_TIME]: " + str(self.getLamportTime())) 
                    
    #    return str_buf
    
    def __str__(self):
        str_buf = (" " + self.getMsg() + " | [MSG_TYPE]: " + self.getMsgType() +
                   " [TIMESTAMP]: " + self.getTimestamp() + 
                   " [LAMPORT_TIME]: " + str(self.getLamportTime())) 
                    
        return str_buf
            
    # getters
    
    def getHeader(self):
        return self.__header
    
    def getData(self):
        return self.__data
    
    def getTimestamp(self):
        return self.__header[MsgParts.TIME_STAMP]
            
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
    
    def setLamportTime(self, lamport_time):
        self.__header[MsgParts.LAMPORT_TIME] = lamport_time
        
    def getLamportTime(self):
        return self.__header[MsgParts.LAMPORT_TIME]
     
     
     
     
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
    LAMPORT_TIME = "lamport_time"
    DATA = "data"
    MSG_TYPE = "message_type"
    MSG = "message"
        
    
class MsgType:
    '''
    Controll messages
    '''
    QUIT = "cm_quit"
    IM_DOWN = "cm_down"    
    MESSAGE = "cm_message"
    REQUEST = "cm_request"
    RELEASE = "cm_release"
    ACKNOWLEDGE = "cm_acknowledge"
    