# -*- coding: utf-8 -*-
import os
from pathlib import PosixPath, PurePosixPath, PureWindowsPath, WindowsPath

if os.name == "posix":
    base = PosixPath
else:
    base = WindowsPath


class WslPath(base):
    """
    - depending on plateform executed extend pathlib's PosixPath or WindowsPath
    - adds attributes _wsl_path and _win_path
    - the getters of those lazily convert the path
    the first time we request the path for the opposite platform
    """
    def __init__(self, fullpath_in: str):
        super().__init__()
        self._init_wsl_path()

    def _init_wsl_path(self):
        path_in = str(self)
        self._wsl_path = None
        self._win_path = None
        # simply check 2nd char for ":" and 1st for "/"
        # to categorise the plateform
        if path_in[1] == ":":
            self._win_path = PureWindowsPath(self)
        elif path_in[0:5] == "/mnt/":
            self._wsl_path = PurePosixPath(self)
        else:
            raise NotImplementedError("Path not in /mnt/ not yet supported")
        if self._win_path:
            self.drive_letter = str(self._win_path)[0].lower()
        else:
            self.drive_letter = str(self._wsl_path)[5].lower()

    @property
    def wsl_path(self):
        try:
            getattr(self, "drive_letter")
        except AttributeError:
            self._init_wsl_path()
        if not self._wsl_path:
            rel_parts = list(self._win_path.parts[1:])
            rel_parts.insert(0, f"/mnt/{self.drive_letter}")
            self._wsl_path = PurePosixPath(*rel_parts)
        return str(self._wsl_path)

    @property
    def win_path(self):
        try:
            getattr(self, "drive_letter")
        except AttributeError:
            self._init_wsl_path()
        if not self._win_path:
            rel_parts = list(self._wsl_path.parts[3:])
            rel_parts.insert(0, f"{self.drive_letter.upper()}:\\")
            self._win_path = PureWindowsPath(*rel_parts)
        return str(self._win_path)
