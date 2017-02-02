'''
Created on 20.01.2017

@author: viwe
'''
from node.node_message import Message, MsgType
import random
from node.voter_node import Voter
from abc import abstractmethod

class A(object):
    def __init__(self):
        pass
        
    def printTest(self, strr):
        print(str)
        
        


class B(A):
    def __init__(self):
        super().__init__()
        self.__blad = "blad"
    
    def printTest(self, strr):
        #print("Hallo Ihr Pennder!")
        A.printTest(self, "Hallo")
        #print("Bla bla: " + strr)

    
       
if __name__ == '__main__':
    b = B()
    b.printTest("selber Penner")
    
    
    