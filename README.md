RDPTools Services
===================

Overview
----------

Tools for the classification and matching of dna/protein sequences.

Deploying RDPTools on KBase
----------
First deploy typecomp and make sure compile_typespec is in the
system path.

From the top level of the development container, run the command
    perl auto-deploy -module rdptools <config file>
where <config file> will usually be bootstrap.cfg.

Starting/Stopping the service
----------
This service utilizes port 7109.  Use the start_service script in the
'scripts' folder to start the service.  Use the stop_service script in
the same folder to stop the service.
