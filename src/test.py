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
        self._test = "Fick dich"
        
    def printTest(self):
        print(self._test)
        
        


class B(A):
    def __init__(self):
        super().__init__()
        self.__blad = "blad"
    
    def getBlad(self):
        return self.__blad


class D(A):
    def __init__(self):
        #super().__init__()
        self.__suka = "sucka"
    
    def getBlad(self):
        return self.__suka

class C(object):
    def __init__(self, A):
        self.__a = A
        self.__a.printTest()
        print(self.__a.getBlad())
        print(self.__a._test)
    
    
       
if __name__ == '__main__':
    b = B()
    d = D()
    c = C(d)
    
    
    