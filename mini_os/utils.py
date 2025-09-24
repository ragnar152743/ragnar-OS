"""Utility helpers shared across MiniOS modules."""

from __future__ import annotations

from typing import Iterable, Sequence


def format_table(rows: Iterable[Sequence[str]]) -> str:
    """Render a lightweight textual table from rows of strings."""

    columns = []
    processed_rows = []
    for row in rows:
        cells = tuple(str(cell) for cell in row)
        processed_rows.append(cells)
        for index, cell in enumerate(cells):
            if len(columns) <= index:
                columns.append(len(cell))
            else:
                columns[index] = max(columns[index], len(cell))

    padded_rows = []
    for cells in processed_rows:
        padded = [cell.ljust(columns[index]) for index, cell in enumerate(cells)]
        padded_rows.append("  ".join(padded).rstrip())

    return "\n".join(padded_rows)

