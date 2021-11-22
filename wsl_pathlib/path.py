# -*coding: utf-8 -*-
"""Extend `pathlib.Path` by addding the properties `wsl_path` and `win_path`.

`wsl_path` and `win_path` each holds respectively the WSL and Windows
representation of the `Path` object.
"""
import os
from pathlib import PosixPath, PurePosixPath, PureWindowsPath, WindowsPath

if os.name == "posix":
    base = PosixPath
else:
    base = WindowsPath


class WslPath(base):
    """Extend pathlib.Path by addding the properties wsl_path and win_path.

    depending on the plateform base class either pathlib's
    PosixPath or WindowsPath.
    Both _wsl_path and _win_path properties are lazily converted for their
    getters, the first time they are requested.

    """

    def __init__(self, fullpath_in: str):
        """Initialize WslPath properties after base init."""
        super().__init__()
        self._init_wsl_path()

    @property
    def wsl_path(self) -> str:
        """Initialise WslPath properties and return lazy loaded value.

        If the Path object had been created by other mean than a direct
        instanciation, ie: p2 = p1 / "add_on", then initialize the WslPath
        properties now.
        Then builds WindowsPath the win_path if it was not yet being build.
        Then returns the string representation of it.

        """
        try:
            self.drive_letter
        except AttributeError:
            self._init_wsl_path()
        if not self._wsl_path:
            rel_parts = list(self._win_path.parts[1:])
            rel_parts.insert(0, f"/mnt/{self.drive_letter}")
            self._wsl_path = PurePosixPath(*rel_parts)
        return str(self._wsl_path)

    @property
    def win_path(self) -> str:
        """Initialise WslPath properties and return lazy loaded value.

        If the Path object had been created by other mean than a direct
        instanciation, ie: p2 = p1 / "add_on", then initializes the WslPath
        properties now.
        Then builds wsl_path if it was not yet being build.
        Then returns the string representation of it.

        """
        try:
            self.drive_letter
        except AttributeError:
            self._init_wsl_path()
        if not self._win_path:
            rel_parts = list(self._wsl_path.parts[3:])
            rel_parts.insert(0, f"{self.drive_letter.upper()}:\\")
            self._win_path = PureWindowsPath(*rel_parts)
        return str(self._win_path)

    def _init_wsl_path(self) -> None:
        """Idying input path platform and getting the drive letter.

        Detects the input path as Unix or Win and save it to either _wsl_path
        or _win_path. Then determine the drive letter that gonna be used during
        the lazy load.

        _wsl_path: properties that holds a PurePosixPath object
        containing the windows reprensetation of the path.
        _win_path: properties that holds a PureWindowsPath object containing
        the windows reprensetation of the path.
        _self.drive_letter: contains the letter of the windows drive.

        """
        path_in = str(self)
        self._wsl_path = None
        self._win_path = None
        # simply check 2nd char for ":" to detect win path
        if path_in[1] == ":":
            self._win_path = PureWindowsPath(self)
        # simply check if path start with "/mnt/" to detect WSL path
        elif path_in[:5] == "/mnt/":
            self._wsl_path = PurePosixPath(self)
        else:
            raise NotImplementedError("Path not in /mnt/ not yet supported")
        if self._win_path:
            self.drive_letter = str(self._win_path)[0].lower()
        else:
            self.drive_letter = str(self._wsl_path)[5].lower()
