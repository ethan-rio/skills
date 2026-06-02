# The default target to run
.DEFAULT_GOAL := check_code_quality

# Config file location
TOML_CONFIG = pyproject.toml

# UV commands
UV_RUN = uv run
UV_RUN_RUFF = uv run ruff

###################################################################################
#                              CODE QUALITY                                       #
###################################################################################

# .py files location (multiple folders or files can be listed, eg. folder1 folder2)
PY_FOLDERS = ./src/example_code_quality/

# notebook folder
NB_FOLDER = ./notebooks/example_code_quality/

#################################### .py files ####################################

.PHONY: check_linting
check_linting:
	@echo Code style checking and linting
	-$(UV_RUN_RUFF) check --config=$(TOML_CONFIG) --output-format concise $(PY_FOLDERS)

.PHONY: apply_isort
apply_isort:
	@echo "Fix order of imports via the isort plugin within ruff"
	-$(UV_RUN_RUFF) check --select I --fix $(PY_FOLDERS)

.PHONY: format_code
format_code:
	@echo "Format code. Manage indents, break lines exceeding max line lengths"
	$(UV_RUN_RUFF) format --config=$(TOML_CONFIG) $(PY_FOLDERS)

.PHONY: apply_mypy
apply_mypy:
	@echo "Running static checker - mypy"
	-$(UV_RUN) mypy --config=$(TOML_CONFIG) $(PY_FOLDERS)

.PHONY: check_code_quality
## Code style checking and linting
check_code_quality:
	@echo "Run code linting"
	-$(UV_RUN_RUFF) check --config=$(TOML_CONFIG) --output-format concise $(PY_FOLDERS)

	@echo "\nFix order of imports via the isort plugin within ruff"
	-$(UV_RUN_RUFF) check --select I --fix $(PY_FOLDERS)

	@echo "\nFormat code. Manage indents, break lines exceeding max line lengths"
	$(UV_RUN_RUFF) format --config=$(TOML_CONFIG) $(PY_FOLDERS)

	@echo "\nRunning static checker"
	-$(UV_RUN) mypy --config=$(TOML_CONFIG) $(PY_FOLDERS)

#################################### .ipynb files ####################################

.PHONY: check_linting_nb
check_linting_nb:
	@echo "Code style checking and linting"
	-$(UV_RUN_RUFF) check --config=$(TOML_CONFIG) --output-format concise $(NB_FOLDER)

.PHONY: apply_isort_nb
apply_isort_nb:
	@echo "Fix order of imports via the isort plugin within ruff"
	-$(UV_RUN_RUFF) check --select I --fix $(NB_FOLDER)

.PHONY: format_code_nb
format_code_nb:
	@echo "Format code. Manage indents, break lines exceeding max line lengths"
	-$(UV_RUN_RUFF) format --config=$(TOML_CONFIG) $(NB_FOLDER)

.PHONY: apply_mypy_nb
apply_mypy_nb:
	@echo "Running static checker"
	-$(UV_RUN) mypy --config=$(TOML_CONFIG) $(NB_FOLDER)

.PHONY: check_functions_nb
check_functions_nb:
	@echo "Checking for presence of functions in notebooks"
	-$(UV_RUN) python scripts/code_quality_notebook_analyser.py $(NB_FOLDER)

.PHONY: check_code_quality_nb
check_code_quality_nb:
	@echo "\nRun code linting"
	-$(UV_RUN_RUFF) check --config=$(TOML_CONFIG) --output-format concise $(NB_FOLDER)

	@echo "\nFix order of imports via the isort plugin within ruff"
	-$(UV_RUN_RUFF) check --select I --fix $(NB_FOLDER)

	@echo "\nFormat code. Manage indents, break lines exceeding max line lengths"
	-$(UV_RUN_RUFF) format --config=$(TOML_CONFIG) $(NB_FOLDER)

	@echo "\nRunning static checker"
	-$(UV_RUN) nbqa mypy --config=$(TOML_CONFIG) $(NB_FOLDER)

	@echo "\nChecking for presence of functions in notebooks"
	-$(UV_RUN) python scripts/code_quality_notebook_analyser.py $(NB_FOLDER)