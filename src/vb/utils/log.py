#!/usr/bin/python3

"""Provide logging handling.

Todo:
    * logging progress on a single line (suppress newline)
    * context manager to finish the log line
"""

from __future__ import annotations

import logging

from typing import Any


# --- constants:

DEBUG2 = 5  # logging level beyond DEBUG


class StreamHandler(logging.StreamHandler):
    """Implement handler that controls the writing of the newline character.

    Todo:
        * Add alternate formatter self.setFormatter(...)?
        * Use the original terminator
    """

    suppress_newline_code = '%[!n]'

    def emit(self, record: logging.LogRecord) -> None:
        """Extend the method to be able to remove trailing newline."""
        if record.msg.endswith(self.suppress_newline_code):
            record.msg = record.msg[:-len(self.suppress_newline_code)]
            self.terminator = ''
        else:
            self.terminator = '\n'
        return super().emit(record)


# --- functions:

def init(verbosity: int = 0, newlinehandler: bool = False) -> None:
    """Initialize logging.

    Args:
        verbosity: number -3 - +3:
            enabled logging levels by verbosity:
                -2: no standard logging
                -1: CRITICAL
                0:  ERROR
                1:  WARNING
                2:  DEBUG
                3:  DEBUG2  - all levels
        newlinehandler: if True, use alternate logging StreamHandler

    Todo:
        * message alignment %(levelname)8s
        * timestamps %(asctime)s %(msecs)03d datefmt='%Y-%m-%d %H:%M:%S'
        * allow modern {} formatter
    """
    logging.addLevelName(DEBUG2, 'DEBUG2')
    optargs: dict[str, Any] = {}
    if newlinehandler:
        optargs['handlers'] = (StreamHandler(),)
    logging.basicConfig(format='%(levelname)s: %(message)s', **optargs)
    logging.getLogger().setLevel(30 - 10 * verbosity)
    if verbosity:
        logging.info(f"verbosity: {verbosity}")
