wagyu
=====

[![](https://dev.azure.com/lycantropos/wagyu/_apis/build/status/lycantropos.wagyu?branchName=master)](https://dev.azure.com/lycantropos/wagyu/_build/latest?definitionId=28&branchName=master "Azure Pipelines")
[![](https://codecov.io/gh/lycantropos/wagyu/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/wagyu "Codecov")
[![](https://img.shields.io/github/license/lycantropos/wagyu.svg)](https://github.com/lycantropos/wagyu/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/wagyu.svg)](https://badge.fury.io/py/wagyu "PyPI")

In what follows `python` is an alias
for `python3.5` or `pypy3.5` or any later version
(`python3.6`, `pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository:
```bash
python -m pip install --upgrade wagyu
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/wagyu.git
cd wagyu
```

Install setup dependencies:
```bash
python -m pip install --force-reinstall -r requirements-setup.txt
```

Install:
```bash
python setup.py install
```

Usage
-----
```python
>>> from wagyu.enums import PolygonKind
>>> from wagyu.linear_ring import LinearRing
>>> from wagyu.point import Point
>>> from wagyu.polygon import Multipolygon, Polygon
>>> from wagyu.wagyu import Wagyu
>>> lower_triangle = Polygon([LinearRing([Point(0, 0), Point(6, 0), Point(3, 3), Point(0, 0)])])
>>> upper_triangle = Polygon([LinearRing([Point(3, 1), Point(6, 4), Point(0, 4), Point(3, 1)])])
>>> wagyu = Wagyu()
>>> wagyu.add_polygon(lower_triangle, PolygonKind.SUBJECT)
True
>>> wagyu.add_polygon(upper_triangle, PolygonKind.CLIP)
True
>>> (wagyu.intersect()
...  == Multipolygon([Polygon([LinearRing([Point(3, 1), Point(4, 2), Point(3, 3), Point(2, 2), Point(3, 1)])])]))
True
>>> (wagyu.unite()
...  == Multipolygon([Polygon([LinearRing([Point(6, 0), Point(4, 2), Point(6, 4), Point(0, 4), Point(2, 2), Point(0, 0), Point(6, 0)])])]))
True
>>> (wagyu.symmetric_subtract()
...  == Multipolygon([Polygon([LinearRing([Point(4, 2), Point(3, 1), Point(2, 2), Point(0, 0), Point(6, 0), Point(4, 2)])]),
...                   Polygon([LinearRing([Point(4, 2), Point(6, 4), Point(0, 4), Point(2, 2), Point(3, 3), Point(4, 2)])])]))
True
>>> (wagyu.subtract()
...  == Multipolygon([Polygon([LinearRing([Point(6, 0), Point(4, 2), Point(3, 1), Point(2, 2), Point(0, 0), Point(6, 0)])])]))
True

```
for `CPython` original C++ implementation can be invoked by importing from `_wagyu` module instead.

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies:
```bash
python -m pip install --force-reinstall -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
