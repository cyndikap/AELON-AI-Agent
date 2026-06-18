# -*- coding: utf-8 -*-
"""
Export handler for AELON interaction data.
Provides CSV export functionality for the admin dashboard.
"""

import csv
import io
from typing import List, Dict, Any


def interactions_to_csv(data: List[Dict[str, Any]]) -> str:
    """
    Convert a list of interaction records to CSV string.

    Args:
        data: List of interaction dictionaries.

    Returns:
        CSV-formatted string.
    """
    if not data:
        return ""

    # Gather all fieldnames preserving insertion order and deduplicating
    all_keys = list(dict.fromkeys(key for record in data for key in record.keys()))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    for record in data:
        writer.writerow({k: record.get(k, "") for k in all_keys})

    return output.getvalue()
