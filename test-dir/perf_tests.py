#!/usr/bin/python
import os,sys,subprocess
from subprocess import call
from counter import counter
from logger import logger 
sys.path.insert(0, '../')
count=0
server_ip=sys.argv[2]
log_file=sys.argv[1]
logfile='/tmp/perftest.txt'

class  Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open(log_file, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)

#sys.stdout = Logger()
#logger(log_file)

def compare(search_str):
        global count
        search_file = open(logfile, "r")
	failed_cases = 0

        for line in search_file:
                if line.strip() == search_str:
                        failed_cases = failed_cases + 1
                        print failed_cases

	if failed_cases == 0:
		count = count + 1
		#print count

        search_file.close()
#sys.stdout=Logger()
logger(log_file)


print "==============================PERF TESTS BEGIN============================="
os.environ['server_ip']=server_ip
os.environ['logfile']=logfile

#=========Running perf tests================#
call(' ./perftest.sh /mnt/ganesha-mnt > $logfile ',shell=True)
compare("FAILED")

if count == 1:
	print "PERF TESTS                   : PASS"
	counter(1)
else:
	print "PERF TESTS                   : FAIL"
print "==============================PERF TESTS END============================="










