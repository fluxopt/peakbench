"""The snapshot contract — the on-disk JSON shapes, the id grammar, and the tidy
long-DataFrame loader.

Dependency-free (stdlib + lazy pandas), so every writer (pytest-benchmark,
:func:`benchkit.memray.measure`, :mod:`benchkit.bench`) and reader
(:mod:`benchkit.plotting`, :func:`benchkit.compare`) shares it.

Two shapes, auto-detected on load:

- **timing** — ``{"benchmarks": [{"fullname": <id>, "stats": {…}}]}`` → seconds
  (what pytest-benchmark writes).
- **memory** — ``{"label": <str>, "peak_mib": {<id>: <float>}}`` → MiB.

The default id grammar is ``…[<subject>-<axis>=<value>]`` (``<axis>`` the sweep
dial). :func:`parse_test_id` recovers the structured columns from it; a consumer
with a different id shape can pass its own dims, but this is the convention the
bundled plots assume.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import pandas as pd

Metric = Literal["min", "median", "mean", "max"]

_SIZE_RE = re.compile(r"(.*)\[([^\[\]]+?)-(\w+)=(\d+)\]")


def id_suffix(subject: str, axis: str, value: object) -> str:
    """The ``<subject>-<axis>=<value>`` fragment inside a case id's ``[...]``."""
    return f"{subject}-{axis}={value}"


def parse_test_id(test_id: str) -> tuple[str, str, int | None, str]:
    """Return ``(phase, subject, value, axis)`` for a case id.

    ``value`` is the integer swept along ``axis``. Falls back to
    ``("other", "other", None, "other")`` for ids that don't match the
    ``…[<subject>-<axis>=<value>]`` shape.
    """
    m = _SIZE_RE.match(test_id)
    if m:
        phase = m.group(1).split("::")[-1]
        return phase, m.group(2), int(m.group(4)), m.group(3)
    return "other", "other", None, "other"


def synth_test_id(
    label: str,
    *,
    spec: str | None,
    size: int | None,
    phase: str | None,
    axis: str = "n",
) -> str:
    """Build a case id from optional metadata.

    With all of ``spec``/``size``/``phase`` supplied, synthesize
    ``bench::{phase}[{spec}-{axis}={size}]`` (round-trips through
    :func:`parse_test_id`). With none, fall back to ``label`` verbatim; a partial
    spec is ambiguous and rejected.
    """
    if spec is not None and size is not None and phase is not None:
        return f"bench::{phase}[{id_suffix(spec, axis, size)}]"
    if spec is not None or size is not None or phase is not None:
        raise ValueError("spec, size, and phase must be given together (or all omitted)")
    return label


def write_timing_snapshot(path: str | Path, entries: list[tuple[str, dict[str, float]]]) -> Path:
    """Write the pytest-benchmark timing shape (seconds) from ``(id, stats)``."""
    data = {
        "benchmarks": [{"fullname": fullname, "stats": dict(stats)} for fullname, stats in entries]
    }
    out = Path(path)
    out.write_text(json.dumps(data, indent=2))
    return out


def write_memory_snapshot(path: str | Path, label: str, peaks: dict[str, float]) -> Path:
    """Write the memory shape (``{id: peak_mib}``)."""
    out = Path(path)
    out.write_text(json.dumps({"label": label, "peak_mib": dict(peaks)}, indent=2))
    return out


def load_snapshot(path: Path, metric: Metric = "min") -> tuple[str, dict[str, float], str]:
    """Return ``(label, {id: value}, unit)`` for one snapshot, auto-detecting shape.

    Timing → ``stats[metric]`` in seconds; memory → peak MiB (``metric``
    ignored). Raises a clear, file-named :class:`ValueError` on a malformed or
    unrecognized file.
    """
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: not a readable JSON snapshot ({exc})") from exc
    if "peak_mib" in data:
        return Path(path).stem, dict(data["peak_mib"]), "MiB"
    if "benchmarks" not in data:
        raise ValueError(
            f"{path}: unrecognized snapshot shape "
            "(no 'peak_mib' memory key or 'benchmarks' timing key)"
        )
    values = {bm["fullname"]: bm["stats"][metric] for bm in data["benchmarks"]}
    return Path(path).stem, values, "s"


def discover_snapshots(root: str | Path = ".benchmarks") -> list[Path]:
    """Return JSON snapshot files under ``root`` (for CLI suggestions)."""
    base = Path(root)
    return sorted(base.rglob("*.json")) if base.exists() else []


def _check_same_unit(snapshots: list[tuple[str, dict[str, float], str]]) -> str:
    units = {u for _, _, u in snapshots}
    if len(units) > 1:
        raise ValueError(f"snapshots mix units {units}; can't compare timing and memory")
    return next(iter(units))


def load_long_df(snapshots: list[Path], metric: Metric = "min") -> tuple[pd.DataFrame, str]:
    """Return ``(df, unit)`` — one row per ``(snapshot, id)``.

    Columns: ``snapshot``, ``test_id``, ``phase``, ``spec``, ``size``
    (``Int64``-nullable), ``axis``, ``value``. ``unit`` is the shared unit
    (``"s"`` or ``"MiB"``) — every loaded snapshot must agree. Every plot view
    pivots this single frame.
    """
    import pandas as pd

    raw = [load_snapshot(p, metric) for p in snapshots]
    unit = _check_same_unit(raw)
    rows = []
    for label, vals, _ in raw:
        for test_id, value in vals.items():
            phase, spec, size, axis = parse_test_id(test_id)
            rows.append(
                {
                    "snapshot": label,
                    "test_id": test_id,
                    "phase": phase,
                    "spec": spec,
                    "size": size,
                    "axis": axis,
                    "value": value,
                }
            )
    df = pd.DataFrame(rows)
    df["size"] = df["size"].astype("Int64")
    return df, unit
