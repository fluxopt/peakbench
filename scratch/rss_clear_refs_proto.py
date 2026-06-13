#!/usr/bin/env python3
"""Linux prototype: validate in-process RSS measurement via /proc/self/clear_refs.

Decides whether the `rss` engine can move from fork to in-process (memory-pass-first,
clear_refs HWM reset). Run on Linux (CI). Asserts three things:

  A. cold allocation is captured  — building a dict reads ~its resident size
  B. inherited-input artifact GONE — sum() over an already-resident list reads ~0
     (the fork approach charged this ~76 MiB; in-process should be ~0 because the
      input is resident *before* we reset the high-water mark)
  C. warm heap defeats it          — the same build, measured after a warmup loop,
     reads ~0 — which is WHY the memory pass must run before timing (ordering is
     load-bearing, not cosmetic)

If A & B & C hold, in-process + memory-first is viable. If not, fall back to fork.
"""

from __future__ import annotations

import gc
import platform
import sys

MIB = 1024 * 1024


def _status_bytes(key: str) -> int:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith(key + ":"):
                return int(line.split()[1]) * 1024  # kB → bytes
    raise RuntimeError(f"{key} not in /proc/self/status")


def _reset_hwm() -> None:
    with open("/proc/self/clear_refs", "w") as f:
        f.write("5")  # CLEAR_REFS_MM_HIWATER_RSS — reset peak RSS to current (Linux >= 4.0)


def measure_rss_inprocess(action) -> tuple[int, int]:
    """Return (net, gross) resident bytes for `action`, measured in-process.

    net  = peak RSS during the action minus RSS at the start (the action's growth)
    gross = absolute peak RSS (whole process)
    """
    gc.collect()
    rss0 = _status_bytes("VmRSS")
    _reset_hwm()
    action()
    hwm = _status_bytes("VmHWM")
    return max(0, hwm - rss0), hwm


def build_dict():
    return {f"key-{i}": i for i in range(300_000)}


def main() -> int:
    print(f"platform={platform.system()} kernel={platform.release()} py={sys.version.split()[0]}")
    if platform.system() != "Linux":
        print("SKIP: clear_refs is Linux-only")
        return 0

    ok = True

    # A. cold allocation captured
    netA, grossA = measure_rss_inprocess(build_dict)
    print(f"\nA cold dict(300k):           net={netA/MIB:6.1f} MiB  gross={grossA/MIB:6.1f} MiB")
    okA = netA > 5 * MIB
    print(f"   [{'PASS' if okA else 'FAIL'}] net > 5 MiB (real allocation captured)")
    ok &= okA

    # compare to heap, to confirm it captures the allocator-overhead divergence
    try:
        from pytest_benchmem.memray import measure_memory

        heap = measure_memory(build_dict, mode="heap").peak_bytes
        print(f"   heap={heap/MIB:.1f} MiB  rss/heap={netA/max(heap,1):.2f}x")
    except Exception as exc:  # noqa: BLE001
        print(f"   (heap comparison skipped: {exc})")

    # B. inherited-input artifact gone
    big = list(range(2_000_000))  # built + resident BEFORE measurement
    netB, _ = measure_rss_inprocess(lambda: sum(big))
    print(f"\nB sum(resident 2M list):     net={netB/MIB:6.2f} MiB")
    okB = netB < 5 * MIB
    print(f"   [{'PASS' if okB else 'FAIL'}] net < 5 MiB (reading resident input NOT charged)")
    ok &= okB

    # C. warm heap defeats it → ordering (memory before timing) is load-bearing
    for _ in range(6):  # warm the heap the way the timed pass would
        build_dict()
    netC, _ = measure_rss_inprocess(build_dict)
    print(f"\nC warm-then-measure dict:    net={netC/MIB:6.2f} MiB  (cold was {netA/MIB:.1f} MiB)")
    okC = netC < netA * 0.5
    print(f"   [{'PASS' if okC else 'FAIL'}] warm net << cold net (confirms memory must run first)")
    ok &= okC

    print(f"\n{'ALL PASS — in-process + memory-first is viable' if ok else 'SOME FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
