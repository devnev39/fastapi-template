# Fastapi-Mongodb Template

This is a simple fastapi mongodb template which some common features. 

> ## Please configure your own onboarding scripts before using them.

> To use poetry as package manager head over to poetry branch

## Features

- JWT Authentication
- Logging
- RBAC
- Testing with pytest
- Coverage

## Installation

This template uses [uv](https://docs.astral.sh/uv/) for package management. First install uv then follow below steps

Install the dependencies by

`uv sync`

Then you can source the virtual environment by

`source .venv/bin/activate`

Run the backend server by

`make run`

or

`make dev`

## Testing

Testing is done using pytest

`make test`

or 

`make test-vv`

## Coverage

Coverage package is used to measure code coverage.

This will test the code coverage and covert that report to html format in folder named htmlcov.

You have to open the index.html directly from the folder.

    `make coverage`

