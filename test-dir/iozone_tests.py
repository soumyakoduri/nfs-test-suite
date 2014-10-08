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
print "=============================IOZONE TESTS BEGIN============================="
call('time /opt/qa/tools/system_light/run.sh -w /mnt/ganesha-mnt -l /export/iozone.log -t iozone >/export/iozone.log',shell=True)
print "Log file : /export/iozone.log"
ret=compare("Total 1 tests were successful","/export/iozone.log")
if ret == 1:
        print "IOZONE TESTS                   : PASS"
        counter(1)
else:
        print "IOZONE TESTS                   : FAIL"

print "==============================IOZONE TESTS END=============================="

