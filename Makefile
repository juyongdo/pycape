CI_FILES=pycape

ci: lint test coverage

fmt:
    poetry install
	isort --atomic ${CI_FILES}
	black ${CI_FILES}

lint:
    poetry install
	flake8 ${CI_FILES}

test:
    poetry install
	pytest

bootstrap:
	poetry install

coverage:
    poetry install
	pytest --cov-report=xml --cov=pycape ${CI_FILES}
	coverage report
