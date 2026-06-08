from __future__ import annotations

import platform
from contextlib import contextmanager

import pytest

from benchkit import Case, measure

memray = pytest.importorskip("memray")
pytestmark = pytest.mark.skipif(
    platform.system() == "Windows", reason="memray unavailable on Windows"
)


def _cases():
    @contextmanager
    def case(n):
        data = list(range(n))  # setup — not measured
        yield lambda: [x * 2 for x in data]

    return [
        Case(id=f"double[n={n}]", dims={"op": "double", "n": n}, run=lambda n=n: case(n))
        for n in (1000, 10_000)
    ]


def test_measure_returns_peak_per_case():
    peaks = measure(_cases())
    assert set(peaks) == {"double[n=1000]", "double[n=10000]"}
    assert all(v >= 0 for v in peaks.values())


def test_select_filters_cases():
    peaks = measure(_cases(), select=lambda c: c.dims["n"] == 1000)
    assert set(peaks) == {"double[n=1000]"}
