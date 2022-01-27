help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:  ## Create a new environment with poetry and install the package
	poetry install

test:  ## Run the test suite using pytest
	pytest

lint:  ## Run linting checks with flake8 and black
	flake8 spatial_kde/
	black --check spatial_kde/

format:  ## Run black to format the code
	black .