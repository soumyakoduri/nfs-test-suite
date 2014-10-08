#!/usr/bin/python
import os
import counter

def print_results(total):
        passed = counter.get_value();
        failed = total - passed

        print ""
        print "==============================Results===================================="
        print " Total tests run : %d  " %total
        print " Tests passed    : %d  " %passed
        print " Tests failed    : %d  " %failed
        print "========================================================================="

	

