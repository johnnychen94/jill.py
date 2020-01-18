unittest:
	python -m unittest jill/tests/tests_filters.py

downloadtest:
	python -m jill download ${JULIA_VERSION}

installtest:
	bash installtest.sh

mirrortest:
	python mirror_daemon.py --config test_mirror.json
	find julia_pkg -name "julia-*"

test:
	@+make unittest
	@+make downloadtest
	@+make installtest
	@+make mirrortest
