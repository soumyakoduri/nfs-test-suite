#!/usr/bin/python
from logger import logger

def header_1(lfile):
        logger (lfile)
        print ""
        print "==============================LOG FILES=============================="
        print " Log file for the tests run  :    %s"%lfile
        print " Log file for ganesha.nfsd   :   /root/nfs-ganesha.log on the ganesha-host"
        print " Log file for pynfs test     :   /tmp/pynfs-results.txt"
        print "====================================================================="

