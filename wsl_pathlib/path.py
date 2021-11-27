# -*coding: utf-8 -*-
"""Extend `pathlib.Path` by addding the properties `wsl_path` and `win_path`.

`wsl_path` and `win_path` each holds respectively the WSL and Windows
representation of the `Path` object.
"""
from os import name as os_name
from pathlib import PosixPath, PurePosixPath, PureWindowsPath, WindowsPath

base = WindowsPath
if os_name == "posix":
    base = PosixPath


def get_drive_letter(path_in, mnt: bool):
    """Return the letter of the windows drive of the path."""
    if mnt:
        return path_in[5].lower()
    return path_in[0].lower()


def is_mnt(path_in: str):
    """Check if the path posix and lives in '/mnt/'."""
    return path_in[:5] == "/mnt/"


def is_nt(path_in: str):
    """Check if the path is a windows path."""
    return path_in[1] == ":"


class WslPath(base):
    """Extend pathlib.Path by addding the properties wsl_path and win_path.

    depending on the plateform base class either pathlib's
    PosixPath or WindowsPath.
    Path objects are instanciated with path representation matching
    the user's OS.
    Both _wsl_path and _win_path properties are lazily converted for their
    getters, the first time they are requested.
    """

    def __new__(cls, *args, **kwargs):
        r"""Correction of the path, to instanciate the version matching the os.

        Crude correction of the path string, in order to instanciate a
        representation of the matching the user's OS.
        ie: we are on wsl and we instanciated WslPath('c:\foo')
        we change the path str to instanciate PosixPath('/mnt/c/foo').
        """
        path_in = str(args[0]).replace("\\", "/")

        if is_mnt(path_in):
            if os_name == "posix":
                crude_path = path_in
            else:
                dl = get_drive_letter(path_in, mnt=True)
                crude_path = f"{dl.upper()}:/{path_in[7:]}"

        elif is_nt(path_in):
            if os_name == "nt":
                crude_path = path_in
            # simply check if path start with "/mnt/" to detect WSL path
            else:
                dl = get_drive_letter(path_in, mnt=False)
                crude_path = f"/mnt/{dl}{path_in[2:]}"
        else:
            raise NotImplementedError(
                "Posix Path not in /mnt/ not yet supported",
            )

        new_args = list(args)
        new_args[0] = crude_path
        args = tuple(new_args)
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
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
        path_in = self.as_posix()
        self._wsl_path = None
        self._win_path = None
        if is_nt(path_in):
            self._win_path = PureWindowsPath(self)
        else:
            self._wsl_path = PurePosixPath(self)
        if self._win_path:
            self.drive_letter = get_drive_letter(
                str(self._win_path),
                mnt=False,
            )
        else:
            self.drive_letter = get_drive_letter(str(self._wsl_path), mnt=True)
