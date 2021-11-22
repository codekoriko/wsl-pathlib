# wsl-pathlib

[![Build Status](https://github.com/salticidae/wsl-pathlib/workflows/test/badge.svg?branch=master&event=push)](https://github.com/salticidae/wsl-pathlib/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/salticidae/wsl-pathlib/branch/master/graph/badge.svg)](https://codecov.io/gh/salticidae/wsl-pathlib)
[![Python Version](https://img.shields.io/pypi/pyversions/wsl-pathlib.svg)](https://pypi.org/project/wsl-pathlib/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

extend to pathlib.Path to add the attribute wsl_path and win_path that holds respectively the  WSL (Windows Subsystem for Linux) representation and Windows representation of that path.


## Features

- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Add yours!


## Installation

```bash
pip install wsl-pathlib
```


## Example

Showcase how your project can be used:

```python
from wsl_pathlib.example import some_function

print(some_function(3, 4))
# => 7
```

## License

[MIT](https://github.com/salticidae/wsl-pathlib/blob/master/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [465848d4daab031f9be6e334ef34af011c2577bc](https://github.com/wemake-services/wemake-python-package/tree/465848d4daab031f9be6e334ef34af011c2577bc). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/465848d4daab031f9be6e334ef34af011c2577bc...master) since then.
