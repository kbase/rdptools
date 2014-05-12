#!/usr/bin/python
from Bio import SeqIO
import sys
import ctypes
import subprocess
import os
from optparse import OptionParser

PORT = 10004

def probematch(primers, cmdoptions, refFile):
	sys.path.append("/Users/wangqion/Desktop/KBase/workshop2014/deployment/lib")
	from RDPToolsClient import RDPTools
	service = RDPTools("http://localhost:"+str(PORT))   
	results = service.probematch(primers, cmdoptions, refFile)

	for k in results:
		print k.strip()
						
def main(args):
	usage = ("usage: %prog [options] <primer_list | primer_file> seq_file\n"
	"If multiple primers are used, you can either save the primers in a file with one primer per line,\n"
	 "or enter the primers as command-line argument, separated by ',' without space" )
		
	parser = OptionParser(usage=usage)
	parser.add_option("-d", "--max_dist", dest="max_dist", help="maximum number of differences allowed", default="0")
	
	(options, args) = parser.parse_args()
	if len(args) < 2 :
		parser.error("Incorrect number of arguments")
	
	cmdoptions  = []
	if options.max_dist:
		if int(options.max_dist) < 0 :
			parser.error("The conf value " + options.conf + " is out or range, should greater than 0, recommend to be 1/10 of the length of the primer")
		cmdoptions.append(options.max_dist)
	
	print "cmdoption %s \n" %(cmdoptions)
	
	primer = args[0]
	if os.path.exists(args[0]):	
		primer = os.path.abspath(args[0])	
	if not os.path.exists(args[1]):			
		parser.error("Reference seq file does not exists: " + args[1]);	

	probematch(primer, cmdoptions, os.path.abspath(args[1]))
	
if __name__ == "__main__":
	main(sys.argv[1:])
