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
print "=============================FILEOP TESTS BEGIN============================="
call('time /opt/qa/tools/system_light/run.sh -w /mnt/ganesha-mnt -l /export/fileop.log -t fileop > /export/fileop.log',shell=True)
print "Log file : /export/fileop.log"
ret=compare("Total 1 tests were successful","/export/fileop.log")
if ret == 1:
        print "FILEOP TESTS                   : PASS"
	counter(1)
else:
        print "FILEOP TESTS                   : FAIL"

print "==============================FILEOP TESTS END=============================="

