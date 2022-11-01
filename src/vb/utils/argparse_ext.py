"""Extend standard argparse with some useful features."""

from __future__ import annotations

import argparse


class StoreTrueCondAction(argparse._StoreTrueAction):
    """Custom argparse store_true action making other options (not) required.

    This is a workaround for the fact that argparse does not support
    conditional actions. The action behaves like the `store_true action`, but
    it can make other options (not) required.

    Attributes:
        make_required: List of options that will be changed to required
        make_not_required: List of options that will be changed to not
            required

    Example:
        >>> parser = argparse.ArgumentParser()
        >>> foo = parser.add_argument('--foo', required=True)
        >>> _ = parser.add_argument('--bar', action=StoreTrueCondAction,
        ...                     make_not_required=[foo])
        >>> args = parser.parse_args(['--bar'])
        >>> args == argparse.Namespace(foo=None, bar=True)
        True

        >>> parser = argparse.ArgumentParser()
        >>> foo = parser.add_argument('--foo', required=True)
        >>> _ = parser.add_argument('--bar', action='store_true')
        >>> parser.parse_args(['--bar'])
        Traceback (most recent call last):
          ...
        SystemExit: 2
    """

    # parser.register('action', 'store_true_cond', StoreTrueCondAction)

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        """Initialize the action object.

        The arguments are the same as for the `store_true` action with two
        optional arguments: `make_required` and `make_not_required`.
        The arguments are passed from the ArgumentParser.add_argument()
        method arguments.

        `make_required` and `make_not_required` are list of options
        represented by Action objects returned by the
        ArgumentParser.add_argument() method. Keep the returned objects
        to add them to the list(s).

        Args:
            option_strings: Option name strings
            dest: Destination variable
            nargs: Number of arguments
            make_required: List of options that will be changed to required
            make_not_required: List of options that will be changed to not
                required
        """
        _make_required = kwargs.pop('make_required', [])
        _make_not_required = kwargs.pop('make_not_required', [])
        super().__init__(option_strings, dest, **kwargs)
        self.make_required = _make_required
        self.make_not_required = _make_not_required

    def __call__(self, parser, namespace, values, option_string=None):
        """Execute the action."""
        for required in self.make_required:
            required.required = True
        for not_required in self.make_not_required:
            not_required.required = False
        try:
            return super().__call__(parser, namespace, values, option_string)
        except NotImplementedError:
            pass


def add_common_arguments(
        parser: argparse.ArgumentParser, version: str | None = None,
        verbose: bool = True) -> None:
    """Add common CLI arguments.

    Added arguments: `-V`, `--version`, `-v`, `--verbose`.

    Args:
        parser: Argument parser to add arguments to
        version: Program version string - must be set to add
            `-V` and `--version`.
        verbose: Add verbose argument
    """
    if verbose:
        parser.add_argument(
            '-v', '--verbose', action='count', default=0,
            help='increase output verbosity, can be repeated')
    if version:
        parser.add_argument(
            '-V', '--version', action='version', version=f'%(prog)s {version}')
