"""The snapshot spine — the :class:`Sample` record, the on-disk JSON shape, and the
tidy long-DataFrame loader.

A snapshot is a list of :class:`Sample` — each an opaque ``id``, a ``value``, and
structured ``dims`` for analysis. Nothing parses the id: structure lives in
``dims``, which flows from :class:`~peakbench.case.Case` through ``measure`` to the
snapshot and out to the plots.

On-disk shape::

    {"label": "v1", "unit": "MiB",
     "samples": [{"id": "...", "value": 18.8, "dims": {"op": "build", "n": 10}}]}

``peakbench.measure`` and ``peakbench.bench`` write this natively. pytest-benchmark
JSON (no dims) is lifted in via :func:`from_pytest_benchmark`, which the consumer
feeds the dims for each id.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from peakbench.case import DimValue

if TYPE_CHECKING:
    import pandas as pd


class Sample(NamedTuple):
    """One measured result: an opaque ``id``, a ``value``, and analysis ``dims``."""

    id: str
    value: float
    dims: Mapping[str, DimValue]


def write_snapshot(path: str | Path, label: str, samples: list[Sample], unit: str) -> Path:
    """Write ``samples`` to ``path`` as a peakbench snapshot."""
    data = {
        "label": label,
        "unit": unit,
        "samples": [{"id": s.id, "value": s.value, "dims": dict(s.dims)} for s in samples],
    }
    out = Path(path)
    out.write_text(json.dumps(data, indent=2))
    return out


def load_snapshot(path: str | Path) -> tuple[str, list[Sample], str]:
    """Return ``(label, samples, unit)`` for a peakbench snapshot.

    Raises a clear, file-named :class:`ValueError` on a malformed file or one
    that isn't the peakbench ``samples`` shape (e.g. a raw pytest-benchmark file —
    convert those with :func:`from_pytest_benchmark`).
    """
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: not a readable JSON snapshot ({exc})") from exc
    if "samples" not in data or "unit" not in data:
        raise ValueError(
            f"{path}: not a peakbench snapshot (expected 'samples' + 'unit' keys). "
            "Convert pytest-benchmark JSON with from_pytest_benchmark()."
        )
    label = data.get("label", Path(path).stem)
    samples = [
        Sample(id=s["id"], value=s["value"], dims=s.get("dims", {})) for s in data["samples"]
    ]
    return label, samples, data["unit"]


def from_pytest_benchmark(
    path: str | Path,
    *,
    dims_for: Callable[[str], Mapping[str, DimValue]] = lambda _id: {},
    metric: str = "min",
) -> tuple[str, list[Sample], str]:
    """Lift a pytest-benchmark JSON file into ``(label, samples, "s")``.

    ``dims_for(id)`` supplies the analysis dims for each benchmark id (the
    benchmark JSON carries none); ``metric`` picks the stat (``min`` / ``median``
    / …). Use this to bring timing snapshots into the peakbench format.
    """
    p = Path(path)
    try:
        data = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: not a readable JSON file ({exc})") from exc
    if "benchmarks" not in data:
        raise ValueError(f"{path}: not a pytest-benchmark file (no 'benchmarks' key)")
    samples = [
        Sample(id=bm["fullname"], value=bm["stats"][metric], dims=dict(dims_for(bm["fullname"])))
        for bm in data["benchmarks"]
    ]
    return p.stem, samples, "s"


def discover_snapshots(root: str | Path = ".benchmarks") -> list[Path]:
    """Return JSON snapshot files under ``root`` (for CLI suggestions)."""
    base = Path(root)
    return sorted(base.rglob("*.json")) if base.exists() else []


def _check_same_unit(units: set[str]) -> str:
    if len(units) > 1:
        raise ValueError(f"snapshots mix units {units}; can't compare across metrics")
    return next(iter(units))


def load_long_df(snapshots: Sequence[str | Path]) -> tuple[pd.DataFrame, str]:
    """Return ``(df, unit)`` — one row per ``(snapshot, id)``.

    Columns: ``snapshot``, ``id``, ``value``, then one column per dim key seen
    across the samples (missing dims are ``NaN``). ``unit`` is the shared unit;
    every loaded snapshot must agree. Every plot view pivots this single frame.
    """
    import pandas as pd

    rows: list[dict[str, object]] = []
    units: set[str] = set()
    for path in snapshots:
        label, samples, unit = load_snapshot(path)
        units.add(unit)
        for s in samples:
            rows.append({"snapshot": label, "id": s.id, "value": s.value, **s.dims})
    unit = _check_same_unit(units)
    df = pd.DataFrame(rows)
    return df, unit
