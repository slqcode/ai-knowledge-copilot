"""Run the local knowledge ingestion placeholder.

Usage:
    python -m scripts.import_data [data_path]
"""

from __future__ import annotations

import sys

from app.ingest import run


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "data")
