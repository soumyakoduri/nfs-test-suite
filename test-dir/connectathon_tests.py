#!/usr/bin/python
import os,sys,subprocess
from subprocess import call
from counter import counter
count=0
sys.path.insert(0, '../')
server_ip=sys.argv[2]
log_file=sys.argv[1]
logfile='/tmp/cthon-results.txt'

class  Logger(object):
        def __init__(self):
                self.terminal = sys.stdout
                self.log = open(log_file, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)

sys.stdout = Logger()

def compare(search_str):
        global count
        search_file = open(logfile, "r")

        for line in search_file:
                if line.strip() == search_str:
                        count = count + 1

        search_file.close()
sys.stdout=Logger()


print "==============================CONNECTATHON TESTS BEGIN============================"
cur=os.getcwd()
call('git clone git://fedorapeople.org/~steved/cthon04',shell=True)
call('yum -y install time',shell=True)
os.chdir('cthon04')
call('make all  >/dev/null 2>/dev/null',shell=True)
os.environ['server_ip']=server_ip
os.environ['logfile']=logfile

#=========Running cthon basic tests================#
print "Running cthon basic tests"
call(' ./server -b  -p /ganesha-test-volume -m /mnt/ganesha-mnt $server_ip  > $logfile ',shell=True)
compare("Congratulations, you passed the basic tests!")
#===========Running cthon general tests============#
print"Running cthon general tests"
call('./server -g  -p /ganesha-test-volume -m /mnt/ganesha-mnt  $server_ip >> $logfile',shell=True)
compare("General tests complete")
#===========Running cthon lock tests===============#
print"Running cthon lock tests"
call('./server -l  -p /ganesha-test-volume -m /mnt/ganesha-mnt $server_ip >> $logfile ', shell=True)
compare("Congratulations, you passed the locking tests!")
#===========Running cthon special tests============#
print"Running cthon special tests"
call('./server -s  -p /ganesha-test-volume -m /mnt/ganesha-mnt $server_ip >>$logfile ', shell=True)
compare("Special tests complete")

if count == 4:
	print "CONNECTATHON  TESTS           : PASS"
	counter(1)
else:
	print "CONNECTATHON TESTS            : FAIL"
print "==============================CONNECTATHON TESTS END============================="










