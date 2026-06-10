# peakbench

[![CI](https://github.com/fluxopt/peakbench/actions/workflows/ci.yaml/badge.svg)](https://github.com/fluxopt/peakbench/actions/workflows/ci.yaml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A small, generic toolkit for **time and precise peak-memory** benchmarking,
built around one primitive — the `Case`.

Its reason to exist is the gap nothing else fills cleanly: **memray-precision
memory benchmarking** of your own code. pytest-benchmark times but can't measure
memory; ASV's `peakmem` is coarse RSS sampling that misses numpy/C-allocation
detail; CodSpeed covers CI. peakbench is the thin memray layer + a `Case` glue,
with cross-version sweeps and plotly views bundled for convenience.

> **Not** a CI dashboard (use [CodSpeed]) and **not** a rigorous perf-history
> system (use [ASV]). If your core need is *precise local memory* numbers over a
> set of your own benchmarks — and timing/sweeps/plots in the same vocabulary —
> that's peakbench.

## Where it sits

| Need | Reach for | peakbench |
|---|---|---|
| CI regression, per-PR dashboard | **CodSpeed** | — (don't rebuild it) |
| Local timing + A/B compare | **pytest-benchmark** | reads its JSON |
| Rigorous perf history across commits | **ASV** | — (heavier, RSS memory) |
| **Precise local peak memory (numpy/C allocs)** | **memray** | ⭐ the core |
| One `Case` → time *or* memory, sweep, plot | — | ⭐ the glue |

## The primitive

Everything consumes one thing — a `Case`: an `id`, structured `dims` for
analysis, and a context manager that does untimed setup, yields the measured
action, and tears down.

```python
from contextlib import contextmanager
from peakbench import Case, measure


@contextmanager
def to_lp_case(model, n):
  m = model.build(n)  # setup — not measured
  yield lambda: m.to_file("/tmp/m.lp")  # the measured action


cases = [
  Case(id=f"to_lp[n={n}]", dims={"op": "to_lp", "n": n},
       run=lambda n=n: to_lp_case(model, n))
  for n in (10, 100, 1000)
]

peaks = measure(cases)  # {id: peak_MiB}, via memray
```

How cases are *generated* is yours — peakbench imposes only `Case`. A registry of
subjects × operations × sizes is a convenience you build on top, not something
peakbench dictates.

## What's in the box

- **`measure` / `measure_peak`** — peak RSS via `memray.Tracker`, with model
  build *outside* the tracked region (min-of-N for noise).
- **`bench`** — ad-hoc `time()` / `memory()` of any callable → a result you can
  drop into a snapshot.
- **`snapshot`** — read pytest-benchmark timing JSON *and* memory JSON into one
  tidy frame (auto-detected).
- **`plot`** — sweep heatmap (log₂ fold-change), scatter, compare-bars, scaling
  — over either metric.
- **`sweep`** — run your benchmarks across installed versions in fresh `uv`
  venvs (the install spec is injected, so it's not tied to any one package).

## Install

```bash
uv add peakbench              # core (stdlib only)
uv add "peakbench[all]"       # + memray, plotly/pandas/numpy, typer CLI
```

## Status

Early. Extracted from the linopy internal benchmark suite, where it's the local
memory-profiling layer. API may move before 1.0.

[CodSpeed]: https://codspeed.io
[ASV]: https://asv.readthedocs.io
