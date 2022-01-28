help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:  ## Create a new environment with poetry and install with pre-commit hooks
	poetry install
	pre-commit install

test:  ## Run the test suite using pytest
	poetry run pytest --cov spatial_kde

lint:  ## Run linting checks with flake8 and black
	poetry run flake8 spatial_kde/
	poetry run black --check spatial_kde/

format:  ## Run black to format the code
	poetry run black .