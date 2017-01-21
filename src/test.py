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

class A(object):
    def __init__(self):
        self.__id = "5"
        self.__ip = [0, 1, 2 , 3]
    
    def __str__(self):
        #print(args)
        #print(kwargs)
        #print(object)
        return str(self.__ip)
    
    
        
class B(object):
    def __init__(self):
        pass
    
    def my(self, A):
        pass
    
    
if __name__ == '__main__':
    a = A()
    print("Blub", a)
    
    