/*
   This module provides methods for the classifying and matching
   of DNA sequences.
*/
module RDPTools {

     /*
        A structure of representing DNA sequences.
        
        string seqid
        
        This parameter is the sequence ID.  The format is an 'S'
        followed by 9 numbers.
        
        string bases
        
        This parameter represents the bases in the sequence.  Possible
        values are any combination of 'A', 'C', 'T', 'G' or their 
        lowercase equivalents.
     */
     typedef structure {
          string seqid;
          string bases;
     } Sequence;

     typedef structure {
          float conf;
          string format;
          string gene;
     } CmdOptions;

     /*
        A structure for returning the results of SequenceMatch.
        
        string seqid
        
        This parameter is the sequence ID of the query sequence.  
        The format is an 'S' followed by 9 numbers.
        
        string matchSeq
        
        This parameter is the ID of the matching reference sequence.
        It consists of a 8 alphanumeric characters followed by a '|'
        and the sequence ID, which has the format given for seqID.
        
        string orientation
        
        float S_ab
        
        This parameter is the ratio of the number of oligomers in 
        shared by the query sequence and the reference sequence and
        the total number of oligomers in the smaller sequence.
        
        int uniqueOligomers
        
        This parameter is the number of oligomers in the smaller 
        sequence.
     */
     typedef structure{
          string seqid;
          string matchSeq;
          string orientation;
          float S_ab;
          int uniqueOligomers;
     } SeqMatchResult;
	
	typedef structure{	
		string seqid;
		string lineage;
	} ClassifierResult;
	
	typedef structure{	
		string seqid;
		string desc;
		int primerNo;
		int position;
		int mismatches;
		string seqPrimerRegion;
	} ProbeMatchResult;

    /* Handle type taken from the handle service spec. */
  
    typedef structure {
            string file_name;
            string id;
            string type;
            string url;
            string remote_md5;
            string remote_sha1;
    } Handle;


     /*
	calling Classifier
	*/
	funcdef classifySeqs(list<Sequence> seqs, list<string> options) returns (list<ClassifierResult> results, list<string> hierResults);
	funcdef classify(list<Handle> files, list<string> options) returns (Handle detailedResults, Handle hierResults);
	
	funcdef classify_submit(list<Handle> files, list<string> options) returns (string jobId);
	funcdef classify_check(string jobId) returns (string status, Handle detailedResults, Handle hierResults);
	
	/*
	calling ProbeMatch with the default reference file or without reference file
	*/
	funcdef probematchSeqs(string primers, list<string> options) returns (list<ProbeMatchResult> results);
	funcdef probematch(string primers, list<string> options, string refFile) returns (list<ProbeMatchResult> results);

    /*
       Takes as input a list of options (namely, the k nearest neighbors
       and the minimum sab score), the file containing reference sequences,
       and the file containing query sequences.  It returns a list of k
       results per query sequence with the matching sequences.
    */
    funcdef seqmatch(list<string> options, string refFile, string queryFile) returns (list<SeqMatchResult> results);
};
