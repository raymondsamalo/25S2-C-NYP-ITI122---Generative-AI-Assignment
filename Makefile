.ONESHELL:

SHELL = /usr/bin/bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
	@echo "Makefile commands:"
	@echo "  run  				 - Run our chat application using Streamlit"
	@echo "  test     			 - Run the unit tests using pytest"
	@echo "  explore_llm_multi   - Run the experiment for using multiple tools with llm"
	@echo "  explore_llm_single  - Run the experiment for using single tool with llm"
test:
	$(CONDA_ACTIVATE) lr && pytest
explore_llm_multi:
	$(CONDA_ACTIVATE) lr &&  python3 explorations/exp_llm_multi.py
explore_llm_single:
	$(CONDA_ACTIVATE) lr &&  python3 explorations/exp_llm_single.py
run:
	$(CONDA_ACTIVATE) lr &&  streamlit run app/streamlit/chat.py