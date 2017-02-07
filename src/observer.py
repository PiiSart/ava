'''
Created on 06.02.2017

@author: Viktor Werle
'''

import zmq
from zmq.backend.cython.constants import PULL
from node.node_message import Message, MsgType
from util.settings import Settings

class Observer(object):
    '''
    Observer
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.ip = "127.0.0.1"
        self.port = "11000"
        self.__survey = {}
        self.__eval = {}
        self.__end_survey = {}
        self.__term_nodes = 0
        self.__number_of_ready_nodes = 0
        self.__pref = Settings()
        self.__pref.loadSettings()
        self.receiver()
        

    def receiver(self):
        '''
        Start the loop to receive the messages from client. The server will be 
        stopped by the message 'quit'!
        '''      
        #self.__LOGGER.debug(self.__node.getIdent() + "init receiver ...")
        self.__message = " "
        
        # create ZMQ context
        self.__context = zmq.Context()
        
        # create ZMQ_REP Socket (incoming strategie: Faire-queued)
        self.__socket = self.__context.socket(PULL)
        # bind socket to ip and port
        self.__socket.bind("tcp://" + self.ip + ":" + self.port)
               
        while True:#self.__quit == False:
            # receive message
            msg_str = self.__socket.recv_string()
            #print("empfangen!")
            # create message obj
            msg = Message()
            # import values from json string
            msg.toMessage(msg_str)     
            #print(msg.getMsgType())       
                                   
            if msg.getMsgType() == MsgType.READY:
                self.__number_of_ready_nodes += 1
                #print("Anzahl Knoten gesamt: " +  self.__pref.getNumberOfNodes())
                if self.__number_of_ready_nodes == int(self.__pref.getNumberOfNodes()):
                    self.printSurvey()
            elif msg.getMsgType() == MsgType.RESET:
                self.__resetSurvey()
            
            elif msg.getMsgType() == MsgType.MY_VOTE:
                #print(msg.getMsgType())
                self.__term_nodes += 1
                if self.__term_nodes >= int(self.__pref.getNumberOfNodes()) - 2:
                    self.printEndSurvey()
                else:
                    self.__recordEndSurvey(msg)
            
            else:
                self.record(msg)            
        
        self.__clear()
    
    def __recordEndSurvey(self, msg):
        '''
        Save confidence levels of candidates after reach the termination time.
        '''
        self.__end_survey[msg.getSubmId()] = msg.getCLevels()
    
    def __resetSurvey(self):
        '''
        Reset survey.
        '''
        print("********************************")
        print("* RESET...                     *")
        print("********************************")
        self.__survey = {}
        self.__eval = {}
        self.__end_survey = {}
        self.__term_nodes = 0
        self.__number_of_ready_nodes = 0
        self.__pref = Settings()
        self.__pref.loadSettings()
        
    def __clear(self):
        '''
        Close socket connection and destroy 0MQ context
        '''
        #self.__LOGGER.debug(self.__node.getIdent() + "close socket ...")
        self.__socket.close()
        #self.__LOGGER.debug(self.__node.getIdent() + "destroy context ...")
        self.__context.destroy()
        
    
    def record(self, msg):
        '''
        Save the incoming survey values.
        '''
        #print("Message Type: " + msg.getMsgType())
        if msg.getMsgType() == MsgType.VOTE_FOR_ME:
            self.calcVoteForMe(msg)
        
        if msg.getMsgType() == MsgType.CAMPAIGN:
            self.calcCampaign(msg)
        
        if msg.getMsgType() == MsgType.MESSAGE:
            self.__survey[msg.getSubmId()] = msg.getCLevels()
       
    
    def calcCampaign(self, msg):
        '''
        Calculate the CAMPAIGN results.
        '''
        node_id = msg.getSubmId()
        # no record available
        if node_id not in self.__survey:
            self.__survey[node_id] = msg.getCLevels()
        else:# calculate
            c_levels = msg.getCLevels()
            cand_one = c_levels.pop()
            cand_two = c_levels.pop()
            c_levels = msg.getCLevels()
            if c_levels[cand_one] == c_levels[cand_two]:
                pass
            else:
                max_cand = max(c_levels, key=lambda candidate_id: c_levels[candidate_id])
                if cand_one == max_cand:
                    self.__survey[node_id][cand_one] += 1
                    self.__survey[node_id][cand_two] -= 1
                else:
                    self.__survey[node_id][cand_one] -= 1
                    self.__survey[node_id][cand_two] += 1
                
                if self.__survey[node_id][cand_one] > 100:
                    self.__survey[node_id][cand_one] = 100
                if self.__survey[node_id][cand_one] < 0:
                    self.__survey[node_id][cand_one] = 0
                
                if self.__survey[node_id][cand_two] > 100:
                    self.__survey[node_id][cand_two] = 100
                if self.__survey[node_id][cand_two] < 0:
                    self.__survey[node_id][cand_two] = 0
                
                
    def calcVoteForMe(self, msg):
        '''
        Calculate the VOTE_FOR_ME results.
        '''
        #print("calc vote for me. c_levels: " + str(msg.getCLevels()))
        node_id = msg.getSubmId()
        cand_id = msg.getCandId()
        # no record available
        if node_id not in self.__survey:
            self.__survey[node_id] = msg.getCLevels()
        else:# calculate
            c_levels = msg.getCLevels()
            for candidate in c_levels:
                if candidate == cand_id:
                    self.__survey[node_id][cand_id] += c_levels[cand_id] / 10
                    if self.__survey[node_id][cand_id] > 100:
                        self.__survey[node_id][cand_id] = 100
                    if self.__survey[node_id][cand_id] < 0:
                        self.__survey[node_id][cand_id] = 0
            
                    
    def __getLogString(self, msg):
        #ident = self.__node.getIdent()
        subm_id = msg.getSubmId()
        
        #recv_str = msg.getRecvId() + " receive message from [" + subm_id + "]: " + str(msg) + " [C_LEVELS]: " + str(msg.getCLevels())
        recv_str = "NODE [%s] C_LEVELS: %s" % (subm_id, msg.getMsg())
        return recv_str

    

    def printSurvey(self):
        '''
        Get out the result of survey on stdout.
        '''
        print("*********************************")
        print("Result of survey: " )
        print("*********************************")
        str_buf = ""
        for node_id in self.__survey:
            str_buf = "Node[%s] : " % (node_id) 
            c_levels = self.__survey[node_id]
            cand_1, level_1 = c_levels.popitem()
            cand_2, level_2 = c_levels.popitem()
            str_buf += "Cand[%s]: %s   |   Cand[%s]: %s \n"  % (cand_1, level_1, cand_2, level_2)
            
            if level_1 > level_2:
                self.evaluation(cand_1)
            elif level_1 < level_2:
                self.evaluation(cand_2)
            else:
                self.evaluation("avoid")
            
            #print(str_buf)
            
        # summary
        print("*********************************")
        print("Summary: ")
        print("*********************************")
        str_buf = ""
        for key in self.__eval:            
            str_buf += "[%s] : %s  |   " % (key, self.__eval[key])
        str_buf += "\n"
        
        print(str_buf)   
            
            
    def printEndSurvey(self):
        '''
        Get out the end result of survey on stdout.
        '''
        print("*********************************")
        print("Result of end survey: " )
        print("*********************************")
        str_buf = ""
        for node_id in self.__end_survey:
            str_buf = "Node[%s] : " % (node_id) 
            c_levels = self.__end_survey[node_id]
            cand_1, level_1 = c_levels.popitem()
            cand_2, level_2 = c_levels.popitem()
            str_buf += "Cand[%s]: %s   |   Cand[%s]: %s \n"  % (cand_1, level_1, cand_2, level_2)
            
            if level_1 > level_2:
                self.evaluation(cand_1)
            elif level_1 < level_2:
                self.evaluation(cand_2)
            else:
                self.evaluation("avoid")
            
            print(str_buf)
        
        
        # summary
        print("*********************************")
        print("Summary: ")
        print("*********************************")
        str_buf = ""
        for key in self.__eval:            
            str_buf += "[%s] : %s  |   " % (key, self.__eval[key])
        str_buf += "\n"
        
        print(str_buf)
        
        
    def evaluation(self, cand_id):
        if cand_id not in self.__eval:
            self.__eval[cand_id] = 1   
        else:
            self.__eval[cand_id] += 1

if __name__ == '__main__':
    o = Observer()