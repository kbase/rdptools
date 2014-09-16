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
   cmdoptions - command line options

returns:
    two (2) file handle, one for the hierarchical file and 
    one for the classified file
"""
def classifier_sync(handle_files, cmdoptions):
    service = RDPTools()
    return service.classify(handle_files, cmdoptions)

"""Run asynchronously using AWE

params:
   same as for classifier_sync()

returns:
   same as for classifier_sync()
"""
def classifier_async(handle_files, cmdoptions):
    service = RDPTools()
    try:
        jobid = service.classify_submit(handle_files, cmdoptions)
    except urllib2.URLError:
        raise SystemExit("Failed to connect to KBase server")
    except RuntimeError:
        raise SystemExit("Failed to upload job to AWE")

    print "Got jobID", jobid

    while True:
        status, detail_handle, hier_handle = service.classify_check(jobid)
        print "status =", status
        if status == "completed":
            return detail_handle, hier_handle
        elif status == "suspend":
            print "Failed to execute job"
            return None, None
        time.sleep(1)

usage = "USAGE: rdp-classifier [options] sequence_file(s)"
available_genes = ["16srrna", "fungallsu"]
available_formats = ["allrank", "fixrank", "filterbyconf", "db"]

parser = OptionParser(usage=usage)
parser.add_option(
    "-c", "--conf", dest="conf", 
    help="assignment confidence cutoff used to determine " +
    "the assignment count for each taxon. Range [0-1]", 
    default="0.8")
parser.add_option(
    "-f", "--format", dest="format", 
    help="tab-delimited output format: " + ", ".join(available_formats), 
    default=available_formats[0])
parser.add_option(
    "-g", "--gene", dest="gene", 
    help= ', '.join(available_genes), 
    default=available_genes[0])
parser.add_option(
    "-s", "--seq", action="store_true", dest="seq", 
    help="input a sequence instead of a file", 
    default=False)
parser.add_option(
    "--sync", action="store_true", dest="sync",
    help="run synchronously",
    default=False)
parser.add_option(
    "-i", "--input", dest="input",
    help="read input from files, comma separated (otherwise reads from STDIN)",
    default=False)
parser.add_option(
    "-o", "--output", dest="output",
    help="save output to file (if not specified, prints to STDOUT)",
    default=None)
parser.add_option(
    "-u", "--upload", action="store_true", dest="upload",
    help="upload input file to Shock",
    default=False)

(options, args) = parser.parse_args()

# assemble the arguments to pass to the service
cmdoptions  = []
if options.conf:
    if float(options.conf) < 0 or float(options.conf) > 1:
        parser.error(
            "The conf value " + options.conf + " is out or range, "+
            "should be within [0 to 1]")
    cmdoptions.append("-c")
    cmdoptions.append(options.conf)
if options.format:
    if options.format not in available_formats :
        parser.error(
            "The format " + options.format + " is not available. " + 
            "Choices: " + ", ".join(available_formats))
    cmdoptions.append("-f")
    cmdoptions.append(options.format)
if options.gene:
    if options.gene not in available_genes :
        parser.error(
            "The gene " + options.gene + " is not available. " + 
            "Choices: " + ", ".join(available_genes))
    cmdoptions.append("-g")
    cmdoptions.append(options.gene)

# whether to delete input files when done
# true when files created from stdin
cleanup_in = False
file_list = []

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
    file_list.extend(options.input.split(','))

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
    detail_handle, hier_handle = classifier_sync(handle_files, cmdoptions)
else:
    detail_handle, hier_handle = classifier_async(handle_files, cmdoptions)

# if the service produced a result
if detail_handle is not None:
    if options.output:
        handle_names = options.output.split(':')
        fdetail = open(handle_names[0], 'w')
        json.dump(detail_handle, fdetail)
        fdetail.close()
        fhier = open(handle_names[1], 'w')
        json.dump(hier_handle, fhier)
        fhier.close()
    else:
        print json.dumps(detail_handle)

# delete temp files
if cleanup_in:
    for name in file_list:
        os.remove(name)
if cleanup_handles:
    for name in handle_files:
        os.remove(name)
