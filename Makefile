
XUTOOLS_ROOT=.
CONFIG_DIR=$(XUTOOLS_ROOT)/config
DOC_DIR=$(XUTOOLS_ROOT)/doc
DOC_DIR_DOXYGEN=$(DOC_DIR)/doxygen
DOC_DIR_MAN=$(DOC_DIR)/man
DOC_DIR_WEBROOT=$(DOC_DIR)/webroot

SRC_DIR=$(XUTOOLS_ROOT)/src
DIST_DIR=$(XUTOOLS_ROOT)/dist

all: usage

clean_desc="clean:  clean the build\n"
clean:
	rm -rf $(DOC_DIR_DOXYGEN)

init_desc="init:  initialize the build\n"
init:	
	mkdir -p $(DOC_DIR_DOXYGEN)

doc_desc="doc:  generate documentation\n"
doc:	init
	doxygen $(CONFIG_DIR)/Doxyfile

test:
	python $(SRC_DIR)/run_test_suite.py

usage:	
	@echo "-------------------"
	@echo "target: description"
	@echo "-------------------"
	@echo $(clean_desc)
	@echo $(init_desc)
	@echo $(doc_desc)
