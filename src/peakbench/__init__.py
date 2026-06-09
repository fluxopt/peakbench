"""peakbench — generic time + peak-memory benchmarking around a ``Case``.

Light to import: only the core (``Case``, the memray engine, snapshots) is
re-exported here. ``peakbench.plotting`` pulls numpy/plotly, ``peakbench.cli``
pulls typer, and ``peakbench.sweep`` shells out to ``uv`` — import those
submodules directly when needed.
"""

from __future__ import annotations

from peakbench import bench
from peakbench.case import Action, Case, CaseFactory, DimValue, build_once
from peakbench.memray import measure, measure_peak
from peakbench.snapshot import (
    Sample,
    from_pytest_benchmark,
    load_long_df,
    load_snapshot,
    write_snapshot,
)

__all__ = [
    "Action",
    "Case",
    "CaseFactory",
    "DimValue",
    "Sample",
    "bench",
    "build_once",
    "from_pytest_benchmark",
    "load_long_df",
    "load_snapshot",
    "measure",
    "measure_peak",
    "write_snapshot",
]
