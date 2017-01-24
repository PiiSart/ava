'''
Created on 20.01.2017

@author: viwe
'''

from enum import Enum
from datetime import datetime
from node.node_message import MsgType, MsgParts
from node.node import Node
from threading import Thread
import json
from logger.logger import NodeLogger

class A(object):
    def __init__(self):
        self.__id = "5"
        self.__ip = [0, 1, 2 , 3]
    
    def type(self):
        if True:
            msg = "Hallo"
        
        print(msg)

    
        
class B(object):
    def __init__(self):
        pass
    
    def my(self, A):
        pass
    
    
if __name__ == '__main__':
    t = A()
    t.type()
    
    
    
    