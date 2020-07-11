test:
	pytest --capture=sys tests/

inter_test:
	pytest -k=interactive --capture=sys tests/

fast_test:
	pytest -k="not interactive" tests/

changelog:
	git log --oneline --decorate --color

mo_compile:
	msgfmt -o exam2pdf/locales/it/LC_MESSAGES/exam2pdf.mo exam2pdf/locales/it/LC_MESSAGES/exam2pdf.po

clean:
	find . -name '*.pyc' -execdir rm -f {} +
	find . -type d -name '__pycache__' -execdir rm -rf {} +
	find . -name '*.log' -execdir rm -f {} +
	python setup clean --all

black:
	black exam2pdf/
	black tests/unit/

build:
	python setup.py sdist bdist_wheel

.PHONY: test clean black build changelog mo_compile
