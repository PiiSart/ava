#!/usr/bin/python3
'''
Created on 21.12.2016

Manager. Can communicate with nodes.

@author: Viktor Werle
'''


from node.node_submitter import Submitter
from logger.logger import NodeLogger
from node.node_message import MsgType, MsgParts, Message
from util.settings import Settings
import zmq
from zmq.backend.cython.constants import PULL, RCVTIMEO
from timeit import default_timer as timer
from datetime import datetime
from zmq.backend.cython.constants import LINGER, PUSH

IDENT = "Manager--> "
__FILE_ACCESS_MODE = "r"
__NODES = {}
__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.MANAGER)
__IP = "127.0.0.1"
__PORT = "10000"


class ManMessage(Message):
    '''
    Manager Message
    '''
    def __init__(self):
        super().__init__()
        
    def init(self, vector_time, subm_id, subm_ip, subm_prot, recv_id, recv_ip, recv_port, msg_type, message):
        '''
        Init message components
        '''
        # create header
        self.getHeader()[MsgParts.TIME_STAMP] = self.__time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3]
        self.getHeader()[MsgParts.VECTOR_TIME] = vector_time
        self.getHeader()[MsgParts.MSG_TYPE] = msg_type        
        self.getHeader()[MsgParts.SUBM_ID] = subm_id
        self.getHeader()[MsgParts.SUBM_IP] = subm_ip
        self.getHeader()[MsgParts.SUBM_PORT] = subm_prot
        self.getHeader()[MsgParts.RECV_ID] = recv_id
        self.getHeader()[MsgParts.RECV_IP] = recv_ip
        self.getHeader()[MsgParts.RECV_PORT] = recv_port
        
        # create data
        self.getData()[str(MsgParts.MSG)] = message
        
        
class ManSubmitter(Submitter):
    def __init_(self):
        super().__init__()
        
    def send_message(self, vector_time, message):#, subm_id, subm_ip, subm_port, recv_id, recv_ip, recv_port): 
        '''
        Send message to receiver.
        
        @param message: message to be send
        @type message: string
        @param id: node id from sender
        @type id: string
        @param ip: destination ip
        @type ip: string
        @param port: destination port
        @type port: string 
        
        
        '''  
                  
        # create ZMQ context
        __context = zmq.Context()
        # set max time for send a message
        __context.setsockopt(LINGER, int(pref.getLingerTime()))#node_message.LINGER_TIME)
        # set max time for receive a response
        #__context.setsockopt(RCVTIMEO, node_message.RCVTIMEO_TIME)
        # create ZMQ_PUSH Socket        
        __socket = __context.socket(PUSH)
        #self.__context.setsockopt(LINGER, 0)        
        #self.__LOGGER.debug(subm_id + " connect to: ip - " + str(recv_ip) + " port - " + str(recv_port))
        self.getLogger().debug(message.getSubmId() + " connect to: ip - " + message.getRecvIp() + " port - " + message.getRecvPort())
        # bind socket to ip and port        
        __socket.connect("tcp://" + message.getRecvIp() + ":" + message.getRecvPort())
        #self.__LOGGER.info(subm_id + " send message an [" + recv_id + "]: " + message)  
              
        # send message        
        
        self.getLogger().info(self.__getLogString(message))
        __socket.send_string(message.toJson())
        __socket.close()
        __context.destroy()
        
    def __getLogString(self, msg):
        recv_id = msg.getRecvId()
        global IDENT
        recv_str = IDENT + " send message on [" + recv_id + "]: " + str(msg)
        return recv_str

def __print_menue():
    print("*******************************")
    print("* 1: Print all avalable Nodes *")
    print("* 2: Shutdown node            *")
    print("* 3: Shutdown all nodes       *")
    print("* 4: Send message             *")
    print("* 5: Tell rumor               *")
    print("* 7: Statistic                *")
    print("* 8: Get whisper state        *")
    print("* 0: Exit manager             *")
    print("*******************************")
    
def __readNodeInfos(fileName):    
    '''
    Read node infos from a file, store these in a dictionary and start Nodes in a separate process.
    
    @param fileName: file, contains node informations on form <id> <ip:port> ex. 0 127.0.0.1:5000
    '''
        
    file = open(str(fileName), __FILE_ACCESS_MODE)
    
    for line in iter(lambda: file.readline(), ''):
        # split id
        buffer = line.split()
        node_id = buffer[0]
        
        # split ip and port
        buffer = buffer[1].split(":")
        node_ip = buffer[0]
        node_port = buffer[1]
    
        # save node in a list
        __NODES[node_id] = {"id":node_id, "ip":node_ip, "port":node_port}
    
    #close file    
    file.close()
   
def __printAllNodes():
    '''
    Print the node list.
    '''
    for i in __NODES:
        print("ID: " + __NODES[i]["id"] + " IP: " + __NODES[i]["ip"] + " PORT: " + __NODES[i]["port"])

def __shutdownNodes():
    '''
    Shutdown all nodes
    '''
    for i in __NODES:        
        __send(i, MsgType.QUIT, "go offline!")  
        
def __shutdownNode():
    '''
    Shutdown node
    '''
    node_id = input("Node ID: ")    
    
    if __send(node_id, MsgType.QUIT, " go offline") == 0:         
        try:
            __NODES.pop(node_id)
        except KeyError:
            __LOGGER.info(IDENT + "node [" + node_id + "] not exist!")
        
def __send(node_id, msg_type, msg):
    '''
    Send a message to a node
    '''

    # check node id
    if node_id in __NODES.keys():
        msg_buf = ManMessage()
        msg_buf.init(vector_time, IDENT, __IP, __PORT, node_id, __NODES[node_id]["ip"], __NODES[node_id]["port"], msg_type, msg)
        t0 = timer()
        ManSubmitter().send_message(vector_time, msg_buf)
        t1 = timer()
        __LOGGER.debug(IDENT + " t1 - t0 = " + str(t1 - t0))
        if (t1 - t0) >= int(pref.getLingerTime())/1000:
            __LOGGER.info(IDENT + "node [" + node_id + "] is not reachable!")
            return -1
        else:
            return 0
    else:
        __LOGGER.info(IDENT + "node id [" + node_id +"] is not in the list!")
        return -1
    

def __sendMsgToNode():
    '''
    Read node id  and message to send from stdoin and call __send() to
    send the message
    '''
    node_id = input("Node ID: ")
    msg = input("Message to send: ")
    __send(node_id, MsgType.MESSAGE, msg) 

def __tellRumor():
    '''
    Read node id from stdoin and call __doWhisper(..) to
    send a rumor to the node
    '''
    node_id = input("Node ID:")
    __doWhisper(node_id)

def __doWhisper(node_id):
    '''
    Send a rumor to the given node id.
    '''
    __send(node_id, MsgType.RUMOR, "rumor")
    

def __getWhisperState():
    node_id = input("Node ID: ")
    if __send(node_id, MsgType.RUMOR_STATE, " get rumor state") != -1:
        context = zmq.Context()
        context.setsockopt(RCVTIMEO, int(pref.getRcvtimeoTime()))
        socket = context.socket(PULL)
        socket.bind("tcp://" + __IP + ":" + __PORT)
        json_str = socket.recv_string()
        msg_buf = Message()
        msg_buf.toMessage(json_str)
        
        __LOGGER.info(IDENT + "node[" + msg_buf.getSubmId() + "]: my state is: " + 
                      msg_buf.getMsg())
        socket.close()
        context.destroy()    

def __getState(node_id):
    if __send(node_id, MsgType.RUMOR_STATE, " get rumor state") != -1:
        context = zmq.Context()
        socket = context.socket(PULL)
        socket.bind("tcp://" + __IP + ":" + __PORT)
        json_str = socket.recv_string()
        msg_buf = Message()
        msg_buf.toMessage(json_str)    
        __LOGGER.debug(msg_buf.getMsg())      
        socket.close()
        context.destroy()
        return msg_buf.getMsg()
    else:
        return -1

def __getStatistic():
    '''
    Get rumor statistic on stdout.
    '''
    true = 0
    false = 0
    not_reachable = 0
    for node_id in __NODES:
        state = __getState(node_id)
        if str(state) == MsgType.TRUE:
            true += 1
        elif str(state) == MsgType.FALSE:
            false += 1
        else:
            not_reachable += 1
    true_false.append("| " + str(true) + "   | | " + str(false) + "   |")
    print("| n  | | m  | | c | | true | | false | | not reachable |")
    print("| %s | | %s | | %s | | %s    | | %s    | |  %s         |" % (pref.getNumberOfNodes(), pref.getNumberOfEdges(), pref.getTrust(), str(true), str(false), 
                                                                      str(not_reachable)))

def __initVectorTime():
    vector = []
    for i in range(0, int(pref.getNumberOfNodes())):
        vector.append(i - i) # init with zero
    return vector    
   
options = {
        1 : __printAllNodes,
        2 : __shutdownNode,
        3 : __shutdownNodes,
        4 : __sendMsgToNode,
        5 : __tellRumor,
        7 : __getStatistic,
        8 : __getWhisperState,
    }


if __name__ == '__main__':
    __LOGGER.debug(IDENT + " start ...")
    # load settings
    pref = Settings()
    pref.loadSettings()
    true_false = []
    vector_time = __initVectorTime()
    
    if pref.isGraphviz():
        __LOGGER.debug(IDENT + " Graphviz is on ...")
        __NODES = pref.getNodeInfos()
        __LOGGER.debug(IDENT + " avalable nodes: " + str(__NODES))
        print(str(__NODES))
    else:
        __NODES = pref.getNodeInfos()
            
    select = "-1"
    while select != "0":
        __print_menue()
        select = input("Your selection: ")
        try:
            if select != "0":
                options[int(select)]()
            else:
                print("Bye-bye!")
        except KeyError:
            __LOGGER.info("Invalid option, please try again!")




        