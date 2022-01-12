#!/bin/sh

PYTHON=python3

if test "$1" = "editable" ; then
    # "$PYTHON" -m pip install --no-use-pep517 -e .
    "$PYTHON" -m pip install -e .
else
    printf 'Unknown parameter %s\n' "$1"
    printf 'Usage: %s editable\n' "$0"
    exit 1
fi
