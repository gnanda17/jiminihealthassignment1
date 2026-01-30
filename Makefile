config.yml: config.example.yml
	cp config.example.yml config.yml

.PHONY: init
init: config.yml
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r requirements-dev.txt

.PHONY: format
format:
	./.venv/bin/black .

.PHONY: static
static:
	./.venv/bin/flake8 .

.PHONY: run
run:
	./.venv/bin/python server.py
