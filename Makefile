# Variables
PYTHON = python3
TEST_DIR = tests
EXTRACT_DIR =  $(PWD)/core/extract
CORE_FOLDER = $(PWD)/core
COMMON_FOLDER = $(PWD)/common
CONFIG_FOLDER = $(PWD)/config
REPLAY_DIR = $(PWD)/core/replay



# Targets
.PHONY: all run setup clean test

extract:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(CORE_FOLDER)/util:$(COMMON_FOLDER) && $(PYTHON) $(EXTRACT_DIR)/extract.py $(CONFIG_FOLDER)/extract.yaml

replay:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(CORE_FOLDER)/util:$(COMMON_FOLDER) && $(PYTHON) $(REPLAY_DIR)/replay.py $(CONFIG_FOLDER)/replay.yaml

setup: requirements.txt
	pip3 install -r requirements.txt

test:
	${PYTHON} -m unittest discover

clean:
	rm -rf __pycache__