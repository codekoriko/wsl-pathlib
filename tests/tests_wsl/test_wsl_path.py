# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from wsl_pathlib.path import WslPath


@pytest.mark.parametrize(("fullpath_in", "getter", "expected"), [
    (r"C:\foo\test.txt", "win_path", r"C:\foo\test.txt"),
    (r"C:\foo\test.txt", "wsl_path", "/mnt/c/foo/test.txt"),
    (Path(r"C:\foo\test.txt"), "wsl_path", "/mnt/c/foo/test.txt"),
    (Path(r"C:\foo", "test.txt"), "wsl_path", "/mnt/c/foo/test.txt"),
    ("/mnt/c/foo/test.txt", "wsl_path", "/mnt/c/foo/test.txt"),
    ("/mnt/c/foo/test.txt", "win_path", r"C:\foo\test.txt"),
    (Path("/mnt/c/foo/test.txt"), "win_path", r"C:\foo\test.txt"),
    (Path("/mnt/c/foo/", "test.txt"), "win_path", r"C:\foo\test.txt"),
])
def test_path_conversion(fullpath_in, getter, expected):
    wsl_p = WslPath(fullpath_in)
    assert getattr(wsl_p, getter) == expected


@pytest.mark.parametrize(("fullpath_in", "add_on", "getter", "expected"), [
    (r"C:\foo", "test.txt", "win_path", r"C:\foo\test.txt"),
    (r"C:\foo", "test.txt", "wsl_path", "/mnt/c/foo/test.txt"),
    ("/mnt/c/foo", "test.txt", "wsl_path", "/mnt/c/foo/test.txt"),
    ("/mnt/c/foo", "test.txt", "win_path", r"C:\foo\test.txt"),
])
def test_path_copy_and_conversion(fullpath_in, add_on, getter, expected):
    p_start = WslPath(fullpath_in)
    wsl_p = p_start / add_on
    assert getattr(wsl_p, getter) == expected


def test_unsupported_path():
    with pytest.raises(NotImplementedError):
        WslPath("~/wsl_user_folde")
