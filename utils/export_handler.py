# -*- coding: utf-8 -*-

"""CSV export utilities for interaction logs."""

import csv
import io
from typing import Any, Dict, List


def to_csv_string(data: List[Dict[str, Any]]) -> str:
    """Serialize a list of dicts to a UTF-8 CSV string."""
    if not data:
        return ""

    # Gather all field names preserving insertion order and deduplicating.
    fieldnames = list(dict.fromkeys(key for record in data for key in record.keys()))

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        restval="",
    )
    writer.writeheader()
    for record in data:
        writer.writerow({k: record.get(k, "") for k in fieldnames})

    return output.getvalue()


def interactions_to_csv(data: List[Dict[str, Any]]) -> str:
    """Backward-compatible alias for CSV export."""
    return to_csv_string(data)
