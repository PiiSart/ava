#!/usr/bin/python3
'''
Created on 14.01.2017

Read from setting file the settings and create config files <node_list.txt> and <graphviz.txt>

@author: Viktor Werle
'''
from util.settings import Settings

from util.gen_node_list import __generate
from util.graphgen import __createGraphviz

def writeSettingsFiles():
    '''
    Create files 'node_list.txt' and 'graphviz.txt'. Exist files will be overwrite.
    '''
    settings = Settings();
    settings.loadSettings();
    # generate node_list.txt
    __generate(int(settings.getNumberOfNodes()))
    # generate graphviz.txt
    __createGraphviz(int(settings.getNumberOfNodes()), int(settings.getNumberOfEdges()))

if __name__ == '__main__':
    writeSettingsFiles()
    