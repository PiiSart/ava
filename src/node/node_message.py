#!/usr/bin/python3
'''
Created on 20.12.2016
Message protocol (JSON)

{
    header: {
        timestamp: <time string>,
        subm_id: <node id string>,
        subm_ip: <node ip string>,
        subm_port: <node port string>,
        recv_id: <node id string>,
        recv_ip: <node ip string>,
        recv_port: <node port string>,
    }
    data: {
        message: <message string>
    }
}


@author: Viktor Werle
'''

from datetime import datetime
import json

'''
Control messages

QUIT = "cm_quit"
IM_DOWN = "cm_down"
WHISPER = "cm_whisper"
OK = "cm_ok"
WHISPER_STATE = "cm_whisper_state"
TRUE = "cm_true"
FALSE = "cm_false"
RESET_WHISPER = "cm_reset_whisper"


Message parts

HEADER = "header"
TIME_STAMP = "timestamp"
SUBM_ID = "subm_id"
SUBM_IP = "subm_ip"
SUBM_PORT = "subm_port"
RECV_ID = "recv_id"
RECV_IP = "recv_ip"
RECV_PORT = "recv_port"
DATA = "data"
MSG = "message"


    
def createMessageStr(subm_id, subm_ip, subm_port, recv_id, recv_ip, recv_port, message):   
    msg_obj = {HEADER:{TIME_STAMP:datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3], SUBM_ID:subm_id, 
                       SUBM_IP:subm_ip, SUBM_PORT:subm_port, RECV_ID:recv_id, RECV_IP:recv_ip, RECV_PORT:recv_port}, DATA:{MSG:message}}    
    return json.dumps(msg_obj)    
    
def convMessageStrToObj(message_str):
    return json.loads(message_str)

def toReceivedStr(ident, message):
    strBuf = (ident + "message received from [" + message[HEADER][SUBM_ID] + "]: <" +  
              message[DATA][MSG] + "> " + "timestamp: " +  message[HEADER][TIME_STAMP] + "\n")
    return str(strBuf)
'''
class Message(object):
    '''
    Node Message.
    '''
    def __init__(self):        
        self.__header = {}
        self.__data = {}
        
    def init(self, Node, vector_time, recv_id, recv_ip, recv_port, msg_type, message):
        '''
        Init message components
        '''
        # create header
        self.__header[MsgParts.TIME_STAMP] = self.__time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        self.__header[MsgParts.VECTOR_TIME] = vector_time
        self.__header[MsgParts.MSG_TYPE] = msg_type        
        self.__header[MsgParts.SUBM_ID] = Node.getID()
        self.__header[MsgParts.SUBM_IP] = Node.getIP()
        self.__header[MsgParts.SUBM_PORT] = Node.getPort()
        self.__header[MsgParts.RECV_ID] = recv_id
        self.__header[MsgParts.RECV_IP] = recv_ip
        self.__header[MsgParts.RECV_PORT] = recv_port
        
        # create data
        self.__data[str(MsgParts.MSG)] = message
        
    
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
    
    def __repr__(self):
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
        return self.__header[MsgParts.SUBM_ID]
    
    def getSubmIp(self):
        return self.__header[MsgParts.SUBM_IP]
    
    def getSubmPort(self):
        return self.__header[MsgParts.SUBM_PORT]
    
    def getRecvId(self):
        return self.__header[MsgParts.RECV_ID]
    
    def getRecvIp(self):
        return self.__header[MsgParts.RECV_IP]
    
    def getRecvPort(self):
        return self.__header[MsgParts.RECV_PORT]
    
    
    def setVectorTime(self, vector_time):
        self.__header[MsgParts.VECTOR_TIME] = vector_time
   
class MsgParts:
    '''
    Message components
    '''
    HEADER = "header"
    TIME_STAMP = "timestamp"
    SUBM_ID = "subm_id"
    SUBM_IP = "subm_ip"
    SUBM_PORT = "subm_port"
    RECV_ID = "recv_id"
    RECV_IP = "recv_ip"
    RECV_PORT = "recv_port"
    VECTOR_TIME = "vector_time"
    DATA = "data"
    MSG_TYPE = "message_type"
    MSG = "message"
    
    
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
    VOTE_ME = "cm_vote_me"
    CAMPAIGN = "cm_campaign"
    MESSAGE = "cm_message"