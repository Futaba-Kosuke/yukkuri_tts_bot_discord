init:
	poetry install -v
	cp .env.template .env
	git config --local core.hooksPath .githooks

env:
	poetry shell

run:
	poetry run python src

lint:
	poetry run isort .
	poetry run black .
	poetry run flake8 .
	poetry run mypy .
