#!/usr/bin/python
import os
import glob
import re


def check_list(test_list, version):
	complete_test_list=[]
	os.chdir("./test-dir")
	for file in glob.glob("*.py"):
        	#print file
        	complete_test_list.append(file)
	os.chdir("..")
	print complete_test_list[0:]
        if test_list:
                test_list = [test + '.py' for test in test_list]
                for test in test_list:
                        if test not in complete_test_list:
                                print "%s is not a valid test, skipping it." %test
                                test_list.remove(test)
                if (version == "3" and "pynfs_tests.py" in test_list):
                        print "pynfs is a v4 specific test, skipping  it."
                        test_list.remove("pynfs_tests.py")
        else:
                test_list.extend(complete_test_list)
        return test_list


