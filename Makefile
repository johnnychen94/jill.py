JULIA_VERSIONS = "1" "1.0" "1.1" "1.2" "1.3" "latest"
unittest:
	python -m unittest jill/tests/tests_filters.py

download_install_test:
	coverage run -a -m jill download --upstream Official
	coverage run -a -m jill install --upstream Official --confirm

	for julia_version in $(JULIA_VERSIONS) ; do \
		echo "Test Julia version:" $$julia_version ; \
		coverage run -a -m jill download $$julia_version ; \
		coverage run -a -m jill install $$julia_version --confirm ; \
	done

	# check if symlinks are created successfully
	bash installtest.sh 1.0.5
	find . -type f -size +20M -name "julia-*" -delete ; \

test:
	@+make unittest
	@+make download_install_test
