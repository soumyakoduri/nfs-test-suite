#!/usr/bin/python

import subprocess,os,sys,counter,time
from subprocess import call
log_file=sys.argv[4]
sys.path.insert(0, '../')
class  Logger(object):
        def __init__(self):

                self.terminal = sys.stdout
                self.log = open(log_file, "a")
        def write(self, message):
                self.terminal.write(message)
                self.log.write(message)
sys.stdout =  Logger()
print "============================== PYNFS TESTS BEGIN==============="

server_ip=sys.argv[1]
export=sys.argv[2]
#confile=sys.argv[2]
known_failures = int (sys.argv[3])
print "known_failures"
print known_failures
#setup.setup("pynfs-test-volume",server_ip,client_ip,confile)
#mount("pynfs-test-volume",server_ip,"4")
if os.path.ismount('/mnt/ganesha-mnt') == True:
        #time.sleep(30)
        if os.path.isdir("pynfs")== True:
	        call('rm -rf pynfs',shell=True)
        call(' git clone git://linux-nfs.org/~bfields/pynfs.git',shell=True)
        cur = os.getcwd()
        os.chdir("pynfs")
        call('yes  | python setup.py build >/dev/null 2>/dev/null' ,shell=True)
        os.chdir("nfs4.0")

        os.environ['server_ip'] = server_ip
        time.sleep(45)
        ret = call('./testserver.py  -v --outfile ~/pynfs.run.1 --maketree $server_ip:/$export --showomit --rundeps  all > /tmp/pynfs-results.log',shell=True)

        if  ret:
	        print "pynfs tests failed, check logfile for details"
	        print " TEST 3 : FAIL"
	        print "==============================TEST 3 ENDS================================="
	else:
                os.chdir(cur)
                os.system('cat /tmp/pynfs-results.log| grep "Command" | cut -d " " -f5 > /tmp/pynfs-log.txt')
                fo = open ('/tmp/pynfs-log.txt','r')
                total = int( fo.read())
                fo.close()
                os.system('cat /tmp/pynfs-results.log| grep "Of those" | cut -d " " -f5 > /tmp/pynfs-log.txt')
                fo = open ('/tmp/pynfs-log.txt','r')
                failures=int(fo.read())
                fo.close()
                os.system('cat /tmp/pynfs-results.log| grep "Of those" | cut -d " " -f9 > /tmp/pynfs-log.txt')
                fo = open ('/tmp/pynfs-log.txt','r')
                passed=int(fo.read())
                fo.close()


                print "===============================Pynfs tests================================================"
                print "TOTAL           : %d " %total
                print "FAILURES        : %d " %failures
                print "PASS            : %d " %passed

                new_failures = failures - known_failures
                if new_failures > 0 :
	                if total == "568" :
		                print "PYNFS TESTS                   : FAIL"
			        print "Check /tmp/pynfs-results.log for results"

                else:
	                        print "PYNFS TESTS                   : PASS"
	                        counter.counter(1)
                print "====================================PYNFS TESTS END=========================================="
else:
        print "Mount failed,skipping pynfs tests."
