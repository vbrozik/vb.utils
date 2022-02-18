"""Provide pretty text output."""

from __future__ import annotations

import shutil
import os
import pprint
import math
import sys

from typing import Optional, Sequence, TypeVar, Iterator, TextIO, Type
from types import TracebackType


_T1 = TypeVar('_T1')


# --- classes:

class Spinner:
    r"""Provide animated text spinner to indicate an ongoing operation.

    The spinner is a sequence of characters or strings being repeatedly
    printed to the stream to create the animation. Initialize the spinner
    using the constructor. The terminal writting position should be at the
    beginning of a line. Then call the update method every time the
    animation should advance (e.g. in a callback function). Finally,
    call the cleanup method to clean up the spinner (overwrite it by spaces).

    The cleanup method does not destroy the spinner object. You can
    use the update method again to start a new spinner.

    The spinner can be used as a context manager. By default the update method
    is called when entering the context manager to show the spinner
    and the cleanup method is called when exiting the context manager
    to clear it.

    Note:
        The spinner works only at the beginning of a line because it uses
        carriage return to move to the beginning of the line and overwrite
        itself at the next iteration.

    Examples:
        >>> spinner = Spinner()
        >>> next(spinner.iterator)
        '|\r'
        >>> next(spinner.iterator)
        '/\r'
        >>> next(spinner.iterator)
        '-\r'
    """

    ASCII_LINE1 = '|/-\\'
    UNICODE_DOTS1 = '⠁⠂⠄⡀⢀⠠⠐⠈'

    def __init__(
            self, sequence: str | Sequence[str] | None = None,
            suppress_nontty: bool = True,
            stream: TextIO = sys.stdout, reset_str: str = '\r',
            cm_update_enter: bool = True) -> None:
        """Initialize the spinner.

        Args:
            sequence: the sequence of characters or strings to cycle
                through. If None, the ASCII_LINE1 sequence is used.
            suppress_nontty: if True, suppress the spinner if the
                stream is not a tty.
            stream: the stream to write the spinner to
            reset_str: the string to append to the end of every cycle
                It resets the cursor to overwrite the spinner on next update.
            cm_update_enter: if True, update the spinner when entering
                as the context manager

        Todo:
            * spinners to add:
            https://github.com/manrajgrover/py-spinners/blob/master/spinners/spinners.py
            https://stackoverflow.com/questions/1923323/console-animations
            https://stackoverflow.com/questions/2685435/cooler-ascii-spinners
        """
        if sequence is None:
            sequence = self.ASCII_LINE1
        self.sequence = sequence
        self.spinner_length = max(len(text) for text in sequence)
        self.suppress = suppress_nontty and not stream.isatty()
        self.stream = stream
        self.reset_str = reset_str
        self.cm_update_enter = cm_update_enter
        self.iterator = self.get_iterator()

    def __enter__(self) -> Spinner:
        """Enter the context manager."""
        if self.cm_update_enter:
            self.update()
        return self

    def __exit__(
                self, __exc_type: Type[BaseException] | None,
                __exc_value: BaseException | None,
                __traceback: TracebackType | None) -> None:
        """Exit the context manager."""
        self.cleanup()

    def get_iterator(self) -> Iterator[str]:
        """Create an iterator to cycle through the sequence."""
        while True:
            for text in self.sequence:
                yield text + self.reset_str

    def update(self) -> None:
        """Write the next spinner character to the stream."""
        if not self.suppress:
            self.stream.write(next(self.iterator))

    def cleanup(self) -> None:
        """Cleanup the spinner."""
        if not self.suppress:
            self.stream.write(' ' * self.spinner_length + self.reset_str)


# --- functions (and module variables):

_terminal_size: Optional[os.terminal_size] = None


def get_terminal_size(force: bool = False) -> os.terminal_size:
    """Get output terminal size.

    Store the terminal size to the module's variable and return it.

    Args:
        force: force retrieving the terminal size even when set already
    """
    global _terminal_size

    if not _terminal_size or force:
        _terminal_size = shutil.get_terminal_size()
    return _terminal_size


def progress(
        value: float, max_value: float,
        num_digits: Optional[int] = None) -> str:
    """Show textual representation of progress of value.

    The non-negative value is should increase from 0 (0 %)
    to max_value. (100 %)

    Args:
        value: current value to measure the progress of
        max_value: the maximum for the value, zero means undefined
        num_digits: optional maximum number of digits override for the value

    Returns:
        formatted string showing the progress of the value

    Examples:
        >>> progress(1, 10)
        ' 1/10   10 %'

        >>> progress(5, 0)
        '5/0  --- %'

    TODO:
        * time estimation
        * user-defined format
        * progress-bar
    """
    percent_str = '---'
    if round(max_value) > 0:                # we have a max value
        max_value = max(max_value, 1)       # has to be a positive integer
        percent_str = f'{round(100 * value / max_value):>3d}'
    max_str = f'{round(max_value):d}'
    if num_digits is None:
        num_digits = len(max_str)           # the maximum value string length
    return f'{round(value):>{num_digits}d}/{max_str}  {percent_str} %'


def pformat(obj: object, color: bool = True) -> str:
    """Format object for better human readable printing.

    If color is set and the pygments module is available make the output
    in color.

    Args:
        obj: object to format to string
        color: colorize the output if set to True

    Examples:
        >>> pformat(1, False)
        '1'

        >>> pformat({'count': 2, 'items': [4, 5]}, False)
        "{'count': 2, 'items': [4, 5]}"
    """
    formated = pprint.pformat(obj)
    if color:
        try:
            from pygments import highlight
            from pygments.lexers.python import PythonLexer
            lexer = PythonLexer()
            from pygments.formatters.terminal256 import Terminal256Formatter
            formatter = Terminal256Formatter()
        except ImportError:
            return formated
        formated = highlight(formated, lexer, formatter)
    return formated


def interval_str(
        interval_tuple: Sequence[float], separator: str = '–',
        print_int_length: bool = False, format_spec: str = '') -> str:
    """Return a string representation of a numeric interval.

    Args:
        interval_tuple: a tuple of two numbers, the start and end of the
            interval
        separator: the separator between the start and end of the interval
            (default is en-dash)
        print_int_length: print the length of the interval as the count
            of integers in it
        format_spec: the format specification for the numbers

    Returns:
        string representation of the interval

    Examples:
        >>> interval_str((1, 2))
        '1–2'

        >>> interval_str((3, 3), format_spec='.2f')
        '3.00'

        >>> interval_str((1, 1.5))
        '1–1.5'
    """
    if not 1 <= len(interval_tuple) <= 2:
        raise ValueError('interval_tuple must have length 1 or 2')
    result = f'{interval_tuple[0]:{format_spec}}'
    int_length = 1
    if (
            len(interval_tuple) > 1 and
            not math.isclose(interval_tuple[0], interval_tuple[1])):
        result = f'{result}{separator}{interval_tuple[1]:{format_spec}}'
        int_length = int(interval_tuple[1] - interval_tuple[0] + 1)
    if print_int_length:
        result = f'{result} ({int_length})'
    return result
