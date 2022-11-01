"""Provide tools for iterables."""

from __future__ import annotations

import itertools
import re

from typing import Final, Hashable, Iterable, Iterator, TypeVar


_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')


def first_last(
        iter_arg: Iterable[_T1],
        default_value: _T1 | None = None) -> tuple[_T1 | None, _T1 | None]:
    """Return the first and last element of an iterable.

    For a single-element iterable, the first and last element are the same.
    For an empty iterable, the first and last element are the `default_value`.

    Args:
        iter_arg: iterable of elements

    Returns:
        tuple of first and last element of the iterable

    Examples:
        >>> first_last([1, 2, 3])
        (1, 3)

        >>> first_last(['hello'])
        ('hello', 'hello')

        >>> first_last([])
        (None, None)
    """
    iterator = iter(iter_arg)
    first = last = next(iterator, default_value)
    for last in iterator:
        pass
    return first, last


def list_to_ranges(input_list: Iterable[int]) -> Iterator[tuple[int, int]]:
    """Return iterable of ranges from iterable of integers.

    Every consecutive sequence of integers in input_list
    is converted to a range represented as a tuple: (first, last).
    The last element of the range is the last element of the sequence
    (not the value after the last element like in range()).
    The function yields those ranges.

    The function groups consecutive numbers. Normally input_list
    should contain only unique and sorted numbers to create
    the optimal (minimal possible) list of ranges.

    Args:
        input_list: iterable of integers (usually unique and sorted)

    Returns:
        iterator of tuples presenting intervals of consecutive numbers

    Examples:
        >>> list(list_to_ranges([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        [(1, 10)]

        >>> list(list_to_ranges([0, 1, 2, 3, 4, 7, 8, 9, 11]))
        [(0, 4), (7, 9), (11, 11)]

        >>> list(list_to_ranges([]))
        []
    """
    # Group items by differences between the values and their indices.
    # Consecutive values are grouped together as they have the same difference.
    for _, indexed_group in itertools.groupby(
            enumerate(input_list),
            lambda index_value: index_value[0] - index_value[1]):
        first_value, last_value = first_last(indexed_group)
        if first_value is not None and last_value is not None:
            # Yield the range which is the first and last value of the group.
            yield first_value[1], last_value[1]


def group_items_by_keys(
        items: Iterable[_T1],
        keys: Iterable[_T2]) -> dict[_T2, list[_T1]]:
    """Return dictionary of lists of items grouped by keys.

    Both input iterables must have the same length or the excessive items
    form the other list are ignored.

    Args:
        items: iterable of items
        keys: iterable of keys

    Returns:
        dictionary of items grouped by keys

    Examples:
        >>> group_items_by_keys(['a', 'b', 'c'], ['x', 'x', 'y'])
        {'x': ['a', 'b'], 'y': ['c']}

        >>> group_items_by_keys([1, 2, 3], ['x', 'x', 'y'])
        {'x': [1, 2], 'y': [3]}
    """
    result: dict[_T2, list[_T1]] = {}
    for key, item in zip(keys, items):
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def iter_len(iterator: Iterable) -> int:
    """Get iterable length. Iterators are consumed.
    
    Infinite iterators cause infinite loop.

    Examples:
        >>> iter_len(())
        0

        >>> iter_len(range(10))
        10
    """
    return sum(1 for _ in iterator)


def are_items_unique(items: Iterable[Hashable]) -> bool:
    """Check if all items of the iterable are unique.

    Examples:
        >>> are_items_unique('ABC')
        True

        >>> are_items_unique('ABAC')
        False
    """
    seen = set()
    # The generator expression uses side-effect on the set seen.
    return not any(
            item in seen or seen.add(item)
            for item in items)


IDENTIFIERS_INVALID_CHARS_RE: Final[str] = r'[^a-zA-Z0-9]'

def unique_identifiers(
        names: Iterable[str], invalid_chars: str = IDENTIFIERS_INVALID_CHARS_RE,
        replacement_char: str = '_') -> list[str]:
    """Create list of valid unique identifiers from a list of names.

    Invalid characters are replaced. Repeated identifiers are given a numeric
    suffix. The returned list contains the identifiers at the same indexes as
    the input iterable.

    Args:
        invalid_chars: regex matching invalid characters to be replaced
        replacement_char: character to be used as replacement

    Examples:
        >>> unique_identifiers(('hello', 'x1_b2'))
        ['hello', 'x1_b2']

        >>> unique_identifiers(('hello', 'x1_b2', 'hello', 'hello'))
        ['hello_1', 'x1_b2', 'hello_2', 'hello_3']

        >>> unique_identifiers(('name@domain', 'name.domain', 'name_domain'))
        ['name_domain_1', 'name_domain_2', 'name_domain_3']

        >>> unique_identifiers(('name@domain', 'name.domain', 'name_domain_1'))
        Traceback (most recent call last):
            ...
        ValueError: Function does not assure uniqueness with pre-existing numeric suffixes.
    """
    identifiers = [re.sub(invalid_chars, replacement_char, name) for name in names]
    identifier_counters = {
            identifier: 1 if iter_len(group) > 1 else 0
            for identifier, group in itertools.groupby(sorted(identifiers))}
    identifiers_unique = []
    for identifier in identifiers:
        suffix = ''
        if identifier_counters[identifier]:
            suffix = f'_{identifier_counters[identifier]}'
            identifier_counters[identifier] += 1
        identifiers_unique.append(identifier + suffix)
    # Currently uniqueness is not assured in all cases. We have to check that.
    if not are_items_unique(identifiers_unique):
        raise ValueError(
            'Function does not assure uniqueness with pre-existing numeric suffixes.')
    return identifiers_unique
