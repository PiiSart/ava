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
'''
QUIT = "cm_quit"
IM_DOWN = "cm_down"
WHISPER = "cm_whisper"
OK = "cm_ok"
WHISPER_STATE = "cm_whisper_state"
TRUE = "cm_true"
FALSE = "cm_false"
RESET_WHISPER = "cm_reset_whisper"

'''
Message parts
'''
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
  
'''
zmq options
'''  
#LINGER_TIME = -1
#RCVTIMEO_TIME = -1
    
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

    
    
    