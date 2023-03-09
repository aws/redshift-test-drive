# Variables
PYTHON = python3
TEST_DIR = tests
EXTRACT_DIR =  $(PWD)/core/extract
CORE_FOLDER = $(PWD)/core
COMMON_FOLDER = $(PWD)/common
CONFIG_FOLDER = $(PWD)/config
REPLAY_DIR = $(PWD)/core/replay
REPLAY_ANALYSIS_DIR = $(PWD)/tools/replay-analysis
EXTERNAL_OBJECT_REPLICATOR_DIR = $(PWD)/tools/external-object-replicator




# Targets
.PHONY: all run setup clean test

extract:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(CORE_FOLDER)/util:$(COMMON_FOLDER) && $(PYTHON) $(EXTRACT_DIR)/extract.py $(CONFIG_FOLDER)/extract.yaml

replay:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(CORE_FOLDER)/util:$(COMMON_FOLDER) && $(PYTHON) $(REPLAY_DIR)/replay.py $(CONFIG_FOLDER)/replay.yaml

replay_analysis:
	export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(CORE_FOLDER)/util:$(COMMON_FOLDER) && export PYTHONPATH=$(PYTHONPATH):$(CORE_FOLDER):$(REPLAY_ANALYSIS_DIR)/util && $(PYTHON) $(REPLAY_ANALYSIS_DIR)/replay_analysis.py 

external-object-replicator:
	export PYTHONPATH=$(PYTHONPATH):$(EXTERNAL_OBJECT_REPLICATOR_DIR):$(EXTERNAL_OBJECT_REPLICATOR_DIR)/util && $(PYTHON) $(EXTERNAL_OBJECT_REPLICATOR_DIR)/external_object_replicator.py $(CONFIG_FOLDER)/external_object_replicator.yaml


setup: requirements.txt
	pip3 install -r requirements.txt

test:
	${PYTHON} -m unittest discover

clean:
	rm -rf __pycache__