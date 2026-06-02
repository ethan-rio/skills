# Code Quality Setup Guide

1. [Getting Started](#1-getting-started)
2. [Purpose](#2-purpose)
   1. [Required Dependencies](#21-required-dependencies)
   2. [Getting started with `uv`](#22-getting-started-with-uv)
      1. [Install a suitable Python version](#221-install-a-suitable-python-version)
      2. [(Automatically) Setup your environment](#222-automatically-setup-your-environment)
      3. [Adding and removing packages](#223-adding-and-removing-packages)
3. [Code Quality Files and Configuration](#3-code-quality-files-and-configuration)
4. [Using the Tools](#4-using-the-tools)
   1. [Setting the Target Folders](#41-setting-the-target-folders)
   2. [Checking `.py` files](#42-checking-py-fileschecking-py-files)
   3. [Checking `.ipynb` files](#43-checking-ipynb-fileschecking-ipynb-files)
      1. [Scanning notebooks for function definitions](#431-scanning-notebooks-for-function-definitionsscanning-notebooks-for-function-definitions)
5. [Changing Linter and Formatter Settings](#5-changing-formatter-and-linter-settings)
   1. [Python files](#51-python-filespython-files)
   2. [Notebooks and Tests](#52-notebooks-and-testsnotebooks-and-tests)
6. [Using `pip` or `poetry`](#6-using-pip-or-poetry)

# 1. Getting Started 

1. Install the [required dependencies](#21-required-dependencies).
2. Do an initial run of the tools to ensure that everything is installed correctly.
   1. Run the steps in [section 4.2](#42-checking-py-files) for python files and compare against the example output. 
   2. Run the steps in [section 4.3](#43-checking-ipynb-files) for notebooks and compare against the example output.
   3. **Note** that the formatter *will* make changes to some files.
3. Replace the [`./src/example_code_quality/`](./src/example_code_quality/) and [`./notebooks/example_code_quality`](./notebooks/example_code_quality) folders with your source files.
4. Change the target directories for the tools in the [`Makefile`](./Makefile) as explained in [section 4.1](#41-setting-the-target-folders).

# 2. Purpose

The purpose of this setup is to improve and enforce code quality in new repositories. It does this by linting, formating and enforces types via static type checking. 

<details>

<summary> <i>Click to see a detailed explanation of the tools and packages used in this template. </i> </summary>

<br />

This setup contains a Makefile to check and format code by using the tools [`ruff`](https://docs.astral.sh/ruff/) and [`nbQA`](https://github.com/nbQA-dev/nbQA) for notebooks. This tool is intended to function in an identical manner to other tools such as [`black`](https://pypi.org/project/black/), [`isort`](https://github.com/PyCQA/isort) and [`flake8`](https://flake8.pycqa.org/en/latest/). The Makefile runs 4 code-quality steps (in no particular order):

1. [**Linting**](https://docs.astral.sh/ruff/linter/): Checks code for styling issues, complexity, function annotations, docstrings and more. The list of rules followed by [`ruff`](https://docs.astral.sh/ruff/) are listed [here](https://docs.astral.sh/ruff/rules/).
2. [**Sorting imports**](https://docs.astral.sh/ruff/formatter/#sorting-imports): Functions very similarly to [`isort`](https://github.com/PyCQA/isort) by formatting code by sorting imports (at the beginning of .py files for example)
3. [**Formatting**](https://docs.astral.sh/ruff/formatter/): Functions very similarly to [`black`](https://pypi.org/project/black/). It does things like fixing spacing and adding line-breaks where code exceeds the provided line-length limit.
4. **Static Checking**: This is done using [`mypy`](https://mypy-lang.org/) which checks whether functions are called appropriately with respect to their type definitions and any other bugs which can be detected before runtime.

It supports Python versions upwards of and including Python 3.12.

</details>

## 2.1 Required Dependencies


This setup is configured using [`uv`](https://docs.astral.sh/uv/). In addition to `uv`, ensure that you have [`make`](https://www.gnu.org/software/make/) installed as well.


## 2.2 Getting started with `uv`

A basic set of commands for using `uv` for managing environments are as described in the sections below.

### 2.2.1 Install a suitable Python version 

Install Python 3.12 because that is the minimum Python requirement.

```bash
uv python install 3.12
```

You may get an error that looks like an SSL certificate error, in which case, try this:

```bash
uv python install --native-tls 3.12  # "Should" work for Windows
```

Or you may need to export the location of your SSL certificate files

```bash
# Each machine may be different, for example, the developer of this template had to do this:
export SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.pem
```

### 2.2.2 (Automatically) Setup your environment

`uv` will automatically create an environment in a `.venv` folder for you. Running the following command should install all required dependencies:

```bash
uv sync
```

To run packages, you need to use the `uv run` interface:

```bash
uv run ruff
uv run nbqa
uv run mypy
```

### 2.2.3 Adding and removing packages

To add and remove packages you can use the `uv add` and `uv remove` interface. Adding a package:

```bash
# Add numpy to the environment
uv add numpy

# Removing numpy
uv remove numpy
```

You can add `dev` packages using the `--dev` flag. This is used for adding packages that would be used during development but not during deployment.

```bash
# Adding pretty-print during development
uv add --dev pytz
```



# 3. Code Quality Files and Configuration

The following files relate to the code quality setup used in this repository and referenced in this guide:

```shell
├── docs
│      └── CODE_QUALITY_SETUP_GUIDE.md         # The current guide
├── notebooks
│      └── example_code_quality                # Example notebooks on which the Makefile can be run
│                ├── has_functions.ipynb       # This notebook has functions and the code_quality_notebook_analyser will complain about it
│                └── no_functions.ipynb        # The formatter will change some of the code in this notebook
├── scripts
│      └── code_quality_notebook_analyser.py   # Python script that analyses a notebook   
├── src                                        
│    └── example_code_quality                  # Example python files on which the Makefile can be run
│              ├── test_type_hinting.py        # Type hinting errors
│              └── unsorted_imports.py         # Unsorted imports which will be sorted in the correct order after running the Makefile
├── Makefile                                   # Makefile that holds the linting commands
├── pyproject.toml                             # Holds the configuration settings for python source files
└── uv.lock                                    # Locked dependency versions for reproducible environments
```

# 4. Using the tools

## 4.1 Setting the Target Folders

Within the Makefile, the following variables define the target directories:

```make
# .py files location (multiple folders or files can be listed, eg. folder1 folder2)
PY_FOLDERS = ./src/example_code_quality/ 
# notebook folder
NB_FOLDER = ./notebooks/example_code_quality/
```

To target different folders, simply change those variables. 

## 4.2 Checking `.py` files
The above modules can be run with the single make command*:

```shell
# Runs linting and static checking on all .py source files
make check_code_quality
# or simply
make
```
<details>
<summary><b>Click here to see some example output</b></summary>

**Terminal output**:
```shell
Run code linting
uv run ruff check --config=pyproject.toml --output-format concise ./src/example_code_quality/
src/example_code_quality/test_type_hinting.py:6:5: ANN201 Missing return type annotation for public function `capitalize_str`
src/example_code_quality/test_type_hinting.py:6:5: D103 Missing docstring in public function
src/example_code_quality/test_type_hinting.py:6:20: ANN001 Missing type annotation for function argument `lower_case_str`
src/example_code_quality/unsorted_imports.py:1:1: D400 First line should end with a period
src/example_code_quality/unsorted_imports.py:3:1: UP035 `typing.List` is deprecated, use `list` instead
src/example_code_quality/unsorted_imports.py:3:20: F401 [*] `typing.List` imported but unused
src/example_code_quality/unsorted_imports.py:4:8: F401 [*] `argparse` imported but unused
src/example_code_quality/unsorted_imports.py:5:8: F401 [*] `json` imported but unused
src/example_code_quality/unsorted_imports.py:6:21: F401 [*] `pathlib.Path` imported but unused
src/example_code_quality/unsorted_imports.py:6:27: F401 [*] `pathlib.WindowsPath` imported but unused
src/example_code_quality/unsorted_imports.py:7:8: F401 [*] `ast` imported but unused
src/example_code_quality/unsorted_imports.py:8:8: F401 [*] `glob` imported but unused
src/example_code_quality/unsorted_imports.py:8:12: W292 [*] No newline at end of file
Found 13 errors.
[*] 8 fixable with the `--fix` option (1 hidden fix can be enabled with the `--unsafe-fixes` option).
make: [Makefile:47: check_code_quality] Error 1 (ignored)

Fix order of imports via the isort plugin within ruff
uv run ruff check --select I --fix ./src/example_code_quality/
Found 1 error (1 fixed, 0 remaining).

Format code. Manage indents, break lines exceeding max line lengths
uv run ruff format --config=pyproject.toml ./src/example_code_quality/
2 files left unchanged

Running static checker
uv run mypy --config=pyproject.toml ./src/example_code_quality/
src/example_code_quality/test_type_hinting.py:28: error: Argument 1 to "addition_typed" has incompatible type "str"; expected "int"  [arg-type]
src/example_code_quality/test_type_hinting.py:28: error: Argument 2 to "addition_typed" has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 1 file (checked 2 source files)
make: [Makefile:53: check_code_quality] Error 1 (ignored)
```

</details>

<br />

*Note that you must have `make` installed and must have installed the project dependencies.

## 4.3 Checking `.ipynb` files
The Makefile can also optionally run `nbqa` to run the above formatters, linters and static checkers on notebooks.
```shell
# Runs linting on .ipynb notebook files
make check_code_quality_nb
```

<details>
<summary><b>Click here to see some example output</b></summary>

```shell
Run code linting
uv run ruff check --config=pyproject.toml --output-format concise ./notebooks/example_code_quality/
notebooks/example_code_quality/no_functions.ipynb:cell 2:3:19: W291 [*] Trailing whitespace
Found 1 error.
[*] 1 fixable with the `--fix` option.
make: [Makefile:88: check_code_quality_nb] Error 1 (ignored)

Fix order of imports via the isort plugin within ruff
uv run ruff check --select I --fix ./notebooks/example_code_quality/
All checks passed!

Format code. Manage indents, break lines exceeding max line lengths
uv run ruff format --config=pyproject.toml ./notebooks/example_code_quality/
1 file reformatted, 1 file left unchanged

Running static checker
uv run nbqa mypy --config=pyproject.toml ./notebooks/example_code_quality/
Success: no issues found in 2 source files

Checking for presence of functions in notebooks
uv run python scripts/code_quality_notebook_analyser.py ./notebooks/example_code_quality/
notebook_analyser: Analysing notebooks/example_code_quality/no_functions.ipynb...
notebook_analyser: notebooks/example_code_quality/no_functions.ipynb has no functions in it :)
```

</details>

### 4.3.1 Scanning notebooks for function definitions 
It is encouraged to define functions in `.py` files and to then import and call them within notebooks. 
For this reason, running `make check_linting_nb` will also log which notebooks cells contain function definitons and returns an error until these are moved into `.py` files: 

```shell
python scripts/code_quality_notebook_analyser.py notebooks/example_code_quality/
```

Expected output:

```shell
notebook_analyser: Analysing notebooks/example_code_quality/has_functions.ipynb...
notebook_analyser: notebooks/example_code_quality/has_functions.ipynb has function in cell number 1
notebook_analyser: notebooks/example_code_quality/has_functions.ipynb has function in cell number 2

notebook_analyser: Analysing notebooks/example_code_quality/no_functions.ipynb...
notebook_analyser: notebooks/example_code_quality/no_functions.ipynb has no functions in it :)
```

# 5. Changing formatter and linter settings

The configuration of the tools has been predefined in `pyproject.toml` for python files and notebooks. These settings are designed to align with our [Code Style Guidelines](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/14722/Code-Style-Guidelines). 

You may modify these settings within the file as needed, but ensure that all changes continue to comply with the guidelines.

## 5.1 Python files

The configuration for linting can be changed in the following section in `pyproject.toml`:

```INI
[tool.ruff.lint]
select = [
    # Select the rules you want to apply
]
ignore = [
    # Select the rules that you wish to ignore
]
```

The configuration for formatting can be changed in this section:

```INI
[tool.ruff.format]
# List your rules here
```

## 5.2 Notebooks and Tests

There may be some error categories that do not make sense for notebooks. Some of these categories are:

1. [`D`](https://docs.astral.sh/ruff/rules/#pydocstyle-d): A lot of `pydocstyle` rules may not need to be applied to notebooks.
2. [`ANN`](https://docs.astral.sh/ruff/rules/#flake8-annotations-ann): `flake8-annotations` checks are disabled for notebooks.

[`ANN`](https://docs.astral.sh/ruff/rules/#flake8-annotations-ann) have also been turned off for tests.

To change any settings for notebooks or tests, in the `pyproject.toml` file, categories you want to ignore can be added:

```INI
[tool.ruff.lint.per-file-ignores]
"tests/**" = [
    # flake8-annotations
    "ANN",
]
"*.ipynb" = [
    # flake8-annotations
    "ANN",
    # flake8-docstring
    "D",
]
```
# 6. Using `pip` or `poetry`

If you need to review how code-quality tooling was previously set up using `pip` or `poetry`, refer to the historical (now unmaintained) tags below:

- [`code-quality-pip-2025.11.28`](https://github.com/rio-tinto/dna-bne-project-template/tree/code-quality-pip-2025.11.28?tab=readme-ov-file)
- [`code-quality-poetry-2025.11.28`](https://github.com/rio-tinto/dna-bne-project-template/tree/code-quality-poetry-2025.11.28?tab=readme-ov-file)

These examples are provided for reference only and are no longer updated.