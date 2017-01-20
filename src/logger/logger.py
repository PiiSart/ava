'''
Created on 27.10.2016

Looger to log network communication. Logger settings are in the folder conf/logger


@author: Viktor Werle
'''

from os import path
import logging
from logging import config

class NodeLogger(object):
    '''
    Logger
    '''
    ROOT = "root"
    NODE = "node"
    SUBMITTER = "submitter"
    RECEIVER = "receiver"
    MANAGER = "manager"
    
    def __init__(self):
        self.__CONFIG_FILE = path.join(path.dirname(path.abspath(__file__)), '../../conf/logger/logging_config.ini')

    def getLoggerInstance(self, lgr_name):
        '''
        Get a logger instance
        
        @param lgr_name: logger name (match config file)
        @type lgr_name: string
        '''
        # load config-file
        config.fileConfig(self.__CONFIG_FILE, defaults=None, disable_existing_loggers=False)
        return logging.getLogger(str(lgr_name))

