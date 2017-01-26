'''
Created on 26.01.2017

@author: viwe
'''
import unittest
from node.node_message import Message, MsgType, MsgParts


class TestMessage(unittest.TestCase):


    def setUp(self):
        # vector time
        self.__vector_time = [0, 0, 0]
        # submitter
        self.__subm_id = "0"
        self.__subm_ip = "127.0.0.1"
        self.__subm_port = "5000"
        self.__c_levels = {"5": 10, "20": 20}
        
        # receiver
        self.__recv_id = "1"
        self.__recv_ip = "127.0.0.1"
        self.__recv_port = "5001"
        
        # candidate
        self.__cand_id = "1"
        self.__cand_ip = "127.0.0.1"
        self.__cand_port = "5001"
        
        # create message
        self.__msg = Message()
        self.__msg.setSubm(self.__subm_id, self.__subm_ip, self.__subm_port, self.__c_levels)
        self.__msg.setRecv(self.__recv_id, self.__recv_ip, self.__recv_port)
        self.__msg.setCand(self.__cand_id, self.__cand_ip, self.__cand_port) 
        
        # message string
        self.__message = "hallo"       
        
        # dictionary subsets
        # header
        self.__subset_header = {}
        self.__subset_header[MsgParts.VECTOR_TIME] = self.__vector_time
        self.__subset_header[MsgParts.SUBM] = {
            MsgParts.SUBM_ID:self.__subm_id, 
            MsgParts.SUBM_IP:self.__subm_ip, 
            MsgParts.SUBM_PORT: self.__subm_port, 
            MsgParts.C_LEVELS: self.__c_levels
            }
        self.__subset_header[MsgParts.RECV] = {
            MsgParts.RECV_ID:self.__recv_id, 
            MsgParts.RECV_IP:self.__recv_ip, 
            MsgParts.RECV_PORT: self.__recv_port            
            }
        self.__subset_header[MsgParts.CAND] = {
            MsgParts.CAND_ID:self.__cand_id, 
            MsgParts.CAND_IP:self.__cand_ip, 
            MsgParts.CAND_PORT: self.__cand_port 
            }
        
        # submitter
        

    def tearDown(self):
        pass


    def testGetHeader(self):
        self.__msg.create(self.__vector_time, MsgType.CAMPAIGN, self.__message)
        header = self.__msg.getHeader()
        self.assertDictContainsSubset(self.__subset_header, header)

         
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()