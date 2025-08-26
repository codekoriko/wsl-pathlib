from __future__ import annotations

import logging
from os import name as os_name
from pathlib import PosixPath, PurePosixPath, PureWindowsPath, WindowsPath
from typing import Any, TypeAlias

# Fix: Use proper type alias and Union for base class
BasePath: TypeAlias = WindowsPath | PosixPath
_BASE_PATH_TYPE = WindowsPath if os_name == 'nt' else PosixPath


class WslPath(_BASE_PATH_TYPE):
    r"""A pathlib-compatible class for handling WSL and Win path conversions.

    This class extends the platform-appropriate Path class and provides
    seamless conversion between Windows drive paths (C:\\path) and WSL
    mount paths (/mnt/c/path).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize WslPath instance."""
        if not args:
            raise TypeError('WslPath requires a path argument.')

        self.logger = logging.getLogger(__name__)
        raw_str = str(args[0]).replace('\\', '/')
        normalized = self._normalize_path(raw_str)

        # Create the parent with normalized path
        new_args = (normalized, *args[1:])
        super().__init__(*new_args[1:], **kwargs)

        # Initialize instance attributes
        self._ensure_attributes()

    def _ensure_attributes(self) -> None:
        """Ensure all instance attributes are initialized."""
        if not hasattr(self, '_wsl_path'):
            self._wsl_path: PurePosixPath | None = None
        if not hasattr(self, '_win_path'):
            self._win_path: PureWindowsPath | None = None
        if not hasattr(self, 'drive_letter'):
            self.drive_letter = ''
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)

        # Initialize views if not already done
        if not self.drive_letter:
            self._init_views()

    def _make_child_relpath(self, name: str) -> WslPath:
        """Create a child path (used by pathlib internally)."""
        # This method is called by pathlib when using / operator
        child = super()._make_child_relpath(name)
        # Ensure the child is a WslPath with proper attributes
        if not isinstance(child, WslPath):
            child = WslPath(str(child))
        else:
            child._ensure_attributes()
        return child

    def __truediv__(self, other: str | Any) -> WslPath:
        """Override / operator to ensure proper WslPath creation."""
        result = super().__truediv__(other)
        if not isinstance(result, WslPath):
            result = WslPath(str(result))
        else:
            result._ensure_attributes()
        return result

    def _normalize_path(self, raw_str: str) -> str:
        """Normalize path based on platform and path type."""
        if self._is_mnt_path(raw_str):
            if os_name == 'posix':
                return raw_str
            drive_letter = self._get_drive_letter(raw_str, is_mnt=True)
            return f'{drive_letter.upper()}:{raw_str[7:]}'

        if self._is_win_drive_path(raw_str):
            if os_name == 'nt':
                return raw_str
            drive_letter = self._get_drive_letter(raw_str, is_mnt=False)
            return f'/mnt/{drive_letter}{raw_str[2:]}'

        error_msg = (
            'Unsupported path. Only drive-letter Windows paths '
            + "and '/mnt/<drive>/' WSL paths are supported."
        )
        raise NotImplementedError(error_msg)

    def _is_mnt_path(self, path_in: str) -> bool:
        """Check if path is a WSL mount path like /mnt/c/..."""
        if not path_in.startswith('/mnt/'):
            return False

        parts = path_in.split('/', 4)
        if len(parts) < 3:
            return False

        drive_part = parts[2]
        return len(drive_part) == 1 and drive_part.isalpha()

    def _is_win_drive_path(self, path_in: str) -> bool:
        r"""Check if path is a Windows drive path like C:\\..."""
        if len(path_in) < 2:
            return False
        return path_in[0].isalpha() and path_in[1] == ':'

    def _get_drive_letter(self, path_in: str, *, is_mnt: bool) -> str:
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
            if len(parts) >= 3:
                drive_part = parts[2]
                if len(drive_part) == 1 and drive_part.isalpha():
                    return drive_part.lower()
            raise ValueError('Invalid /mnt/ path: cannot derive drive letter.')

        if self._is_win_drive_path(path_in):
            return path_in[0].lower()
        raise ValueError('Invalid Windows path: cannot derive drive letter.')

    @property
    def wsl_path(self) -> str:
        """Get the WSL mount path representation (e.g., /mnt/c/path)."""
        self._ensure_attributes()

        if self._wsl_path is None:
            self._ensure_wsl_view()

        if self._wsl_path is None:
            raise RuntimeError('Failed to initialize WSL path view')

        return str(self._wsl_path)

    @property
    def win_path(self) -> str:
        r"""Get the Windows path representation (e.g., C:\\path)."""
        self._ensure_attributes()

        if self._win_path is None:
            self._ensure_win_view()

        if self._win_path is None:
            raise RuntimeError('Failed to initialize Windows path view')

        return str(self._win_path)

    def _init_views(self) -> None:
        """Initialize internal path views based on current path."""
        self._wsl_path = None
        self._win_path = None
        current = self.as_posix()

        if self._is_win_drive_path(current):
            self._win_path = PureWindowsPath(current)
            self.drive_letter = self._get_drive_letter(current, is_mnt=False)
        elif self._is_mnt_path(current):
            self._wsl_path = PurePosixPath(current)
            self.drive_letter = self._get_drive_letter(current, is_mnt=True)
        else:
            error_msg = (
                'Only \'/mnt/<drive>/\' and \'X:/\' drive paths are supported.'
            )
            raise NotImplementedError(error_msg)

    def _ensure_wsl_view(self) -> None:
        """Ensure WSL view is populated."""
        if self._wsl_path is not None:
            return

        if self._win_path is None:
            self._ensure_views_from_self()

        if self._win_path is not None:
            rel_parts = list(self._win_path.parts[1:])  # drop 'C:\\'
            self._wsl_path = PurePosixPath(
                '/mnt',
                self.drive_letter,
                *rel_parts,
            )

    def _ensure_win_view(self) -> None:
        """Ensure Windows view is populated."""
        if self._win_path is not None:
            return

        if self._wsl_path is None:
            self._ensure_views_from_self()

        if self._wsl_path is not None:
            parts = self._wsl_path.parts
            if len(parts) < 3 or parts[1] != 'mnt':
                error_msg = (
                    'Cannot convert POSIX path not under '
                    + "'/mnt/<drive>/' to Windows."
                )
                raise NotImplementedError(error_msg)

            rel_after_drive = parts[3:]
            drive_root = f'{self.drive_letter.upper()}:\\'
            self._win_path = PureWindowsPath(drive_root, *rel_after_drive)

    def _ensure_views_from_self(self) -> None:
        """Ensure internal views are populated from current path state."""
        posix_view = self.as_posix()

        try:
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
        except Exception:
            self.logger.exception('Failed to ensure views from path: %s')
            raise


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
        Windows path string (e.g., 'C:\\\\path')
    """
    return WslPath(str(path_like)).win_path
