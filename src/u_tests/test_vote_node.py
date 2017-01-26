'''
Created on 26.01.2017

@author: viwe
'''
import unittest
from node.voter_node import Voter
from node.node_message import Message, MsgType


class TestVoter(unittest.TestCase):


    def setUp(self):
        self.__voter = Voter("1")
        
        # vector time
        self.__vector_time = [0, 0, 0]
        # submitter
        self.__subm_id = "0"
        self.__subm_ip = "127.0.0.1"
        self.__subm_port = "5000"
        self.__c_levels = {"0": 10, "9": 20}
        
        # receiver
        self.__recv_id = "1"
        self.__recv_ip = "127.0.0.1"
        self.__recv_port = "5001"
        
        # candidate
        self.__cand_id = "0"
        self.__cand_ip = "127.0.0.1"
        self.__cand_port = "5001"
        
        # create message
        self.__msg = Message()
        self.__msg.setSubm(self.__subm_id, self.__subm_ip, self.__subm_port, self.__c_levels)
        self.__msg.setRecv(self.__recv_id, self.__recv_ip, self.__recv_port)
        self.__msg.setCand(self.__cand_id, self.__cand_ip, self.__cand_port) 
        
        # message string
        self.__message = "hallo" 
        
        # create msg
        self.__msg.create(self.__vector_time, MsgType.VOTE_FOR_ME, self.__message)

    def tearDown(self):
        pass


    def testIncConfedenceLevel(self):
        print(self.__voter.incConfedenceLevel(self.__msg))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()