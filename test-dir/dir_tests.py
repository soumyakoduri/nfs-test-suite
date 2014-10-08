#!/usr/bin/python
import sys,time
from success import success
import os
import shutil
sys.path.insert(0, '../')
from counter import counter
from logger import logger


log_file = sys.argv[1]

count = 0

class  Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open(log_file, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)

#sys.stdout = Logger()
logger(log_file)

#First testcase : Directory based tests

#Unit test1 : Creating directories on the mount point;
print "=============================DIR TESTS BEGIN============================="
def test1_1 ():
                #message.header2("1.1",log_file)
                try:
                        for i in range(1,10):
                                s="dir"
                                s+=str(i)
                                #printf1("os.mkdir('/mnt/ganesha-mnt/",s)
                                os.mkdir('/mnt/ganesha-mnt/%s'%s) 
                except OSError as ex:
                       print(ex)
                       print " Test 1.1: FAIL"
                else:
                       success("1.1")
		       global count
		       count = count + 1
                #time.sleep(2)
                #message.end1("1.1")

#Unit test2 : Creating subdirectories on the mount point;

def test1_2 ():
                #message.header2("1.2")
                try:
                        for i in range(1,10):
                                s="dir"
                                s+=str(i)
                                for j in range(1,3):
                                        k="dir"
                                        k+=str(j)
                                       # print "os.mkdir('/mnt/ganesha-mnt/%s/%s')" %(s,k)
                                        os.mkdir('/mnt/ganesha-mnt/%s/%s' %(s,k))
                except OSError as ex:
                        print (ex)
                        print "Test 1.2 : FAIL "
                else:
                        success("1.2")
			global count
			count = count + 1
               # message.end1("1.2")

#Unit test3: Creating files on the directories created;

def test1_3 ():
                #message.header2("1.3")
                try:
                        for i in range(1,10):
                                s="dir"
                                s+=str(i)
                                for j in range(1,10):
                                        k="file"
                                        k+=str(j)
                                       # print"open('/mnt/ganesha-mnt/%s/%s' %(s,k),'w')"
                                        fo1 = open('/mnt/ganesha-mnt/%s/%s' %(s,k),'w')
                                        fo1.close()
                except IOError as ex:
                        print (ex)
                        print "Test 1.3 : FAIL"

                else:
                        success("1.3")
			global count
			count = count + 1
                #message.end1("1.3")

#Unit test4 : Removing directories recursively;

def  test1_4 ():
                #message.header2("1.4")
                try:
                        for i in range(1,10):
                                s="dir"
                                s+=str(i)
                                shutil.rmtree('/mnt/ganesha-mnt/%s'%s)
                except OSError as ex:
                        print (ex)
                        print "Test 1.4 : FAIL"
                else:
                        success("1.4")
			global count
			count = count + 1
                #message.end1("1.4")



test1_1()
test1_2()
test1_3()
test1_4()

if count == 4:
        print "DIR TESTS                   : PASS"
        counter(1)
else:
        print "DIR TESTS                   : FAIL"
print "==============================DIR TESTS END=============================="

