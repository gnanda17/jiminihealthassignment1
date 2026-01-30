.PHONY: init format static run

init:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r requirements-dev.txt

format:
	./.venv/bin/black .

static:
	./.venv/bin/flake8 .

run:
	./.venv/bin/python server.py
