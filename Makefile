test:
	python -m pytest

test-vv:
	python -m pytest -vv

run:
	uv run python -m fastapi run src/main.py --host 0.0.0.0 --port 8000

dev:
	uv run python -m fastapi dev src/main.py --host 0.0.0.0 --port 8000

coverage:
	coverage run --source src -m pytest -vv
	coverage report --show-missing
	coverage html

