#BEGIN_HEADER

from Bio import SeqIO
import sys
import ctypes
import os, subprocess
import os.path
import ConfigParser
from tempfile import mkstemp, mktemp
import json
import re
import urllib2

CONFIG_FILE = os.environ["KB_DEPLOYMENT_CONFIG"]
SERVICE_NAME = os.environ["KB_SERVICE_NAME"]

#CONFIG_FILE = "../services/RDPTools/conf/rdp-config.ini"
TEMP_DIR = "../services/RDPTools/tmp"

if os.environ.has_key("TEMPDIR"):
    TEMP_DIR = os.environ["TEMPDIR"]

#END_HEADER


class RDPTools:
    '''
    Module Name:
    RDPTools

    Module Description:
    This module provides methods for the classifying and matching
of DNA sequences.
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
	if not os.path.exists(os.path.abspath(CONFIG_FILE)):
			raise Exception("config file does not exist: " + os.path.abspath(CONFIG_FILE))

	self.this_config = ConfigParser.ConfigParser()
	self.this_config.read(CONFIG_FILE)	
        #END_CONSTRUCTOR
        pass

    def classifySeqs(self, seqs, options):
        # self.ctx is set by the wsgi application class
        # return variables are: results, hierResults
        #BEGIN classifySeqs
        #making a temp file to be run in classifier
        fd, tempFile = mkstemp(suffix='.fasta', dir=TEMP_DIR)	
        infile = os.fdopen(fd, "w+")
        for seq in seqs:
            seqId = seq['seqid']
            seqBases = seq['bases']
            infile.write(">"+seqId + "\n" + seqBases+ "\n")
        infile.close()
		
        tempClassifierOut = tempFile + "_classified.txt"
        tempHierOut = tempFile + "_hier.txt"
        #calling classifier tool
        args = ['java', self.this_config.get(SERVICE_NAME, "classifier_memory"), '-jar']
        args.append("classifier.jar")
        args.append(self.this_config.get(SERVICE_NAME, "classifier_subcommand"))
        args.extend(options)
        args.extend(['-o', tempClassifierOut, '-h', tempHierOut, tempFile])
        print "args %s \n" %(args)
        subprocess.check_call(args)
		
        os.remove(tempFile)
        
        #Putting Results in a list to be sent back
        results = []
        result_file = open(tempClassifierOut, "r")
        for line in result_file:
			results.append( line)  # this does not work because the client treat it as string
	
        hierResults = []
        result_file = open(tempHierOut, "r")
        for line in result_file:
			hierResults.append( line)  # this does not work because the client treat it as string
	
        
        
        #END classifySeqs

        #At some point might do deeper type checking...
        if not isinstance(results, list):
            raise ValueError('Method classifySeqs return value ' +
                             'results is not type list as required.')
        if not isinstance(hierResults, list):
            raise ValueError('Method classifySeqs return value ' +
                             'hierResults is not type list as required.')
        # return the results
        return [results, hierResults]

    def classify(self, files, options):
        # self.ctx is set by the wsgi application class
        # return variables are: detailedResults, hierResults
        #BEGIN classify
        fd, tempFile = mkstemp(suffix='', dir=TEMP_DIR)
        tempClassifierOut = tempFile + "_classified.txt"
        tempHierOut = tempFile + "_hier.txt"

	#
	# For each handle in our input files list, use kbhs-download
	# to download the associated file. We need a tempfile
	# to write the handle to (that we can reuse) and a tempfile
	# to write each downloaded to.
	#

	tempFiles = []
	handleTemp = mktemp(suffix='', dir=TEMP_DIR)
	for h in files:
		fh = file(handleTemp, "w")
		json.dump(h, fh)
		fh.close()
		fileTemp = mktemp(suffix='', dir=TEMP_DIR)
		tempFiles.append(fileTemp)
		args = ["kbhs-download", "--handle", handleTemp, "-o", fileTemp]
		print args
		subprocess.check_call(args)

        #calling classifier tool
        args = ['java', self.this_config.get(SERVICE_NAME, "classifier_memory"), '-jar']
        args.append("classifier.jar")
        args.append(self.this_config.get(SERVICE_NAME, "classifier_subcommand"))
        args.extend(options)
        args.extend(['-o', tempClassifierOut, '-h', tempHierOut])
        args.extend(tempFiles)
        print "args %s \n" %(args)
        subprocess.check_call(args)

        os.remove(tempFile)


	#
	# Upload each of our result files, and return their handles.
	#

	args = ['kbhs-upload', '-i', tempClassifierOut, '-o', handleTemp]
	print args
	subprocess.check_call(args)
	fh = file(handleTemp)
	detailedResults = json.load(fh)
	fh.close()
	args = ['kbhs-upload', '-i', tempHierOut, '-o', handleTemp]
	print args
	subprocess.check_call(args)
	fh = file(handleTemp)
	hierResults = json.load(fh)
	fh.close()
	
		#Putting Results in a list to be sent back
        #results = []
        #result_file = open(tempClassifierOut, "r")
        #for line in result_file:
            ##TypeError: <kbase_rdptools_serviceImpl.ClassifierResult instance at 0x2261670> is not JSON serializable
            ##results.append( ClassifierResult(line))
            #results.append( line)
			
        #END classify

        #At some point might do deeper type checking...
        if not isinstance(detailedResults, dict):
            raise ValueError('Method classify return value ' +
                             'detailedResults is not type dict as required.')
        if not isinstance(hierResults, dict):
            raise ValueError('Method classify return value ' +
                             'hierResults is not type dict as required.')
        # return the results
        return [detailedResults, hierResults]

    def classify_submit(self, files, options):
        # self.ctx is set by the wsgi application class
        # return variables are: jobId
        #BEGIN classify_submit

	handleTemp = mktemp(suffix='', dir=TEMP_DIR)

        workflowTemp = mktemp(suffix='', dir=TEMP_DIR)

        fh = file(handleTemp, "w")
        json.dump(files, fh)
        fh.close()

        args = ["rdp-expand-template", "--list", "--output", workflowTemp]
        args.extend(options)
        args.append(handleTemp)

        print args
        subprocess.check_call(args)
        
        awe_server = self.this_config.get(SERVICE_NAME, "awe_server")
        args = ["awe_submit", "-awe", awe_server, "-script", workflowTemp]

        os.remove(handleTemp)

        jobTemp = mktemp(suffix='', dir=TEMP_DIR)
        jt = file(jobTemp, "w")
        subprocess.check_call(args, stdout=jt)
        jt.close()
        jt = file(jobTemp)
        
        # Look for this:
        # submitting job script to AWE...Done! id=2c9d83d3-4f3e-429a-950d-31bc57bafa5f

        jobId = ''
        for l in jt:
            print l
            m = re.search('id=([a-z0-9A-Z-]+)', l)
            if m:
                jobId = m.group(1)
        jt.close()        
                
        #END classify_submit

        #At some point might do deeper type checking...
        if not isinstance(jobId, basestring):
            raise ValueError('Method classify_submit return value ' +
                             'jobId is not type basestring as required.')
        # return the results
        return [jobId]

    def classify_check(self, jobId):
        # self.ctx is set by the wsgi application class
        # return variables are: status, detailedResults, hierResults
        #BEGIN classify_check
        
        #
        # Check the job status by hitting the AWE server using 
        # the host/port from our configuration and the jobid
        # passed in our parameter list.
        #

        awe_server = self.this_config.get(SERVICE_NAME, "awe_server")
        url = "http://" +  awe_server + "/job/" + jobId

        resp = urllib2.urlopen(url)
        txt = resp.read()
        obj = json.loads(txt)

        status = obj['data']['state']

        detailedResults = {}
        hierResults = {}

        if status == 'completed':
            classified_output = obj['data']['tasks'][0]['outputs']['rdp-classify.classified']
            hier_output = obj['data']['tasks'][0]['outputs']['rdp-classify.hierarchical']
            
            detailedResults['file_name'] = "rdp-classify.classified"
            detailedResults['id'] = classified_output['node']
            detailedResults['type'] = 'shock'
            detailedResults['url'] = classified_output['host']

            hierResults['file_name'] = "rdp-classify.hierarchical"
            hierResults['id'] = hier_output['node']
            hierResults['type'] = 'shock'
            hierResults['url'] = hier_output['host']

        #END classify_check

        #At some point might do deeper type checking...
        if not isinstance(status, basestring):
            raise ValueError('Method classify_check return value ' +
                             'status is not type basestring as required.')
        if not isinstance(detailedResults, dict):
            raise ValueError('Method classify_check return value ' +
                             'detailedResults is not type dict as required.')
        if not isinstance(hierResults, dict):
            raise ValueError('Method classify_check return value ' +
                             'hierResults is not type dict as required.')
        # return the results
        return [status, detailedResults, hierResults]

    def probematchSeqs(self, primers, options):
        # self.ctx is set by the wsgi application class
        # return variables are: results
        #BEGIN probematchSeqs
        #END probematchSeqs

        #At some point might do deeper type checking...
        if not isinstance(results, list):
            raise ValueError('Method probematchSeqs return value ' +
                             'results is not type list as required.')
        # return the results
        return [results]

    def probematch(self, primers, options, refFile):
        # self.ctx is set by the wsgi application class
        # return variables are: results
        #BEGIN probematch
        fd, tempFile = mkstemp(suffix='', dir=TEMP_DIR)
        tempProbeMatchOut = tempFile + "_probematch.txt"
        args = ['java', self.this_config.get("probematch", "probematch_memory"), '-jar']
        args.append("ProbeMatch.jar")
        args.extend([primers, refFile])
        args.extend(options)
		
        print "args %s, output %s\n" %(args, tempProbeMatchOut)
        tempProbeMatchOutStream = open(tempProbeMatchOut, "w")
        subprocess.check_call(args, stdout=tempProbeMatchOutStream)
        os.remove(tempFile)
        tempProbeMatchOutStream.close()
        
        #Putting Results in a list to be sent back
        results = []
        result_file = open(tempProbeMatchOut, "r")
        for line in result_file:
            #match = ProbeMatchResult()
            print "result %s\n" %(line)
            results.append(line)

        fd, tempFile = mkstemp(suffix='', dir=TEMP_DIR)
        tempProbeMatchOut = tempFile + "_probematch.txt"
        args = ['java', self.this_config.get("probematch", "probematch_memory"), '-jar'] 
        args.append("ProbeMatch.jar") 
        args.extend([primers, refFile])
        args.extend(options)
		
        print "args %s, output %s\n" %(args, tempProbeMatchOut)
        tempProbeMatchOutStream = open(tempProbeMatchOut, "w")
        subprocess.check_call(args, stdout=tempProbeMatchOutStream)
        os.remove(tempFile)
        tempProbeMatchOutStream.close()
        
        #END probematch

        #At some point might do deeper type checking...
        if not isinstance(results, list):
            raise ValueError('Method probematch return value ' +
                             'results is not type list as required.')
        # return the results
        return [results]

    def seqmatch(self, options, refFile, queryFile):
        # self.ctx is set by the wsgi application class
        # return variables are: results
        #BEGIN seqmatch
        fd, tempfile = mkstemp(suffix='', dir=TEMP_DIR)
        tempSeqMatch = tempfile + "_seqmatch.txt"
        
        args = ["java", self.this_config.get("seqmatch", "seqmatch_memory"), "-jar"]
        args.append("SequenceMatch.jar")
        args.append("seqmatch")
        args.extend(options)
        args.append(refFile)
        args.append(queryFile)
        
        tempSeqMatchOut = open(tempSeqMatch, 'w')
        
        subprocess.check_call(args, stdout=tempSeqMatchOut)
        
        os.remove(tempfile)
        tempSeqMatchOut.close()
        
        results = []
        result_file = open(tempSeqMatch)
        for line in result_file:
            results.append(line)
            
        result_file.close()
        
        #END seqmatch

        #At some point might do deeper type checking...
        if not isinstance(results, list):
            raise ValueError('Method seqmatch return value ' +
                             'results is not type list as required.')
        # return the results
        return [results]
