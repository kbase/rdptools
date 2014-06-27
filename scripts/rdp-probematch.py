import sys
import os
import subprocess
import json
import time
import urllib2

from tempfile import mktemp
from optparse import OptionParser
from biokbase.RDPTools.client import RDPTools

def probematch_sync(handle_files, cmdoptions):
    service = RDPTools()
    return service.probematch(handle_files[0], cmdoptions, handle_files[1])

def probematch_async(handle_files, cmdoptions):
    service = RDPTools()
    try:
        jobid = service.probematch_submit(handle_files[0], cmdoptions, handle_files[1])
    except urllib2.URLError:
        raise SystemExit("Failed to connect to KBase server")
    except subprocess.CalledProcessError, args:
        raise SystemExit("Failed to execute command: " + ' '.join(args))
    except RuntimeError:
        raise SystemExit("Failed to upload job to AWE")

    print "Got jobID", jobid

    while True:
        status, result_handle = service.probematch_check(jobid)
        print "status =", status
        if status == "completed":
            return result_handle
        elif status == "suspend":
            print "Failed to execute job"
            return None
        time.sleep(1)

args = sys.argv[1:]

usage = ("USAGE: %prog [options] <primer_list | primer_file> seq_file\n" + 
         "If multiple primers are used, you can either save the primers in a file with one primer per line,\n" +
         "or enter the primers as command-line argument, separated by ',' without space" )

parser = OptionParser(usage=usage)
parser.add_option("-n", "--max_dist", dest="max_dist", 
                  help="maximum number of differences allowed",
                  default="0")
parser.add_option("--sync", action="store_true", dest="sync", 
                  help="run synchronously",
                  default=False)
parser.add_option("-i", "--input", dest="input",
                  help="read input from file (otherwise reads from STDIN)",
                  default=None)
parser.add_option("-p", "--primers", dest="primers",
                  help="primer file (must be provided)")
parser.add_option("-o", "--output", dest="output",
                  help="save output to file (if not specified, prints to STDOUT)",
                  default=None)
parser.add_option("-u", "--upload", action="store_true", dest="upload",
                  help="upload input files to Shock",
                  default=False)

(options, args) = parser.parse_args()

cmdoptions  = []
if options.max_dist:
    if int(options.max_dist) < 0 :
        parser.error("The conf value " + options.conf + " is out of range," +
                     " should be greater than 0, recommended to be 1/10 of the length of the primer")
    cmdoptions.append("-n")
    cmdoptions.append(options.max_dist)

cleanup_in = False
file_list = [options.primers]

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
    result_handle = probematch_sync(handle_files, cmdoptions)
else:
    result_handle = probematch_async(handle_files, cmdoptions)

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
    os.remove(handle_list[0])
    os.remove(handle_list[1])
