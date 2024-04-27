"""Extend standard re module with some useful features."""

from __future__ import annotations

import re
from typing import Iterable


def first_fullmatch(
        patterns: Iterable[re.Pattern[str] | str], string: str) -> re.Match[str] | None:
    """Return the first fullmatch of a string.

    Args:
        string: string to match
        regexes: list of compiled regular expressions

    Returns:
        The first fullmatch of the string or None if no match is found.

    Examples:
        >>> first_fullmatch('foo', [re.compile('foo'), re.compile('bar')])
        <re.Match object; span=(0, 3), match='foo'>

        >>> first_fullmatch('baz', [re.compile('bar'), re.compile('foo')])
    """
    for pattern in patterns:
        if match := re.fullmatch(pattern, string):
            return match
    return None
