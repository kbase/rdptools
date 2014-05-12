#!/usr/bin/python
from Bio import SeqIO
import sys
import ctypes
import subprocess
import os
from optparse import OptionParser

def classifySeqs(seqfile, cmdoptions):
	#Putting fasta file into a dictionary of lists
	input_seqs = []
	results = []
	for seq in SeqIO.parse(seqfile, "fasta"):		
		Sequence = {'seqid': seq.description, 'bases': str(seq.seq)}
	input_seqs.append(Sequence)
	
	#calling the classify service, and storing the return in results
	#sys.path.append("/Users/wangqion/Desktop/KBase/workshop2014/deployment/lib")
	from biokbase.RDPTools.client import RDPTools
	service = RDPTools()
	results, hierResults = service.classifySeqs(input_seqs, cmdoptions)

	for k in results:
		print k
	print "Hierarchy results"
	for k in hierResults:
		print k

def classifyFiles(seqfile, cmdoptions):
	#calling the classify service, and storing the return in results
	#sys.path.append("/Users/wangqion/Desktop/KBase/workshop2014/deployment/lib")
	from biokbase.RDPTools.client import RDPTools
	service = RDPTools()
	results = service.classify(seqfile, cmdoptions)

	for k in results:
		print k	
				
			
def main(args):
	usage="usage: %prog [options] sequence_file(s)"
	available_genes = ["16srrna", "fungallsu"]
	available_formats = ["allrank", "fixrank", "filterbyconf", "db"]
	
	parser = OptionParser(usage=usage)
	parser.add_option("-c", "--conf", dest="conf", help="assignment confidence cutoff used to determine the assignment count for each taxon. Range [0-1]", default="0.8")
	parser.add_option("-f", "--format", dest="format", help="tab-delimited output format: " + ", ".join(available_formats), default=available_formats[0])
	parser.add_option("-g", "--gene", dest="gene", help= ', '.join(available_genes), default=available_genes[0])	

	(options, args) = parser.parse_args()
	if len(args) < 1 :
		parser.error("Incorrect number of arguments")
	
	cmdoptions  = []
	if options.conf:
		if float(options.conf) < 0 or float(options.conf) > 1:
			parser.error("The conf value " + options.conf + " is out or range, should be within [0 to 1]")
		cmdoptions.append("-c")
		cmdoptions.append(options.conf)
	if options.format:
		if options.format not in available_formats :
			parser.error("The format " + options.format + " is not available. Choices: " + ", ".join(available_formats))
		cmdoptions.append("-f")
		cmdoptions.append(options.format)
	if options.gene:
		if options.gene not in available_genes :
			parser.error("The gene " + options.gene + " is not available. Choices: " + ", ".join(available_genes))
		cmdoptions.append("-g")
		cmdoptions.append(options.gene)
	
	print "cmdoption %s \n" %(cmdoptions)
	
	for seqfile in args:
		classifySeqs(seqfile, cmdoptions)
		
	inputfiles = []
	#for seqfile in args:
	#	if os.path.exists(seqfile):
	#		inputfiles.append(os.path.abspath(seqfile))
	#	else:
	#		parser.error("Input seq file does not exists: " + seqfile);	

	#classifyFiles(inputfiles, cmdoptions)
	
if __name__ == "__main__":
	main(sys.argv[1:])
