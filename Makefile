help:
	@echo "Makefile commands:"
	@echo "  test      - Run the unit tests using pytest"
	@echo "  explore   - Run the experiments for using llm to provide recommendation"
test:
	pytest
explore:
	python3 explorations/exp_local_llm.py