init:
	pip install -r requirements.txt

install:
	pip install .

test:
	# py.test tests - Not implemented just yet

.PHONY: init test
