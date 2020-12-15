CI_FILES=cape

ci: lint test coverage

fmt:
	isort --atomic ${CI_FILES}
	black ${CI_FILES}

lint:
	flake8 ${CI_FILES}

test:
	pytest

bootstrap:
	pip install -U pip setuptools
	pip install -r requirements.txt
	pip install -e .

coverage:
	pytest --cov-report=xml --cov=cape cape
	coverage report
