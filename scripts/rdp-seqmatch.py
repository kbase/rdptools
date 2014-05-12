#!/usr/bin/python

from Bio import SeqIO
import sys
import ctypes
import subprocess
import os
from optparse import OptionParser

PORT = 10004

def seqmatch(cmdoptions, refFile, queryFile):
    sys.path.append("/Users/wangqion/Desktop/KBase/workshop2014/deployment/lib")
    from RDPToolsClient import RDPTools
    service = RDPTools("http://localhost:"+str(PORT))
    results = service.seqmatch(cmdoptions, refFile, queryFile)
     
    for k in results:
        print k[:-1]
          
def main(args):
    usage = "usage: seqmatch [options] reference_file query_file"
     
    parser = OptionParser(usage=usage)
    parser.add_option("-k", "--knn", dest="k", 
                      help="Find k nearest neighbors (default=20)",
                      default="20")
    parser.add_option("-s","--sab", dest="sab",
                      help="Minimum sab score (default=0.5)",
                      default="0.5")
    (options, args) = parser.parse_args()
    if len(args) < 2:
         parser.error("Incorrect number of arguments")
         
    cmdoptions = []
    if options.k:
         cmdoptions.append("-k")
         cmdoptions.append(options.k)
    if options.sab:
         cmdoptions.append("-s")
         cmdoptions.append(options.sab)
     
    inputFiles = []
    for file in args:
         if os.path.exists(file):
              inputFiles.append(os.path.abspath(file))
         else:
              parser.error("Input file does not exist: " + file)
     
    seqmatch(cmdoptions, inputFiles[0], inputFiles[1])
     
if __name__ == "__main__":
    main(sys.argv[1:])