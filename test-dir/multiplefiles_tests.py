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
print "=============================MULTIPLE_FILES TESTS BEGIN============================="
call('time /opt/qa/tools/system_light/run.sh -w /mnt/ganesha-mnt -l /export/multiple_files.log -t multiple_files >/export/multiple_files.log',shell=True)
print "Log file : /export/multiple_files.log"
ret=compare("Total 1 tests were successful","/export/multiple_files.log")
if ret == 1:
        print "MULTIPLE_FILES TESTS        : PASS"
        counter(1)
else:
        print "MULTIPLE_FILES TESTS        : FAIL"

print "==============================MULTIPLE FILES TESTS END=============================="

