# Variables
PYTHON = python3
TEST_DIR = tests
EXTRACT_DIR =  $(PWD)/core/extract
CORE_FOLDER = $(PWD)/core
COMMON_FOLDER = $(PWD)/common


# Targets
.PHONY: all run setup clean test

extract:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER)/:$(COMMON_FOLDER) && $(PYTHON) $(EXTRACT_DIR)/extract.py $(EXTRACT_DIR)/extract.yaml

setup: requirements.txt
	pip install -r requirements.txt

test:
	$(TEST_DIR)/

clean:
	rm -rf __pycache__