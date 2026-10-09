<span align="center">

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![tests](https://github.com/billwallis/git-meta/actions/workflows/tests.yaml/badge.svg)](https://github.com/billwallis/git-meta/actions/workflows/tests.yaml)
[![coverage](https://raw.githubusercontent.com/billwallis/git-meta/refs/heads/main/coverage.svg)](https://smarie.github.io/python-genbadge/)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/billwallis/git-meta/main.svg)](https://results.pre-commit.ci/latest/github/billwallis/git-meta/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/billwallis/git-meta)](https://shields.io/badges/git-hub-last-commit)

</span>

---

# Git Meta

Tools for handling many Git repositories.

## Contributing

Install the dependencies:

```shell
python -m venv .venv/
source .venv/bin/activate

pip install --editable . --group dev --group test
pre-commit install --install-hooks
```
