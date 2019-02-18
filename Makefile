# This Makefile is not used (yet) for making, but rather, to simplify
# invocation of common tasks, especially about testing.
#
#
# SCL <scott@rerobots.net>
# Copyright (C) 2018 rerobots, Inc.

.PHONY: lint
lint:
	pylint rerobots

.PHONY: check
check: lint
	cd tests && nosetests -v

.PHONY: checklocal
checklocal: lint
	cd tests && nosetests -v -I test_anonymous.py

.PHONY: checkcover
checkcover: lint
	cd tests && nosetests -v --with-coverage --cover-html --cover-package=rerobots

.PHONY: checklocalcover
checklocalcover: lint
	cd tests && nosetests -v --with-coverage --cover-html --cover-package=rerobots -I test_anonymous.py

.PHONY: checktests
checktests:
	pylint -j 4 -E `find tests -name \*.py`


clean:
	rm -rf tests/cover
	rm -f tests/.coverage
