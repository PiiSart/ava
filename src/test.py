'''
Created on 20.01.2017

@author: viwe
'''
from node.node_message import Message, MsgType
import random
from abc import abstractmethod
from queue import PriorityQueue

    
       
if __name__ == '__main__':
    
    q = PriorityQueue()
    q.put(5)
    q.put(3)
    q.put(10)
    
    for i in range(q.qsize()):
        print(q.get())
    