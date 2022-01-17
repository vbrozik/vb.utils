"""Provide date and time functions."""

from __future__ import annotations

from datetime import datetime, timezone, tzinfo


def timezone_from_name(name: str) -> tzinfo | None:
    """Return timezone from name.

    Args:
        name: timezone name
            special names: 'UTC', 'local', 'localtime'
            Other names reqire the zoneinfo package from Python 3.9+
            or backports.zoneinfo from pypi.org.

    Returns:
        timezone

    Todo:
        * Add support for pytz.
        * Check the best way of importing the alternative packages.
        * Add dependencies to setup.cfg?
    """
    if name == 'UTC':
        return timezone.utc
    elif name in {'local', 'localtime'}:
        # alternative: None
        return datetime.now(timezone.utc).astimezone().tzinfo
    else:
        # For other timezones than UTC and local we need to import module
        # zoneinfo which is in the standard library since Python 3.10.
        try:
            import zoneinfo                 # type: ignore # optional import
        except ImportError:
            from backports import zoneinfo  # type: ignore # optional import
        return zoneinfo.ZoneInfo(name)


def iso_from_timestamp(
        timestamp: float, t_zone: tzinfo | None = timezone.utc) -> str:
    """Return ISO 8601 date string from timestamp.

    Args:
        timestamp: timestamp (seconds since epoch) in the given timezone
        t_zone: timezone (UTC by default)

    Returns:
        ISO 8601 date string

    Examples:
        >>> iso_from_timestamp(1568783600)
        '2019-09-18T05:13:20+00:00'

        >>> iso_from_timestamp(0)
        '1970-01-01T00:00:00+00:00'

        >>> iso_from_timestamp(1568783600.123456)
        '2019-09-18T05:13:20.123456+00:00'

        >>> from datetime import timedelta
        >>> iso_from_timestamp(
        ...     1568783600.123456, t_zone=timezone(offset=timedelta(hours=1)))
        '2019-09-18T06:13:20.123456+01:00'
    """
    return datetime.fromtimestamp(timestamp, t_zone).isoformat()


def hms_from_seconds(
        seconds: float,
        frac_digits: int = 0, omit_significant: int = 2) -> str:
    """Return time string from seconds.

    Args:
        seconds: number of seconds
        frac_digits: number of fractional digits for seconds
        omit_significant: number of the most significant parts
            (hours, minutes) to omit

    Returns:
        time string in [[HH:]MM:]SS[.ss] format

    Examples:
        >>> hms_from_seconds(0, omit_significant=0)
        '00:00:00'

        >>> hms_from_seconds(7)
        '07'

        >>> hms_from_seconds(3743.123456)
        '01:02:23'

        >>> hms_from_seconds(3743.123456, frac_digits=2)
        '01:02:23.12'

    Todo:
        * Allow the highest order part not to be zero-padded.
    """
    hr, sec = divmod(seconds, 3600)
    mn, sec = divmod(sec, 60)
    time_parts: list[str] = []
    if hr or not omit_significant:
        time_parts.append(f'{int(hr):02d}')
        omit_significant = 0
    if omit_significant:
        omit_significant -= 1
    if mn or not omit_significant:
        time_parts.append(f'{int(mn):02d}')
    time_parts.append(f'{sec:02.{frac_digits}f}')
    return ':'.join(time_parts)
