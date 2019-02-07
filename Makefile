# This Makefile is not used (yet) for making, but rather, to simplify
# invocation of common tasks, especially about testing.
#
#
# SCL <scott@rerobots.net>
# Copyright (C) 2018 rerobots, Inc.

.PHONY: check
check:
	pylint -j 4 -E `find rerobots -name \*.py`
	cd tests && nosetests -v

.PHONY: checklocal
checklocal:
	pylint -j 4 -E `find rerobots -name \*.py`
	cd tests && nosetests -v -I test_anonymous.py

.PHONY: checkcover
checkcover:
	pylint -j 4 -E `find rerobots -name \*.py`
	cd tests && nosetests -v --with-coverage --cover-html --cover-package=rerobots

.PHONY: checklocalcover
checklocalcover:
	pylint -j 4 -E `find rerobots -name \*.py`
	cd tests && nosetests -v --with-coverage --cover-html --cover-package=rerobots -I test_anonymous.py

.PHONY: checktests
checktests:
	pylint -j 4 -E `find tests -name \*.py`


clean:
	rm -rf tests/cover
	rm -f tests/.coverage
