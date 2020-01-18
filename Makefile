unittest:
	python -m unittest jill/tests/tests_filters.py

downloadtest:
	python -m jill download ${JULIA_VERSION}

installtest:
	bash installtest.sh

test:
	@+make unittest
	@+make downloadtest
	@+make installtest
