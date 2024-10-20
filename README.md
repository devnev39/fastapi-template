# Fastapi-Mongodb Template

This is a simple fastapi mongodb template which some common features. 

> ## Please configure your own onboarding scripts before using them.

> To use uv as package manger head over to main branch.

## Features

- JWT Authentication
- Logging
- RBAC
- Testing with pytest
- Coverage

## Installation

1. Since this template uses poetry for dependencies, make sure you have poetry installed.

    `pip install poetry`

2. Install the dependencies using

    `poetry install`

3. Run the application using

    `make dev` or `make run`


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

