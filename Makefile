.ONESHELL:
SHELL = bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
	@echo "Makefile commands:"
	@echo "  run  				 - Run our chat application using Streamlit"
	@echo "  test     			 - Run the unit tests using pytest"
	@echo "  explore			 - Run the experiment "
test:
	$(CONDA_ACTIVATE) lr && pytest
explore:
	$(CONDA_ACTIVATE) lr &&  python3 explorations/exp_llm_single.py
run:
	$(CONDA_ACTIVATE) lr &&  streamlit run app/streamlit/chat.py