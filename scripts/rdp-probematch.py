import sys
import os
import subprocess
import json
import time
import urllib2

from tempfile import mktemp
from optparse import OptionParser
from biokbase.RDPTools.client import RDPTools

"""Run synchronously on the server-side machine

params:
   handle_files - input file names 
                  (files formatted as Shock file handles)
                  Note: must have primers file handle first,
                  followed by sequence file handle
   cmdoptions - command line options

returns:
   file handle containing SequenceMatch results 
"""
def probematch_sync(handle_files, cmdoptions):
    service = RDPTools()
    return service.probematch(handle_files[0], cmdoptions, handle_files[1])

"""Run asynchronously using AWE

params:
   same as for probematch_sync()

returns:
   same as for probematch_sync()
"""
def probematch_async(handle_files, cmdoptions):
    service = RDPTools()
    try:
        jobid = service.probematch_submit(
                    handle_files[0], cmdoptions, handle_files[1])
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

usage = ("USAGE: rdp-probematch [options] <primer_list | primer_file> + " 
         "seq_file\nIf multiple primers are used, " +
         "you can either save the primers in a file with " + 
         "one primer per line,\nor enter the primers as command-line " + 
         "argument, separated by ',' without space")

parser = OptionParser(usage=usage)
parser.add_option(
   "-n", "--max_dist", dest="max_dist", 
   help="maximum number of differences allowed",
   default="0")
parser.add_option(
    "--sync", action="store_true", dest="sync", 
    help="run synchronously",
    default=False)
parser.add_option(
    "-i", "--input", dest="input",
    help="read input from file (otherwise reads from STDIN)",
    default=None)
parser.add_option(
    "-p", "--primers", dest="primers",
    help="primer file (must be provided)")
parser.add_option(
    "-o", "--output", dest="output",
    help="save output to file (if not specified, prints to STDOUT)",
    default=None)
parser.add_option(
    "-u", "--upload", action="store_true", dest="upload",
    help="upload input files to Shock",
    default=False)

(options, args) = parser.parse_args()

# assemble the arguments to pas to the service
cmdoptions  = []
if options.max_dist:
    if int(options.max_dist) < 0 :
        parser.error("The conf value " + options.conf + 
                     " is out of range, should be greater than 0, " +
                     "recommended to be 1/10 of the length of the primer")
    cmdoptions.append("-n")
    cmdoptions.append(options.max_dist)

# whether to delete input files when done
# true when files created from stdin
cleanup_in = False
file_list = [options.primers]

if not options.input:
    # if there is nothing in stdin, print usage and exit
    if sys.stdin.isatty():
        parser.print_usage()
        sys.exit(1)
    tmp = mktemp()
    f = open(tmp, 'w')
    f.write(sys.stdin.read())
    f.close()
    file_list.append(tmp)
    cleanup_in = True
else:
    file_list.append(options.input)

# whether to delete file handles when done
# true when the input files need to be uploaded to Shock
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

# remove temp files
if cleanup_in:
    os.remove(file_list[1])
if cleanup_handles:
    os.remove(handle_list[0])
    os.remove(handle_list[1])
