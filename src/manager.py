#!/usr/bin/python3
'''
Created on 21.12.2016

Manager. Can communicate with nodes.

@author: Viktor Werle
'''


from node.node_submitter import Submitter
from logger.logger import NodeLogger
from node import node_message
from util.settings import Settings
import zmq
from zmq.backend.cython.constants import PULL, RCVTIMEO
from timeit import default_timer as timer

__IDENT = "Manager--> "
__FILE_ACCESS_MODE = "r"
__NODES = {}
__LOGGER = NodeLogger().getLoggerInstance(NodeLogger.MANAGER)
__IP = "127.0.0.1"
__PORT = "10000"

def __print_menue():
    print("*******************************")
    print("* 1: Print all avalable Nodes *")
    print("* 2: Shutdown node            *")
    print("* 3: Shutdown all nodes       *")
    print("* 4: Send message             *")
    print("* 5: Tell whisper             *")
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
        __send(i, node_message.QUIT)  
        
def __shutdownNode():
    '''
    Shutdown node
    '''
    node_id = input("Node ID: ")
    
    if __send(node_id, node_message.QUIT) == 0:         
        try:
            __NODES.pop(node_id)
        except KeyError:
            __LOGGER.info(__IDENT + "node [" + node_id + "] not exist!")
        
def __send(node_id, msg):
    '''
    Send a message to a node
    '''

    # check node id
    if node_id in __NODES.keys():
        t0 = timer()
        Submitter().send_message(msg, __IDENT, __IP, __PORT, str(__NODES[node_id]["id"]), str(__NODES[node_id]["ip"]), str(__NODES[node_id]["port"]))
        t1 = timer()
        __LOGGER.debug(__IDENT + " t1 - t0 = " + str(t1 - t0))
        if (t1 - t0) >= int(pref.getLingerTime())/1000:
            __LOGGER.info(__IDENT + "node [" + node_id + "] is not reachable!")
            return -1
        else:
            return 0
    else:
        __LOGGER.info(__IDENT + "node id [" + node_id +"] is not in the list!")
        return -1
    

def __sendMsgToNode():
    '''
    Read node id  and message to send from stdoin and call __send() to
    send the message
    '''
    node_id = input("Node ID: ")
    msg = input("Message to send: ")
    __send(node_id, msg) 

def __tellWhisper():
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
    __send(node_id, node_message.WHISPER)
    

def __getWhisperState():
    node_id = input("Node ID: ")
    if __send(node_id, node_message.WHISPER_STATE) != -1:
        context = zmq.Context()
        context.setsockopt(RCVTIMEO, int(pref.getRcvtimeoTime()))
        socket = context.socket(PULL)
        socket.bind("tcp://" + __IP + ":" + __PORT)
        msg = socket.recv_string()
        msg = node_message.convMessageStrToObj(msg)
        __LOGGER.info(__IDENT + "node[" + msg[node_message.HEADER][node_message.SUBM_ID] + "]: my state is: " + 
                      msg[node_message.DATA][node_message.MSG])      
        socket.close()
        context.destroy()    

def __getState(node_id):
    if __send(node_id, node_message.WHISPER_STATE) != -1:
        context = zmq.Context()
        socket = context.socket(PULL)
        socket.bind("tcp://" + __IP + ":" + __PORT)
        msg = node_message.convMessageStrToObj(socket.recv_string())    
        __LOGGER.debug(msg)      
        socket.close()
        context.destroy()
        return msg[node_message.DATA][node_message.MSG]
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
        if str(state) == node_message.TRUE:
            true += 1
        elif str(state) == node_message.FALSE:
            false += 1
        else:
            not_reachable += 1
    true_false.append("| " + str(true) + "   | | " + str(false) + "   |")
    print("| n  | | m  | | c | | true | | false | | not reachable |")
    print("| %s | | %s | | %s | | %s    | | %s    | |  %s         |" % (pref.getNumberOfNodes(), pref.getNumberOfEdges(), pref.getTrust(), str(true), str(false), 
                                                                      str(not_reachable)))
    
   
options = {
        1 : __printAllNodes,
        2 : __shutdownNode,
        3 : __shutdownNodes,
        4 : __sendMsgToNode,
        5 : __tellWhisper,
        7 : __getStatistic,
        8 : __getWhisperState,
    }


if __name__ == '__main__':
    __LOGGER.debug(__IDENT + " start ...")
    # load settings
    pref = Settings()
    pref.loadSettings()
    true_false = []
    
    if pref.isGraphviz():
        __LOGGER.debug(__IDENT + " Graphviz is on ...")
        __NODES = pref.getNodeInfos()
        __LOGGER.debug(__IDENT + " avalable nodes: " + str(__NODES))
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


