from __future__ import annotations

from os import name as os_name
from pathlib import PosixPath, PurePosixPath, PureWindowsPath, WindowsPath
from typing import Any, TypeAlias

BASE_PATH = WindowsPath if os_name == 'nt' else PosixPath

BasePath: TypeAlias = WindowsPath | PosixPath


class WslPath(BASE_PATH):
    r"""A pathlib-compatible class for handling WSL and Win path conversions.

    This class extends the platform-appropriate Path class and provides
    seamless conversion between Windows drive paths (C:\path) and WSL
    mount paths (/mnt/c/path).
    """

    _wsl_path: PurePosixPath | None
    _win_path: PureWindowsPath | None
    drive_letter: str  # always lower-case

    # ----------------- helper utilities (private) -----------------

    @staticmethod
    def _safe_char(s: str, idx: int) -> str | None:
        """Safely get character at index, returning None if out of bounds."""
        return s[idx] if 0 <= idx < len(s) else None

    @staticmethod
    def _is_mnt_path(path_in: str) -> bool:
        """Check if path is a WSL mount path like /mnt/c/..."""
        if not path_in.startswith('/mnt/'):
            return False
        parts = path_in.split('/', 4)
        return len(parts) >= 3 and len(parts[2]) == 1 and parts[2].isalpha()

    @staticmethod
    def _is_win_drive_path(path_in: str) -> bool:
        r"""Check if path is a Windows drive path like C:\..."""
        if len(path_in) < 2:
            return False
        return path_in[0].isalpha() and path_in[1] == ':'

    @staticmethod
    def _get_drive_letter(path_in: str, *, is_mnt: bool) -> str:
        """Extract drive letter from path.

        Args:
            path_in: The input path string
            is_mnt: Whether this is a /mnt/ style path (keyword-only)

        Returns:
            The drive letter in lowercase

        Raises:
            ValueError: If drive letter cannot be derived
        """
        if is_mnt:
            parts = path_in.split('/', 4)
            if len(parts) >= 3 and len(parts[2]) == 1 and parts[2].isalpha():
                return parts[2].lower()
            raise ValueError('Invalid /mnt/ path: cannot derive drive letter.')
        if WslPath._is_win_drive_path(path_in):
            return path_in[0].lower()
        raise ValueError('Invalid Windows path: cannot derive drive letter.')

    # ----------------- core construction & init -------------------

    def __new__(cls, *args: Any, **kwargs: Any) -> WslPath:
        """Create new WslPath instance with normalized path."""
        if not args:
            raise TypeError('WslPath requires a path argument.')
        raw_str = str(args[0]).replace('\\', '/')

        if cls._is_mnt_path(raw_str):
            if os_name == 'posix':
                normalized = raw_str
            else:
                dl = cls._get_drive_letter(raw_str, is_mnt=True)
                # '/mnt/<d>/' -> start at 7
                normalized = f'{dl.upper()}:{raw_str[7:]}'
        elif cls._is_win_drive_path(raw_str):
            if os_name == 'nt':
                normalized = raw_str
            else:
                dl = cls._get_drive_letter(raw_str, is_mnt=False)
                normalized = f'/mnt/{dl}{raw_str[2:]}'
        else:
            raise NotImplementedError(
                'Unsupported path. Only drive-letter Windows paths '
                "and '/mnt/<drive>/' WSL paths are supported."
            )
        new_args = list(args)
        new_args[0] = normalized
        instance = super().__new__(cls, *tuple(new_args), **kwargs)

        # Initialize the instance attr here since __init__ may not be called
        instance._wsl_path = None
        instance._win_path = None
        instance._init_views()

        return instance

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize WslPath instance."""
        super().__init__()  # pathlib no-op
        # Only initialize if not already done in __new__
        if not hasattr(self, '_wsl_path'):
            self._init_views()

    # ----------------- public properties -------------------------

    @property
    def wsl_path(self) -> str:
        """Get the WSL mount path representation (e.g., /mnt/c/path)."""
        if getattr(self, '_wsl_path', None) is None:
            if getattr(self, '_win_path', None) is None:
                self._ensure_views_from_self()
            # If ensure gave us a WSL view, just use it.
            if getattr(self, '_wsl_path', None) is not None:
                return str(self._wsl_path)
            # Otherwise we must have a Windows view to derive from.
            win_path = getattr(self, '_win_path', None)
            if win_path is None:
                raise RuntimeError('Failed to initialize Windows path view')
            rel_parts = list(win_path.parts[1:])  # drop 'C:\\'
            self._wsl_path = PurePosixPath(
                '/mnt', self.drive_letter, *rel_parts
            )
        return str(self._wsl_path)

    @property
    def win_path(self) -> str:
        r"""Get the Windows path representation (e.g., C:\path)."""
        if getattr(self, '_win_path', None) is None:
            if getattr(self, '_wsl_path', None) is None:
                self._ensure_views_from_self()
            # If ensure gave us a Windows view, just use it.
            if getattr(self, '_win_path', None) is not None:
                return str(self._win_path)
            # Otherwise we must have a WSL view to derive from.
            wsl_path = getattr(self, '_wsl_path', None)
            if wsl_path is None:
                raise RuntimeError('Failed to initialize WSL path view')
            parts = wsl_path.parts
            if len(parts) < 3 or parts[1] != 'mnt':
                raise NotImplementedError(
                    'Cannot convert POSIX path not under '
                    "'/mnt/<drive>/' to Windows."
                )
            rel_after_drive = parts[3:]
            self._win_path = PureWindowsPath(
                f'{self.drive_letter.upper()}:\\', *rel_after_drive
            )
        return str(self._win_path)

    # ----------------- internals ---------------------------------

    def _init_views(self) -> None:
        """Initialize internal path views based on current path."""
        self._wsl_path = None
        self._win_path = None
        current = self.as_posix()

        if self._is_win_drive_path(current):
            self._win_path = PureWindowsPath(current)
            self.drive_letter = self._get_drive_letter(
                current, is_mnt=False
            )
        elif self._is_mnt_path(current):
            self._wsl_path = PurePosixPath(current)
            self.drive_letter = self._get_drive_letter(current, is_mnt=True)
        else:
            raise NotImplementedError(
                "Only '/mnt/<drive>/' and 'X:/' drive paths are supported."
            )

    def _ensure_views_from_self(self) -> None:
        """Ensure internal views are populated from current path state."""
        posix_view = self.as_posix()

        # Be resilient if attributes were never set on this instance
        if not hasattr(self, '_wsl_path'):
            self._wsl_path = None
        if not hasattr(self, '_win_path'):
            self._win_path = None
        if not hasattr(self, 'drive_letter'):
            self.drive_letter = ''

        if self._is_win_drive_path(posix_view):
            self._win_path = PureWindowsPath(posix_view)
            self.drive_letter = self._get_drive_letter(
                posix_view, is_mnt=False
            )
        elif self._is_mnt_path(posix_view):
            self._wsl_path = PurePosixPath(posix_view)
            self.drive_letter = self._get_drive_letter(
                posix_view, is_mnt=True
            )
        else:
            raise NotImplementedError(
                'Cannot derive views from an unsupported path.'
            )


def to_wsl(path_like: str | BasePath) -> str:
    """Convert a Windows or WSL path to WSL mount path format.

    Args:
        path_like: Path to convert (string or Path object)

    Returns:
        WSL mount path string (e.g., '/mnt/c/path')
    """
    return WslPath(str(path_like)).wsl_path


def to_windows(path_like: str | BasePath) -> str:
    r"""Convert a Windows or WSL path to Windows path format.

    Args:
        path_like: Path to convert (string or Path object)

    Returns:
        Windows path string (e.g., 'C:\\path')
    """
    return WslPath(str(path_like)).win_path
