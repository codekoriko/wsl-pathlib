# -*- coding: utf-8 -*-

import pytest
from pathlib import Path

from wsl_pathlib.path import WslPath


@pytest.mark.parametrize(('fullpath_in', 'getter', 'expected'), [
    (r"D:\.wor\test.txt", "win_path", r"D:\.wor\test.txt"),
    (r"D:\.wor\test.txt", "wsl_path", "/mnt/d/.wor/test.txt"),
    (Path(r"D:\.wor\test.txt"), "wsl_path", "/mnt/d/.wor/test.txt"),
    (Path(r"D:\.wor", "test.txt"), "wsl_path", "/mnt/d/.wor/test.txt"),
    ("/mnt/d/.wor/test.txt", "wsl_path", "/mnt/d/.wor/test.txt"),
    ("/mnt/d/.wor/test.txt", "win_path", r"D:\.wor\test.txt"),
    (Path("/mnt/d/.wor/test.txt"), "win_path", r"D:\.wor\test.txt"),
    (Path("/mnt/d/.wor/", "test.txt"), "win_path", r"D:\.wor\test.txt"),
])
def test_path_conversion(fullpath_in, getter, expected):
    wsl_p = WslPath(fullpath_in)
    assert getattr(wsl_p, getter) == expected


@pytest.mark.parametrize(('fullpath_in', 'add_on', 'getter', 'expected'), [
    (r"D:\.wor", "test.txt", "win_path", r"D:\.wor\test.txt"),
    (r"D:\.wor", "test.txt", "wsl_path", "/mnt/d/.wor/test.txt"),
    ("/mnt/d/.wor", "test.txt", "wsl_path", "/mnt/d/.wor/test.txt"),
    ("/mnt/d/.wor", "test.txt", "win_path", r"D:\.wor\test.txt"),
])
def test_path_copy_and_conversion(fullpath_in, add_on, getter, expected):
    p_start = WslPath(fullpath_in)
    wsl_p = p_start / add_on
    assert getattr(wsl_p, getter) == expected


def test_unsupported_path():
    with pytest.raises(NotImplementedError):
        WslPath("~/wsl_user_folder")
