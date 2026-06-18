# -*- coding: utf-8 -*-

"""CSV export utilities for interaction logs."""

import csv
import io
from typing import Any, Dict, List


def to_csv_string(data: List[Dict[str, Any]]) -> str:
    """Serialize a list of dicts to a UTF-8 CSV string.

    All keys found across all records are used as column headers so that
    sparse data (missing keys in some records) is exported cleanly.
    """
    if not data:
        return ""

    # Collect all field names preserving insertion order
    fieldnames: List[str] = []
    seen = set()
    for record in data:
        for key in record.keys():
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        restval="",
    )
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()
