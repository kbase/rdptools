#BEGIN_HEADER
import os
import RDPToolsService
import ConfigParser

CONFIG_FILE = os.environ["KB_DEPLOYMENT_CONFIG"]
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
            raise Exception(
                      "config file does not exist: " + 
                      os.path.abspath(CONFIG_FILE))

        self.this_config = ConfigParser.ConfigParser()
        self.this_config.read(CONFIG_FILE)
        #END_CONSTRUCTOR
        pass

    def classifySeqs(self, seqs, options):
        # self.ctx is set by the wsgi application class
        # return variables are: detailed_results, hier_results
        #BEGIN classifySeqs
        #END classifySeqs

        #At some point might do deeper type checking...
        if not isinstance(detailed_results, dict):
            raise ValueError('Method classifySeqs return value ' +
                             'detailed_results is not type dict as required.')
        if not isinstance(hier_results, dict):
            raise ValueError('Method classifySeqs return value ' +
                             'hier_results is not type dict as required.')
        # return the results
        return [detailed_results, hier_results]

    def classify(self, handles, options):
        # self.ctx is set by the wsgi application class
        # return variables are: detailed_results, hier_results
        #BEGIN classify

        classifier = RDPToolsService.Classifier(self.this_config, self.ctx)
        results = classifier.run_locally(options, handles)

        detailed_results = results[0]
        hier_results = results[1]

        #END classify

        #At some point might do deeper type checking...
        if not isinstance(detailed_results, dict):
            raise ValueError('Method classify return value ' +
                             'detailed_results is not type dict as required.')
        if not isinstance(hier_results, dict):
            raise ValueError('Method classify return value ' +
                             'hier_results is not type dict as required.')
        # return the results
        return [detailed_results, hier_results]

    def classify_submit(self, handles, options):
        # self.ctx is set by the wsgi application class
        # return variables are: jobid
        #BEGIN classify_submit

        classifier = RDPToolsService.Classifier(self.this_config, self.ctx)
        jobid = classifier.submit_awe(options, handles)

        #END classify_submit

        #At some point might do deeper type checking...
        if not isinstance(jobid, basestring):
            raise ValueError('Method classify_submit return value ' +
                             'jobid is not type basestring as required.')
        # return the results
        return [jobid]

    def classify_check(self, jobid):
        # self.ctx is set by the wsgi application class
        # return variables are: status, detailed_results, hier_results
        #BEGIN classify_check

        classifier = RDPToolsService.Classifier(self.this_config, self.ctx)
        status, output = classifier.check_awe(jobid)

        if len(output) > 0:
            detailed_results = output[0]
            hier_results = output[1]
        else:
            detailed_results = {}
            hier_results = {}

        #END classify_check

        #At some point might do deeper type checking...
        if not isinstance(status, basestring):
            raise ValueError('Method classify_check return value ' +
                             'status is not type basestring as required.')
        if not isinstance(detailed_results, dict):
            raise ValueError('Method classify_check return value ' +
                             'detailed_results is not type dict as required.')
        if not isinstance(hier_results, dict):
            raise ValueError('Method classify_check return value ' +
                             'hier_results is not type dict as required.')
        # return the results
        return [status, detailed_results, hier_results]

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

    def probematch(self, primers, options, ref_file):
        # self.ctx is set by the wsgi application class
        # return variables are: results
        #BEGIN probematch

        probematch = RDPToolsService.ProbeMatch(self.this_config, self.ctx)
        results = probematch.run_locally(options, [primers, ref_file])[0]

        #END probematch

        #At some point might do deeper type checking...
        if not isinstance(results, dict):
            raise ValueError('Method probematch return value ' +
                             'results is not type dict as required.')
        # return the results
        return [results]

    def probematch_submit(self, primers, options, ref_file):
        # self.ctx is set by the wsgi application class
        # return variables are: jobid
        #BEGIN probematch_submit

        probematch = RDPToolsService.ProbeMatch(
                         self.this_config, self.ctx, False)
        jobid = probematch.submit_awe(options, [primers, ref_file])

        #END probematch_submit

        #At some point might do deeper type checking...
        if not isinstance(jobid, basestring):
            raise ValueError('Method probematch_submit return value ' +
                             'jobid is not type basestring as required.')
        # return the results
        return [jobid]

    def probematch_check(self, jobid):
        # self.ctx is set by the wsgi application class
        # return variables are: status, results
        #BEGIN probematch_check

        probematch = RDPToolsService.ProbeMatch(self.this_config, self.ctx)
        status, output = probematch.check_awe(jobid)

        if len(output) > 0:
            results = output[0]
        else:
            results = {}

        #END probematch_check

        #At some point might do deeper type checking...
        if not isinstance(status, basestring):
            raise ValueError('Method probematch_check return value ' +
                             'status is not type basestring as required.')
        if not isinstance(results, dict):
            raise ValueError('Method probematch_check return value ' +
                             'results is not type dict as required.')
        # return the results
        return [status, results]

    def seqmatch(self, ref_file, query_file, options):
        # self.ctx is set by the wsgi application class
        # return variables are: result_handle
        #BEGIN seqmatch

        seqmatch = RDPToolsService.SeqMatch(self.this_config, self.ctx)
        result_handle = seqmatch.run_locally(options, [ref_file, query_file])[0]

        #END seqmatch

        #At some point might do deeper type checking...
        if not isinstance(result_handle, dict):
            raise ValueError('Method seqmatch return value ' +
                             'result_handle is not type dict as required.')
        # return the results
        return [result_handle]

    def seqmatch_submit(self, ref_file, query_file, options):
        # self.ctx is set by the wsgi application class
        # return variables are: jobid
        #BEGIN seqmatch_submit

        seqmatch = RDPToolsService.SeqMatch(self.this_config, self.ctx)
        jobid = seqmatch.submit_awe(options, [ref_file, query_file])

        #END seqmatch_submit

        #At some point might do deeper type checking...
        if not isinstance(jobid, basestring):
            raise ValueError('Method seqmatch_submit return value ' +
                             'jobid is not type basestring as required.')
        # return the results
        return [jobid]

    def seqmatch_check(self, jobid):
        # self.ctx is set by the wsgi application class
        # return variables are: status, result_handle
        #BEGIN seqmatch_check

        seqmatch = RDPToolsService.SeqMatch(self.this_config, self.ctx)
        status, output = seqmatch.check_awe(jobid)

        if len(output) > 0:
            result_handle = output[0]
        else:
            result_handle = {}

        #END seqmatch_check

        #At some point might do deeper type checking...
        if not isinstance(status, basestring):
            raise ValueError('Method seqmatch_check return value ' +
                             'status is not type basestring as required.')
        if not isinstance(result_handle, dict):
            raise ValueError('Method seqmatch_check return value ' +
                             'result_handle is not type dict as required.')
        # return the results
        return [status, result_handle]
