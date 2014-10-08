#!/usr/bin/python

def compare(search_str,l_file):
        search_file = open(l_file, "r")
        for line in search_file:
                if line.strip() == search_str:
                	search_file.close()
			return 1;

