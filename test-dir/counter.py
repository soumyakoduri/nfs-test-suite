#!/usr/bin/python
import os	
	
	
def counter(count):
	if  os.path.isfile('/tmp/counter.txt') == False:
		fo = open('/tmp/counter.txt','w')
		fo.write("0")
		fo.close()
	
	fo =open('/tmp/counter.txt','r')
	str1=fo.read()
	fo.close()
	
	num=int(str1)
	num=num+count
	num1=str(num)
	fo = open('/tmp/counter.txt','w')
	fo.write("%s"%num1)
	fo.close()
	return num;

def reset():
	fo = open('/tmp/counter.txt','w')
	fo.write("0")
	fo.close()
        

def get_value():
	fo =open('/tmp/counter.txt','r')
	str1=fo.read()
	fo.close()
	num=int(str1)
	return num;
	
	
