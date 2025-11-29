.ONESHELL:

SHELL = /usr/bin/bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
	@echo "Makefile commands:"
	@echo "  test      - Run the unit tests using pytest"
	@echo "  explore   - Run the experiments for using llm to provide recommendation"
test:
	$(CONDA_ACTIVATE) lr && pytest
explore:
	$(CONDA_ACTIVATE) lr &&  python3 explorations/exp_local_llm.py
