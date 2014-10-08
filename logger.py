#!/usr/bin/python

import sys

def  logger(log_file):
        class  Logger(object):
                def __init__(self):
                        self.terminal = sys.stdout
                        self.log = open(log_file, "a")
                def write(self, message):
                        self.terminal.write(message)
                        self.log.write(message)

        sys.stdout = Logger()

