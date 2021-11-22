# wsl-pathlib

[![Build Status](https://github.com/salticidae/wsl-pathlib/workflows/test/badge.svg?branch=master&event=push)](https://github.com/salticidae/wsl-pathlib/actions?query=workflow%3Atest)
[![codecov](https://codecov.io/gh/salticidae/wsl-pathlib/branch/master/graph/badge.svg)](https://codecov.io/gh/salticidae/wsl-pathlib)
[![Python Version](https://img.shields.io/pypi/pyversions/wsl-pathlib.svg)](https://pypi.org/project/wsl-pathlib/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

Extend `pathlib.Path` by addding the properties `wsl_path` and `win_path` that holds respectively the  WSL (Windows Subsystem for Linux) and Windows representation of the `Path` object.


## Features
- Works on both WSL and Windows side
- Lazy loading of the wsl_path and win_path properties on first access
- Base `Path` object fully functional

## Limitations
- Only works for paths living in the wsl's `'/mnt/'` mount point. `'/home/'` won't work.
- Performs very simple checks, for example: `if path[1] == ":" => windows`. I haven't fiddle with it to see how it behave for different edge cases.


## Installation

```bash
pip install wsl-pathlib
```


## Example

Showcase how your project can be used:

```python
from wsl_pathlib.path import WslPath

wsl_p = WslPath("/mnt/c/foo")
print(wsl_p.win_path)
# => 'C:\foo'

wsl_p2 = wsl_p / "file.txt"
print(wsl_p2.win_path)
# => 'C:\foo\file.txt'
```

## License

[MIT](https://github.com/salticidae/wsl-pathlib/blob/master/LICENSE)


## Credits

This project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [465848d4daab031f9be6e334ef34af011c2577bc](https://github.com/wemake-services/wemake-python-package/tree/465848d4daab031f9be6e334ef34af011c2577bc). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/465848d4daab031f9be6e334ef34af011c2577bc...master) since then.
