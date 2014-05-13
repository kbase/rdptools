#largely copied from Makefile for assembly

TOP_DIR = ../..
TARGET ?= /kb/deployment
DEPLOY_RUNTIME ?= /kb/runtime
SERVICE = RDPTools
SERVICE_NAME = RDPTools
SERVICE_NAME_PY = $(SERVICE_NAME)
SERVICE_DIR = $(TARGET)/services/$(SERVICE)
SERVICE_PSGI_FILE = rdptools.psgi

SERVER_SPEC = $(SERVICE).spec

SERVICE_PORT = 7119

SERVICE_URL = http://localhost:$(SERVICE_PORT)
#SERVICE_URL = https://kbase.us/services/$(SERVICE)

ifdef TEMPDIR
TPAGE_TEMPDIR = --define kb_tempdir=$(TEMPDIR)
endif

TPAGE_ARGS = --define kb_top=$(TARGET) \
        --define kb_runtime=$(DEPLOY_RUNTIME) \
        --define kb_service_name=$(SERVICE) \
        --define kb_service_port=$(SERVICE_PORT) \
        $(TPAGE_TEMPDIR)

#note: requires full development container to work
#otherwise, use an alternative python wrapper
include $(TOP_DIR)/tools/Makefile.common

SRC_PYTHON = $(wildcard scripts/rdp-*.py)

#note:  no test scripts have been written;
#the below is a placeholder
SERVER_TESTS = $(wildcard test/server/*.t)
CLIENT_TESTS = $(wildcard test/client/*.t)
SCRIPT_TESTS = $(wildcard test/script/*.t)

default: build-java-libs compile-typespec

build-java-libs: build-rdptools

build-rdptools: checkout-rdptools RDPTools/SequenceMatch.jar

checkout-rdptools: RDPTools

RDPTools:
	git clone https://github.com/rdpstaff/RDPTools.git
	cd RDPTools; git submodule init; git submodule update

RDPTools/SequenceMatch.jar:
	cd RDPTools; make


compile-typespec: Makefile
	mkdir -p lib/biokbase/$(SERVICE_NAME_PY)
	touch lib/biokbase/__init__.py #do not include code in biokbase/__init__.py
	touch lib/biokbase/$(SERVICE_NAME_PY)/__init__.py 
	mkdir -p lib/javascript/$(SERVICE_NAME)
	compile_typespec \
	        --psgi $(SERVICE_PSGI_FILE) \
	        --impl Bio::KBase::$(SERVICE_NAME)::%sImpl \
	        --service Bio::KBase::$(SERVICE_NAME)::Service \
	        --client Bio::KBase::$(SERVICE_NAME)::Client \
	        --py biokbase/$(SERVICE_NAME_PY)/client \
	        --js javascript/$(SERVICE_NAME)/Client \
	        --url $(SERVICE_URL) \
	        $(SERVER_SPEC) lib

test-client:
	for t in $(CLIENT_TESTS) ; do \
		if [-f $$t]; then \
			$(DEPLOY_RUNTIME)/bin/python2.7 $$t; \
			if [$$? -ne 0]; then \
				exit 1; \
			fi \
		fi \
	done

test-scripts:
	for t in $(SCRIPT_TESTS); do \
		if [-f $$t]; then \
			$(DEPLOY_RUNTIME)/bin/python2.7 $$t; \
			if [$$? -ne 0]; then \
				exit 1; \
			fi \
		fi \
	done

test-service:
	for t in $(SERVER_TESTS); do \
		if [-f $$t]; then \
			$(DEPLOY_RUNTIME)/bin/python2.7 $$t; \
			if [$$? -ne 0]; then \
				exit 1; \
			fi \
		fi \
	done

test: test-client test-scripts test-service

deploy-client: deploy-libs deploy-scripts deploy-docs

deploy-service: deploy-libs #deploy-cfg
	mkdir -p $(SERVICE_DIR)
	mkdir -p $(SERVICE_DIR)/tmp
	chmod 777 $(SERVICE_DIR)/tmp
	mkdir -p $(SERVICE_DIR)/conf
	#cp conf/rdp-config.ini $(SERVICE_DIR)/conf
	$(TPAGE) $(TPAGE_ARGS) service/start_service.tt > $(SERVICE_DIR)/start_service
	chmod +x $(SERVICE_DIR)/start_service
	$(TPAGE) $(TPAGE_ARGS) service/stop_service.tt > $(SERVICE_DIR)/stop_service
	chmod +x $(SERVICE_DIR)/stop_service
	cp workflow/rdpclassify.awt.tt $(SERVICE_DIR)/rdpclassify.awt.tt

deploy: deploy-client

deploy-docs:
	mkdir -p $(SERVICE_DIR)/webroot

deploy-libs: compile-typespec
	rsync -arv RDPTools/*.jar $(TARGET)/lib
	mkdir -p $(TARGET)/lib/lib
	rsync -arv RDPTools/lib/*.jar $(TARGET)/lib/lib
	rsync -arv lib/. $(TARGET)/lib/.
	#cp lib/*.py $(TARGET)/lib

clean:
	rm -rfv $(SERVICE_DIR)
	rm -f start_service stop_service
    
include $(TOP_DIR)/tools/Makefile.common.rules
