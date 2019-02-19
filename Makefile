# This Makefile is not used (yet) for making, but rather, to simplify
# invocation of common tasks, especially about testing.
#
#
# SCL <scott@rerobots.net>
# Copyright (C) 2018 rerobots, Inc.

.PHONY: lint
lint:
	pylint --disable=fixme rerobots

.PHONY: check
check: lint
	cd tests && pytest -v

.PHONY: checklocal
checklocal: lint
	cd tests && pytest -v --ignore=test_anonymous.py

.PHONY: checkcover
checkcover: lint
	cd tests && coverage run --source=rerobots -m pytest -v
	cd tests && coverage html -d cover

.PHONY: checklocalcover
checklocalcover: lint
	cd tests && coverage run --source=rerobots -m pytest -v --ignore=test_anonymous.py
	cd tests && coverage html -d cover

.PHONY: checktests
checktests:
	pylint -j 4 -E `find tests -name \*.py`


clean:
	rm -rf tests/cover
	rm -f tests/.coverage
