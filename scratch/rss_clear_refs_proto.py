#!/usr/bin/env python3
"""Linux prototype: in-process RSS via /proc/self/clear_refs — does it diverge from heap?

First run showed cold dict: in-process rss 0.99x heap, vs 1.24x under the fork approach —
suggesting the fork divergence was largely an artifact (the child is charged for faulting
code pages a no-op baseline never touched). This run tests whether in-process rss ≈ heap
*generally* (→ rss is redundant) or still diverges for some workloads (→ rss has value).

Each workload is measured in its OWN fresh subprocess (cold heap, no cross-workload
retention). Plus the B check: the inherited-input artifact is gone in-process.
"""

from __future__ import annotations

import gc
import platform
import subprocess
import sys

MIB = 1024 * 1024


def _status_bytes(key: str) -> int:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith(key + ":"):
                return int(line.split()[1]) * 1024
    raise RuntimeError(f"{key} missing")


def measure_rss_inprocess(action):
    gc.collect()
    rss0 = _status_bytes("VmRSS")
    with open("/proc/self/clear_refs", "w") as f:
        f.write("5")
    action()
    return max(0, _status_bytes("VmHWM") - rss0)


def _np():
    import numpy as np

    return np


WORKLOADS = {
    "dict-300k": lambda: {f"k{i}": i for i in range(300_000)},
    "set-1M": lambda: set(range(1_000_000)),
    "list-tuples-1M": lambda: [(i, i, i) for i in range(1_000_000)],
    "deepcopy-200k": lambda: __import__("copy").deepcopy({i: [i, i, i] for i in range(200_000)}),
    "str-concat": lambda: "".join(str(i) for i in range(2_000_000)),
    "np-ones-50M": lambda: _np().ones(50_000_000),
    "np-empty-50M": lambda: _np().empty(50_000_000),  # untouched → rss should be << heap
}


def run_one(key: str) -> None:
    action = WORKLOADS[key]
    try:
        rss = measure_rss_inprocess(action)  # cold, measured first
        from pytest_benchmem.memray import measure_memory

        heap = measure_memory(action, mode="heap").peak_bytes
        print(f"{key:<16} heap={heap / MIB:7.1f}M  rss_inproc={rss / MIB:7.1f}M  "
              f"rss/heap={rss / max(heap, 1):.2f}x")
    except ImportError as exc:
        print(f"{key:<16} skipped ({exc})")


def main() -> int:
    if len(sys.argv) > 1:
        run_one(sys.argv[1])
        return 0

    print(f"platform={platform.system()} kernel={platform.release()} py={sys.version.split()[0]}")
    if platform.system() != "Linux":
        print("SKIP: Linux only")
        return 0

    # B: inherited-input artifact gone in-process
    big = list(range(2_000_000))
    netB = measure_rss_inprocess(lambda: sum(big))
    print(f"\nB inherited-input: sum(resident 2M list) net={netB / MIB:.2f} MiB "
          f"[{'PASS gone' if netB < 5 * MIB else 'FAIL'}]\n")

    # divergence table — each workload in a fresh subprocess (cold)
    print("in-process rss vs heap (each in a fresh process):")
    for key in WORKLOADS:
        subprocess.run([sys.executable, __file__, key], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
