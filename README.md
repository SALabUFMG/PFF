# Handling Tracking Data from PFF

This package handles tracking data from PFF FC.

- [Setup Guide](#setup-guide)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)

## Python

- Python 3.10 or higher

## What is in this repo

- Data cleansing
- Frame visualization
- Pitch control

## Setup guide

### Using Make

To clone the repository and install all requirements, you can use the provided `Makefile`:

```bash
git clone git@github.com:SALabUFMG/PFF.git
cd PFF
make install
```

This will create a virtual environment, install Poetry, and install all project dependencies. In addition, it will build the pitch control modules.

Running `make` without args will also install all deps.

Activate venv and you're good to go:

```bash
. .venv/bin/activate
```

### Manual install

If you don't want to use the Makefile, you can follow the lines below:

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

#### Pitch Control modules

Before you build the Pitch Control modules, ensure that you have a C++ compiler installed.

In MacOS:

```bash
brew install gcc
```

You can manually build the Pitch Control module by running from the root directory:

```bash
python build_pitch_control.py build_ext --inplace
```

## Usage
Details on how to use each of the tools in this repository will be provided soon.

Until then, don't forget to deactivate the virtualenv when you're done:

```bash
deactivate
```

## Testing
Testing guidelines and procedures will be added in the near future :)

## Contributing

If you plan to contribute to the project, make sure to install the pre-commit hooks:

```bash
make dev
```

The pre-commit hooks will run automatically when you attempt to commit code. Make sure they pass to ensure code quality and maintainability.

To clean the repo of compiled and generated files, run

```bash
make clean
```
