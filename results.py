#!/usr/bin/python
import os

def results():
        L = list()
	os.system('cat /tmp/pynfs-results.log| grep "Command" | cut -d " " -f5 > /tmp/pynfs-log.txt')
	fo = open ('/tmp/pynfs-results.log','r')
        L.insert(0,fo.read())
        fo.close()
        os.system('cat /tmp/pynfs-results.log| grep "Of those" | cut -d " " -f5 > /tmp/pynfs-log.txt')
        fo = open ('/tmp/pynfs-results.log','r')
        L.insert(1,fo.read())
        fo.close()
        os.system('cat /tmp/pynfs-results| grep "Of those" | cut -d " " -f9 > /tmp/pynfs-log.txt')
        fo = open ('/tmp/pynfs-results.log','r')
        L.insert(2,fo.read())
        fo.close()
	return L
	

