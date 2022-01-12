"""Provide tools for iterables."""

from __future__ import annotations

import itertools

from typing import Iterable, TypeVar


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


def list_to_ranges(input_list: Iterable[int]) -> Iterable[tuple[int, int]]:
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
        iterable of tuples presenting intervals of consecutive numbers

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
