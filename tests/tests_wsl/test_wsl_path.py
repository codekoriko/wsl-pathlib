from pathlib import Path

import pytest

from wsl_pathlib.path import WslPath


@pytest.mark.parametrize(('fullpath_in', 'getter', 'expected'), [
    (r'C:\foo\test.txt', 'win_path', r'C:\foo\test.txt'),
    (r'C:\foo\test.txt', 'wsl_path', '/mnt/c/foo/test.txt'),
    (Path(r'C:\foo\test.txt'), 'wsl_path', '/mnt/c/foo/test.txt'),
    (Path(r'C:\foo', 'test.txt'), 'wsl_path', '/mnt/c/foo/test.txt'),
    ('/mnt/c/foo/test.txt', 'wsl_path', '/mnt/c/foo/test.txt'),
    ('/mnt/c/foo/test.txt', 'win_path', r'C:\foo\test.txt'),
    (Path('/mnt/c/foo/test.txt'), 'win_path', r'C:\foo\test.txt'),
    (Path('/mnt/c/foo/', 'test.txt'), 'win_path', r'C:\foo\test.txt'),
])
def test_path_conversion(
    fullpath_in: str,
    getter: str,
    expected: str,
) -> None:
    """Test conversion between Windows and WSL path formats.

    Args:
        fullpath_in: Input path (string or Path object)
        getter: Property name to access ('win_path' or 'wsl_path')
        expected: Expected output path string
    """
    wsl_p = WslPath(fullpath_in)
    assert getattr(wsl_p, getter) == expected


@pytest.mark.parametrize(('fullpath_in', 'add_on', 'getter', 'expected'), [
    (r'C:\foo', 'test.txt', 'win_path', r'C:\foo\test.txt'),
    (r'C:\foo', 'test.txt', 'wsl_path', '/mnt/c/foo/test.txt'),
    ('/mnt/c/foo', 'test.txt', 'wsl_path', '/mnt/c/foo/test.txt'),
    ('/mnt/c/foo', 'test.txt', 'win_path', r'C:\foo\test.txt'),
])
def test_path_copy_and_conversion(
    fullpath_in: str,
    add_on: str,
    getter: str,
    expected: str,
) -> None:
    """Test path joining and conversion operations.

    Args:
        fullpath_in: Base path (string or Path object)
        add_on: Path component to join
        getter: Property name to access ('win_path' or 'wsl_path')
        expected: Expected output path string after joining
    """
    p_start = WslPath(fullpath_in)
    wsl_p = p_start / add_on
    path_retrieved = getattr(wsl_p, getter)
    assert path_retrieved == expected


def test_unsupported_path() -> None:
    """Test that unsupported path formats raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        WslPath('~/wsl_user_folde')
