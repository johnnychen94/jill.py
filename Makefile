JULIA_VERSIONS = "" "1" "1.0" "1.0.5" "1.1" "1.2" "1.3" "latest"
unittest:
	python -m unittest jill/tests/tests_filters.py

downloadtest:
	for julia_version in $(JULIA_VERSIONS) ; do \
		echo $$julia_version ; \
		coverage run -a -m jill download $$julia_version ; \
	done

installtest:
	for julia_version in $(JULIA_VERSIONS) ; do \
		echo $$julia_version ; \
		coverage run -a -m jill install $$julia_version --confirm ; \
	done
	# check if symlinks are created successfully
	bash installtest.sh 1.0.0

test:
	@+make unittest
	@+make downloadtest
	@+make installtest
