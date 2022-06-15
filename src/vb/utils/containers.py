"""Provide tools for containers."""

from __future__ import annotations


def dict_update_missing(target_dict: dict, source_dict: dict) -> None:
    """Update target_dict with missing keys and values from source_dict.

    The function updates target_dict with missing keys and values
    from source_dict. If a key is missing in the target_dict,
    it is added with the corresponding value from the source_dict.

    Args:
        target_dict: dictionary to update
        source_dict: dictionary to update from

    Examples:
        >>> target_dict = {'a': 1, 'b': 2}
        >>> source_dict = {'a': 10, 'c': 3}
        >>> dict_update_missing(target_dict, source_dict)
        >>> target_dict
        {'a': 1, 'b': 2, 'c': 3}
    """
    for key, value in source_dict.items():
        if key not in target_dict:
            target_dict[key] = value
