#!/usr/bin/python
import os,sys
import re
import glob

dir = sys.argv[1]
print dir
os.chdir(dir)
f= []
f1= []
for file in glob.glob("test*.py"):
        print file
        f.append(file)
for test in f:
        f1.append(os.path.splitext(test)[0])
#print f1[0:]
f2 = sorted(f1, key = lambda x: int(x.split("test")[1]))
print f2[0:]
f2 = [test + '.py' for test in f2]
print f2[0:]
 
