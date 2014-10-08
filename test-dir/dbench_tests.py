#!/usr/bin/python
from subprocess import call
from logger import logger
import sys
log_file=sys.argv[1]
sys.path.insert(0, '../')
logger(log_file)
from counter import counter
from compare import compare


call('./run-qa.sh',shell=True)
print "=============================DBENCH TESTS BEGIN============================="
call('time /opt/qa/tools/system_light/run.sh -w /mnt/ganesha-mnt -l /export/dbench.log -t dbench > /export/dbench.log',shell=True)
print "Log file : /export/dbench.log"
ret=compare("Total 1 tests were successful","/export/dbench.log")
if ret == 1:
        print "DBENCH TESTS                   : PASS"
	counter(1)
else:
        print "DBENCH TESTS                   : FAIL"

print "==============================DBENCH TESTS END=============================="

