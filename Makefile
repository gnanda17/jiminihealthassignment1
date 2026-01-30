config.yml: config.example.yml
	cp config.example.yml config.yml

.env: .env.example
	cp .env.example .env

.PHONY: init
init: config.yml .env
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

.PHONY: test
test:
	./.venv/bin/pytest tests/ -v
