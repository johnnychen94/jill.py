JULIA_VERSIONS = "1" "1.0" "1.1" "1.2" "1.3" "1.4.0-rc1" "latest"
unittest:
	python -m unittest jill/tests/tests_filters.py
	python -m unittest jill/tests/tests_versions.py

download_install_test:
	# check if upstream works
	coverage run -a -m jill download --upstream Official
	coverage run -a -m jill install --upstream Official --confirm --keep_downloads

	for julia_version in $(JULIA_VERSIONS) ; do \
		echo "Test Julia version:" $$julia_version ; \
		coverage run -a -m jill download $$julia_version ; \
		coverage run -a -m jill install $$julia_version --confirm --keep_downloads ; \
		julia -e 'using InteractiveUtils; versioninfo()' ; \
	done

	# check if symlinks are created successfully
	bash installtest.sh 1.0.5
	find . -type f -size +20M -name "julia-*" -delete ; \

test:
	@+make unittest
	@+make download_install_test
