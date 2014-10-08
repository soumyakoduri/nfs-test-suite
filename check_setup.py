#!/usr/bin/python
import os.path
f=[]

def check_setup(name):
	test_list = [name + '_setup' + '.py']
	if (os.path.exists(test_list[0])) == False :
		print "Setup file \"%s\" not found in the current directory, exiting." %test_list[0]
		exit(1)

	
	

