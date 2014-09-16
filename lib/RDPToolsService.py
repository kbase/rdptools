import os
import subprocess
import json
import urllib2
import re

from tempfile import mkstemp, mktemp

CONFIG_FILE = os.environ["KB_DEPLOYMENT_CONFIG"]
SERVICE_NAME = os.environ["KB_SERVICE_NAME"]
TEMP_DIR = "../services/RDPTools/tmp" #os.environ["SERVICE_TEMP_DIR"]

'''A template for a KBase service that can be run either "locally"
(i.e. on the KBase server, as opposed to an AWE client) or on an
AWE client

This is an "abstract" class template that is meant to be inherited
from.

Subclasses must define the following functions:
    _run_locally_internal()
    _get_workflow()
    _get_awe_output()
See below on specific documentation on how to use them.
'''
class Service:

    def __init__(self, config, ctx, cleanup=True):
        self.config = config
        self.ctx = ctx
        # whether to delete temp files
        # set to False for debugging
        self.cleanup = cleanup

    def run_locally(self, options, handle_files):
        temp_files = []
        for name in handle_files:
            tmp = mktemp(suffix='', dir=TEMP_DIR)
            args = ["kbhs-download", "--handle", name, "-o", tmp]
            subprocess.check_call(args)
            temp_files.append(tmp)

        result_files = list(self._run_locally_internal(options, temp_files))

        if self.cleanup:
            for name in temp_files:
                os.remove(name)

        handles = []
        for name in result_files:
            tmp = mktemp(suffix='.handle', dir=TEMP_DIR)
            args = ["kbhs-upload", "-i", name, "-o", tmp]
            subprocess.check_call(args)
            fh = open(tmp)
            h = json.load(fh)
            fh.close()
            handles.append(h)
            if self.cleanup:
                os.remove(tmp)
                os.remove(name)

        return handles

    '''Performs algorithm or calls external program to perform algorithm.

    params:
        options - command line options passed to the algorithm
        file_list - list of file names

    returns:
        list of result file names
    '''
    def _run_locally_internal(self, options, file_list):
        pass

    def submit_awe(self, options, handle_files):
        workflow = self._get_workflow(options, handle_files)

        awe_server = self.config.get(SERVICE_NAME, "awe-server")
        args = ["awe_submit", "-awe", awe_server, "-script", workflow]

        job_file = mktemp(suffix=".job", dir=TEMP_DIR)
        jf = open(job_file, 'w')
        subprocess.check_call(args, stdout=jf)
        jf.close()

        jf = open(job_file)
        jobid = ''
        for line in jf:
            m = re.search("id=([a-z0-9A-Z-]+)", line)
            if m:
                jobid = m.group(1)
        jf.close()

        if self.cleanup:
            os.remove(workflow)
            os.remove(job_file)

        if jobid == '':
            raise RuntimeError("Failed to upload job to AWE")

        return jobid

    '''Provides workflow document for use by AWE
    
    params:
        options - command line options
        handle_files - names of handle files

    returns:
        workflow document name
    '''
    def _get_workflow(self, options, handle_files):
        pass

    def check_awe(self, jobid):
        awe_server = self.config.get(SERVICE_NAME, "awe-server")
        url = "http://" + awe_server + "/job/" + jobid

        resp = urllib2.urlopen(url)
        txt = resp.read()
        obj = json.loads(txt)

        status = obj["data"]["state"]

        output_handles = []

        if status == "completed":
            output = self._get_awe_output(obj)

            if type(output) == list:
                for task in output:
                    node = task["node"]
                    host = task["host"]
                    handle = self.download_handle(host, node)
                    output_handles.append(handle)
            elif type(output) == dict:
                node = output["node"]
                host = output["host"]
                handle = self.download_handle(host, node)
                output_handles.append(handle)
            else:
                raise TypeError("_get_awe_output returns invalid type")

        return status, output_handles

    '''Returns file handles to results of workflow run by AWE

    params:
        obj - dictionary derived retrieved from JSON-formatted url
    
    returns:
       file handles as dictionaries (NOT as files or file names) 
    '''
    def _get_awe_output(self, obj):
        pass

    def download_handle(self, host, node):
        url = host + "/node/" + node

        resp = urllib2.urlopen(url)
        txt = resp.read()
        obj = json.loads(txt)

        handle = {}
        handle["remote_md5"] = obj["data"]["file"]["checksum"]["md5"]
        handle["file_name"] = obj["data"]["file"]["name"]
        handle["url"] = host
        if "sha1" in obj["data"]["file"]["checksum"]:
            handle["remote_sha1"] = obj["data"]["file"]["checksum"]["sha1"]
        else:
            handle["remote_sha1"] = None
        handle["id"] = node
        handle["type"] = "shock"

        return handle

class Classifier(Service):

    def _run_locally_internal(self, options, file_list):
        hier_out = mktemp(suffix=".hier", dir=TEMP_DIR)
        class_out = mktemp(suffix=".classified", dir=TEMP_DIR)

        args = ["java", self.config.get(SERVICE_NAME, "classifier-memory"), 
                "-jar"]
        args.append("classifier.jar")
        args.append(self.config.get(SERVICE_NAME, "classifier-subcommand"))
        args.extend(options)
        args.extend(["-o", class_out, "-h", hier_out])
        args.extend(file_list)
       
        subprocess.check_call(args)

        return hier_out, class_out

    def _get_workflow(self, options, file_list):
        workflow = mktemp(suffix=".workflow", dir=TEMP_DIR)
        
        args = ["rdp-expand-classifier", "--output", workflow]
        if self.ctx["token"] is not None:
            args.extend(["--token", self.ctx["token"]])
        args.extend(options)
        args.extend(file_list)

        subprocess.check_call(args)

        return workflow

    def _get_awe_output(self, obj):
        num_tasks = len(obj["data"]["tasks"])
        classified_output = obj['data']['tasks'][num_tasks-2]['outputs']['rdp-classify.classified']
        hier_output = obj['data']['tasks'][num_tasks-1]['outputs']['rdp-classify.hier']

        return classified_output, hier_output

class ProbeMatch(Service):

    def _run_locally_internal(self, options, file_list):
        out = mktemp(suffix=".probematch", dir=TEMP_DIR)

        args = ["java", self.config.get(SERVICE_NAME, "probematch-memory"), 
                "-jar"]
        args.append("ProbeMatch.jar")
        args.extend(options)
        args.extend(["-o", out])
        args.extend(file_list)

        print args
        subprocess.check_call(args)

        return out

    def _get_workflow(self, options, file_list):
        workflow = mktemp(suffix=".workflow", dir=TEMP_DIR)

        args = ["rdp-expand-probematch", "--output", workflow]
        if self.ctx["token"] is not None:
            args.extend(["--token", self.ctx["token"]])
        args.extend(options)
        args.extend(file_list)

        subprocess.check_call(args)

        return workflow

    def _get_awe_output(self, obj):
        return obj["data"]["tasks"][0]["outputs"]["rdp-probematch.txt"]

class SeqMatch(Service):

    def _run_locally_internal(self, options, file_list):
        out = mktemp(suffix=".seqmatch", dir=TEMP_DIR)
    
        args = ["java", self.config.get(SERVICE_NAME, "seqmatch-memory"), 
                "-jar"]
        args.append("SequenceMatch.jar")
        args.append("seqmatch")
        args.extend(["-o", out])
        args.extend(options)
        args.extend(file_list)

        subprocess.check_call(args)

        return out

    def _get_workflow(self, options, file_list):
        workflow = mktemp(suffix=".workflow", dir=TEMP_DIR)

        args = ["rdp-expand-seqmatch", "--output", workflow]
        if self.ctx["token"] is not None:
            args.extend(["--token", self.ctx["token"]])
        args.extend(options)
        args.extend(file_list)

        subprocess.check_call(args)

        return workflow

    def _get_awe_output(self, obj):
        return obj["data"]["tasks"][0]["outputs"]["rdp-seqmatch.txt"]
