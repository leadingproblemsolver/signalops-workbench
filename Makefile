PYTHON ?= python
.PHONY: install test smoke validate clean
install:
	$(PYTHON) -m pip install -e .
test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
smoke:
	$(PYTHON) scripts/smoke_test.py
validate: test smoke
clean:
	rm -rf build dist *.egg-info .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
