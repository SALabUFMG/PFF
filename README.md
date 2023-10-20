# Handling Tracking Data from PFF

This package handles tracking data from PFF FC.

- [Features](#features)
- [Python version](#python)
- [Setup Guide](#setup-guide)
- [Usage](#usage)
- [Testing](#testing)

## Python

- Python 3.10 or higher

## What is in this repo

- Pitch control
- OBSO
- Data cleansing
- Frame visualization

## Setup guide

Here's what you have to do to clone and install the requirements.

```bash
git clone git@github.com:SALabUFMG/PFF.git
cd PFF

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Poetry package manager
pip install poetry

# Install project dependencies
poetry install
```

When you're done, don't forget to deactivate the virtual env:

```bash
deactivate
```

## Usage
Details on how to use each of the tools in this repository will be provided soon.

## Testing
Testing guidelines and procedures will be added in the near future :)

## Contributing

If you plan to contribute to the project, make sure to install the pre-commit hooks:

```bash
pre-commit install
```

The pre-commit hooks will run automatically when you attempt to commit code. Make sure they pass to ensure code quality and maintainability.
