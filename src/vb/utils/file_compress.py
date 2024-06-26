"""Provide tools for working with compressed files."""

from __future__ import annotations

import contextlib
import errno
import gzip
import os
import pathlib
import shutil
import tempfile
import warnings
from types import TracebackType
from typing import Type

from . import ppr


COMPRESSION_SUFFIXES = {
        '.gz': 'gzip',
        '.zip': 'zip',
        '.bz2': 'bzip2',
        '.xz': 'xz',
        '.lzma': 'lzma',
        }
"""Mapping of compression file suffixes to their types."""


# pylint: disable=too-many-instance-attributes  # We support similar arguments as tempfile.mkstemp.
class TemporaryDecompressedFile(contextlib.AbstractContextManager):
    """A context manager for creating a temporarily decompressed file.

    In `__enter__()` the given file is decompressed to a temporary file
    whose path is returned. The temporary file is deleted in `__exit__()`.

    Note:
        Currently the spinner shows only its first phase to indicate
        that the decompression is in progress.
        The function `shutil.copyfileobj()` used during the decompression
        does not have a callback function to update a spinner.

    Todo:
        * Check if support for text mode works and if we should keep it.
        * Check if decompression progress callback can be implemented
            reasonably.
    """
    compressed_path: str | pathlib.Path
    """The path to the compressed file."""
    suffix: str | None
    """The suffix of the temporary decompressed file."""
    prefix: str | None
    """The prefix of the temporary decompressed file."""
    dir: str | None
    """The directory of the temporary decompressed file."""
    pass_unknown_compression_type: bool
    """If `True`, the of unknown compression is passed directly."""
    compression_type: str | None
    """The type of compression."""
    spinner: ppr.Spinner | None
    """The spinner instance to show that decompression is in progress."""
    decompressed_path: str | None

    # pylint: disable=too-many-arguments    # We support similar arguments as tempfile.mkstemp().
    def __init__(
            self, compressed_path: str | pathlib.Path,
            compression_type_from_suffix: bool = True,
            pass_unknown_compression_type: bool = True,
            spinner: ppr.Spinner | None = None,
            suffix: str | None = None,
            prefix: str | None = None, dir_=None):
        """Initialize the decompressed context manager.

        Args:
            compressed_path: The path to the compressed file.
            compression_type_from_suffix: If `True`, the compression type
                is determined from the file name suffix.
            pass_unknown_compression_type: If `True`, the of unknown
                compression is passed directly (its path is returned as is).
            spinner: The spinner instance to show that decompression is
                in progress.
            suffix: The suffix of the temporary decompressed file.
            prefix: The prefix of the temporary decompressed file.
            dir_: The directory of the temporary decompressed file.
        """
        self.compressed_path = compressed_path
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir_
        self.pass_unknown_compression_type = pass_unknown_compression_type
        self.compression_type = None
        self.spinner = spinner
        self.decompressed_path = None
        if compression_type_from_suffix:
            self.compression_type = COMPRESSION_SUFFIXES.get(pathlib.Path(compressed_path).suffix)

    def __enter__(self):
        """Enter the context manager."""
        if (
                self.compression_type is None
                and self.pass_unknown_compression_type):
            return self.compressed_path
        decompressed_fd, self.decompressed_path = tempfile.mkstemp(
                suffix=self.suffix, prefix=self.prefix, dir=self.dir, text=False)
        with contextlib.ExitStack() as stack:
            decompressed_file = stack.enter_context(
                    os.fdopen(decompressed_fd, 'wb'))
            if self.compression_type == 'gzip':
                onfly_decompressed_file = stack.enter_context(
                        gzip.open(self.compressed_path, 'rb'))
            else:
                raise ValueError(
                        f'Unsupported compression type: '
                        f'{self.compression_type}')
            if self.spinner is not None:
                stack.enter_context(self.spinner)
            shutil.copyfileobj(onfly_decompressed_file, decompressed_file)
            # The copied files must be opened in binary mode.
        try:
            os.close(decompressed_fd)
        except OSError as os_err:       # file descriptor is normally closed
            if os_err.args[0] != errno.EBADF:   # so do not raise if closed
                raise
        return self.decompressed_path

    def __exit__(
                self, __exc_type: Type[BaseException] | None,
                __exc_value: BaseException | None,
                __traceback: TracebackType | None) -> None:
        """Exit the context manager."""
        del __exc_type, __exc_value, __traceback
        if self.decompressed_path is not None:
            try:
                os.remove(self.decompressed_path)
            except OSError as os_err:
                warnings.warn(
                    f'Failed to remove temporary file '
                    f'{self.decompressed_path!r}: {os_err}')
