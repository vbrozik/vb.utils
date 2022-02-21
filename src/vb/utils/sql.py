"""Provide SQL utilities."""

from __future__ import annotations

import sqlite3
import itertools
import inspect

from typing import Iterable

# import pandas as pd


def pivot_view(
        conn: sqlite3.Connection,
        table_name: str,
        pivot_column: str,
        pivot_values: Iterable[str | int],
        pivoted_value_columns: Iterable[str],
        group_by_column: str,
        pivot_view_name: str = '',
        temporary: bool = True,
        aggreg_function: str = 'MAX') -> str:
    """Create a view that pivots a table.

    pivot_values is a list of values to pivot on. Every value in the list
    creates a new column for every column in pivoted_value_columns.
    On the other hand every value in group_by_column is expected to have
    only single row for every value in pivot_values.
    All the rows with the same value in the group_by_column are grouped
    together and the newly created columns will contain values from the
    original rows.

    Fixme: Fix/add examples.

    Args:
        conn: connection to the database
        table_name: name of the table to pivot
        pivot_column: name of the column to pivot by
        pivot_values: values of the pivot_column to pivot (other are ignored)
        pivoted_value_columns: columns to be multiplied by pivot
        group_by_column: column to group by, this column is not pivoted
            every pivot_value is expected to have a single appearance
            in the group
        pivot_table_name: name of the pivot view (_pivot suffix by default)
        temporary: whether the created view should be a temporary one
        aggreg_function: SQL function name to use for aggregation

    Returns:
        name of the pivot view

    Examples:
        FIXME: This test has to be completed.
        >>> import sqlite3
        >>> conn = sqlite3.connect(':memory:')
        >>> pivot_table = pivot_view(
        ...     conn, 'table_name', 'group_by', 'value_column',
        ...     'pivot_column', 'pivot_value')
        >>> conn.execute(       # doctest: +SKIP
        ...     f'select * from {pivot_table}').fetchall()
        [(1, 'a', 1), (1, 'a', 2), (1, 'a', 3), (1, 'b', 1), (1, 'b', 2),
         (1, 'b', 3), (2, 'a', 1), (2, 'a', 2), (2, 'a', 3), (2, 'b', 1),
         (2, 'b', 2), (2, 'b', 3)]
    """
    if not pivot_view_name:
        pivot_view_name = f'{table_name}_pivot'
    temporary_cmd = 'TEMPORARY' if temporary else ''
    pivot_col_cmds: list[str] = []
    for pivot_value in pivot_values:
        pivot_col_cmds.extend(
            f'''{aggreg_function}("{pivoted_value_column}") '''
            f'''FILTER (WHERE "{pivot_column}" = {pivot_value}) '''
            f'''AS {pivoted_value_column}_{pivot_value}'''
            for pivoted_value_column in pivoted_value_columns)
    pivot_col_cmds_txt = '\n            , '.join(pivot_col_cmds)
    command = f'''
        CREATE {temporary_cmd} VIEW IF NOT EXISTS "{pivot_view_name}" AS
        SELECT
            "{group_by_column}"
            , {pivot_col_cmds_txt}
        FROM "{table_name}"
        GROUP BY "{group_by_column}"
        '''
    conn.execute(command)
    # df = pd.read_sql(f'''SELECT * FROM "{pivot_view_name}" LIMIT 10''', conn)
    # print(df)
    return pivot_view_name


def pivot_moving_view(
        conn: sqlite3.Connection,
        table_name: str,
        pivot_column: str,
        pivot_values: Iterable[str | int],
        pivoted_value_columns: Iterable[str],
        window_column: str,
        window_size: tuple[int, int] = (90, 90),
        pivot_view_name: str = '',
        temporary: bool = True,
        aggreg_function: str = 'AVG',
        min_aggreg_count: int = 3) -> str:
    """Create a view that pivots a table and calculates moving averages."""
    if not pivot_view_name:
        pivot_view_name = f'{table_name}_m_avg'
    temporary_cmd = 'TEMPORARY' if temporary else ''
    pivot_col_cmds = []
    pivot_col_cnt_cmds = []
    pivot_col_cnt_conditions = []
    for pivot_value in pivot_values:
        for pivoted_value_column in pivoted_value_columns:
            column_template = (
                f'''{{aggreg_function}}("{pivoted_value_column}") '''
                f'''FILTER (WHERE "{pivot_column}" = {pivot_value}) '''
                f'''OVER pivot_window '''
                f'''AS {pivoted_value_column}_{{col_suffix}}_{pivot_value}''')
            pivot_col_cmds.append(column_template.format(
                    aggreg_function=aggreg_function,
                    col_suffix=aggreg_function.lower()))
            pivot_col_cnt_cmds.append(column_template.format(
                    aggreg_function='COUNT', col_suffix='cnt'))
            pivot_col_cnt_conditions.append(
                f'{pivoted_value_column}_cnt_{pivot_value} '
                f'>= {min_aggreg_count}')
    pivot_col_cmds_txt = '\n                , '.join(pivot_col_cmds)
    pivot_col_cnt_cmds_txt = '\n                , '.join(pivot_col_cnt_cmds)
    command = f'''
        CREATE {temporary_cmd} VIEW IF NOT EXISTS "{pivot_view_name}" AS
        WITH pivot_ungrouped AS (
            SELECT
                "{window_column}"
                , {pivot_col_cmds_txt}
                , {pivot_col_cnt_cmds_txt}
            FROM "{table_name}"
            WINDOW pivot_window AS (
                ORDER BY "{window_column}"
                RANGE BETWEEN
                    {window_size[0]} PRECEDING AND
                    {window_size[1]} FOLLOWING))
        SELECT * FROM pivot_ungrouped
        WHERE {' AND '.join(pivot_col_cnt_conditions)}
        GROUP BY "{window_column}"
        '''
    # print(command)            # DEBUG
    conn.execute(command)
    # df = pd.read_sql(f'''SELECT * FROM "{pivot_view_name}" LIMIT 10''', conn)
    # print(df)
    return pivot_view_name


def consec_diff_view(
        conn: sqlite3.Connection,
        table_name: str,
        diff_column: str,
        diff_view_name: str = '',
        temporary: bool = True) -> str:
    """Create a view adding differences between consecutive values of a column.

    Args:
        conn: connection to the database
        table_name: name of the table to pivot
        diff_column: name of the column to add the differences of
        diff_view_name: name of the view (_cdiff suffix by default)

    Returns:
        name of the diff view

    Examples:
        >>> import sqlite3
        >>> conn = sqlite3.connect(':memory:')
    """
    if not diff_view_name:
        diff_view_name = f'{table_name}_cdiff'
    temporary_cmd = 'TEMPORARY' if temporary else ''
    command = f'''
        CREATE {temporary_cmd} VIEW IF NOT EXISTS "{diff_view_name}" AS
        SELECT
            *,
            "{diff_column}" - LAG("{diff_column}")
                OVER (ORDER BY "{diff_column}") AS "{diff_column}_diff_p1",
            "{diff_column}" - LEAD("{diff_column}")
                OVER (ORDER BY "{diff_column}") AS "{diff_column}_diff_n1"
        FROM "{table_name}"
        ORDER BY "{diff_column}"
        '''
    conn.execute(command)
    return diff_view_name


def many_columns_condition(
        columns: Iterable[str],
        comparison: str,
        bool_op: str = 'AND',
        quote_columns: bool = True) -> str:
    """Generate condition applying the same comparison to multiple columns.

    Args:
        columns: columns to compare
        comparison: comparison operation to apply
        bool_op: boolean operator joining the conditions
        quote_columns: whether to quote the column names or not

    Returns:
        SQL expression

    Examples:
        >>> many_columns_condition(['a', 'b'], '= 2')
        '"a" = 2 AND "b" = 2'
    """
    quote = '"' if quote_columns else ''
    return f' {bool_op} '.join(
            f'{quote}{col}{quote} {comparison}' for col in columns)


def order_by_columns(
        columns: Iterable[str],
        reverse: Iterable[bool | None] = (),
        clause: str = 'ORDER BY',
        quote_columns: bool = True) -> str:
    """Generate ORDER BY clause.

    Args:
        columns: columns to order by
        reverse: descending direction of the column ordering
        quote_columns: whether to quote the column names or not

    Returns:
        values for SQL ORDER BY clause as a string

    Examples:
        >>> order_by_columns(('a', 'b', 'c'))
        'ORDER BY "a", "b", "c"'

        >>> order_by_columns(('a', 'b', 'c'), (None, True))
        'ORDER BY "a", "b" DESC, "c"'
    """
    quote = '"' if quote_columns else ''
    if not columns:
        return ''
    if clause:
        clause += ' '
    return clause + ', '.join(
            f'{quote}{col}{quote}{" DESC" if rev else ""}'
            for col, rev in itertools.zip_longest(columns, reverse))


def query_extreme(
        table: str,
        extreme_column: str,
        extreme_func: str = 'max',
        order_columns: Iterable[str] = (),
        reverse: Iterable[bool | None] = (),
        quote_identifiers: bool = True) -> str:
    """Generate SQL query to get the extreme value of a column.

    Args:
        table: name of the table to query
        extreme_column: name of the column to get the extreme value of
        extreme_func: function to apply to the extreme column (max, min)
        order_columns: columns to order by and select
        reverse: descending direction of the individual columns ordering

    Returns:
        SQL query as a string

    Examples:
        >>> print(query_extreme('table', 'column'))
        SELECT "column"
        FROM "table"
        WHERE "column" = (
            SELECT max("column")
            FROM "table")

        >>> print(query_extreme('table', 'column', order_columns=('a', 'b')))
        SELECT "a", "b", "column"
        FROM "table"
        WHERE "column" = (
            SELECT max("column")
            FROM "table")
        ORDER BY "a", "b"
    """
    quote = '"' if quote_identifiers else ''
    return inspect.cleandoc(
            f'''
            SELECT {', '.join(f'{quote}{col}{quote}' for col
                    in itertools.chain(order_columns, (extreme_column,)))}
            FROM {quote}{table}{quote}
            WHERE {quote}{extreme_column}{quote} = (
                SELECT {extreme_func}({quote}{extreme_column}{quote})
                FROM {quote}{table}{quote})
            {order_by_columns(
                    order_columns, reverse, quote_columns=quote_identifiers)}
            ''')
