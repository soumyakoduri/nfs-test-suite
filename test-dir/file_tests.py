#!/usr/bin/python
import os,sys
sys.path.insert(0, '../')
from success import success
from counter import  counter
from logger import logger

count =0
log_file=sys.argv[1]

class  Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open(log_file, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)


#sys.stdout= Logger()
logger(log_file)
print "==============================FILE TESTS BEGIN============================="

#Unit test1: Creating files on the mountpoint;

def test2_1 ():
                #message.header2("2.1")
                try:
                        for i in range(1,10):
                                s="file"
                                s+=str(i)
                                #printf1("os.mkdir('/mnt/ganesha-mnt/",s)
                                fo=open('/mnt/ganesha-mnt/%s'%s,'w')
                                fo.close()
                except OSError as ex:
                       print(ex)
                       print " Test 2.1: FAIL"
                else:
                       success("2.1")
		       global count
		       count = count + 1



#Unit test2 : Writing into the files created;

def test2_2():
               # message.header2("2.1")
                try:
                        for i in range(1,10):
                                s="file"
                                s+=str(i)
                                #printf1("os.mkdir('/mnt/ganesha-mnt/",s)
                                fo=open('/mnt/ganesha-mnt/%s'%s,'w')
                                fo.write("This is a test to check if the file is written")
                                fo.close
                except IOError as ex:
                        print (ex)
                        print "Test 2.2:FAIL"
                else:
                        success("2.2")
			global count
			count = count + 1
#Unit test3 : Reading from the files created ;

def test2_3():
        try:
                for i in range(1,10):
                                s="file"
                                s+=str(i)
                                #printf1("os.mkdir('/mnt/ganesha-mnt/",s)
                                fo=open('/mnt/ganesha-mnt/%s'%s,'r')
                                fo.read(10)
                                fo.close
        except IOError as ex:
                 print(ex)
                 print "Test 2.3:FAIL"
        else:
                 success("2.3")
	         global count
		 count = count + 1

#Unit test4 : Removing the files created;

def test2_4():
        try:
                for i in range(1,10):
                        s="file"
                        s+=str(i)
                        os.remove("/mnt/ganesha-mnt/%s"%s)
        except OSError as ex :
                print (ex)
                print "Test 2.4:FAIL"
        else:
                success("2.4")
		global count
		count = count + 1

test2_1()
test2_2()
test2_3()
test2_4()

if count == 4:
        print "FILE TESTS                   : PASS"
	counter(1)
else:
	print "FILE TESTS                   : FAIL"

print "==============================FILE TESTS END==============================="


