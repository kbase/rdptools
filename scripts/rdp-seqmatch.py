import sys
import os
import subprocess
import json
import time
import urllib2

from tempfile import mktemp
from optparse import OptionParser
from biokbase.RDPTools.client import RDPTools

def seqmatch_sync(handle_files, cmdoptions):
    service = RDPTools()
    return service.seqmatch(handle_files[0], handle_files[1], cmdoptions)

def seqmatch_async(handle_files, cmdoptions):
    service = RDPTools()
    try:
        jobid = service.seqmatch_submit(handle_files[0], handle_files[1], cmdoptions)
    except urllib2.URLError:
        raise SystemExit("Failed to connect to KBase server")
    except RuntimeError:
        raise SystemExit("Failed to upload job to AWE server")

    print "Got jobID", jobid

    while True:
        status, result_handle = service.seqmatch_check(jobid)
        print "status =", status
        if status == "completed":
            return result_handle
        elif status == "suspend":
            print "Failed to execute job"
            return None
        time.sleep(1)

args = sys.argv[1:]

usage = "USAGE: seqmatch [options] reference_file query_file"

parser = OptionParser(usage=usage)
parser.add_option("-k", "--knn", dest="k",
                  help="Find k nearest neighbors (default=20)",
                  default="20")
parser.add_option("-s","--sab", dest="sab",
                  help="Minimum sab score (default=0.5)",
                  default="0.5")
parser.add_option("--sync", action="store_true", dest="sync", 
                  help="run synchronously", 
                  default=False)
parser.add_option("-i", "--input", dest="input", 
                  help="read input from file (otherwise reads from STDIN)",
                  default=None)
parser.add_option("-r", "--ref", dest="reference",
                  help="reference file (must be provided)")
parser.add_option("-o", "--output", dest="output",
                  help="save output to file (if not specified, prints to STDOUT)",
                  default=None)
parser.add_option("-u", "--upload", action="store_true", dest="upload",
                  help="upload input files to Shock",
                  default=False)

(options, args) = parser.parse_args()

cmdoptions  = []
if options.k:
    cmdoptions.append("-k")
    cmdoptions.append(options.k)
if options.sab:
     cmdoptions.append("-s")
     cmdoptions.append(options.sab)

cleanup_in = False
file_list = [options.reference]

if not options.input:
    tmp = mktemp()
    f = open(tmp, 'w')
    f.write(sys.stdin.read())
    f.close()
    file_list.append(tmp)
    cleanup_in = True
else:
    file_list.append(options.input)

cleanup_handles = options.upload
handle_files = []
for file_name in file_list:
    if os.path.exists(file_name):
        if options.upload:
            handle_name = '.'.join([file_name, "handle"])
            upload_args = ["kbhs-upload", "-i", file_name, "-o", handle_name]
            subprocess.check_call(upload_args)
        else:
            handle_name = file_name
        handle_files.append(os.path.abspath(handle_name))
    else:
        parser.error("Input file handle does not exist: " + handle_name)

if options.sync:
    result_handle = seqmatch_sync(handle_files, cmdoptions)
else:
    result_handle = seqmatch_async(handle_files, cmdoptions)

if result_handle is not None:
    if options.output:
        fh = open(options.output, 'w')
        json.dump(result_handle, fh)
        fh.close()
    else:
        print json.dumps(result_handle)

if cleanup_in:
    os.remove(file_list[1])
if cleanup_handles:
    for handle_name in handle_files:
        os.remove(handle_files)
