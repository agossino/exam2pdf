test:
	pytest --capture=sys tests/

clean:
	find . -name '*.pyc' -execdir rm -f {} +
	find . -type d -name '__pycache__' -execdir rm -rf {} +
	find . -name '*.log' -execdir rm -f {} +
	python setup clean --all

black:
	black quest2pdf/
	black tests/unit/

build:
	python setup.py sdist bdist_wheel

.PHONY: test clean black build
