from __future__ import annotations

import pytest

from benchkit.snapshot import (
    id_suffix,
    load_snapshot,
    parse_test_id,
    write_memory_snapshot,
    write_timing_snapshot,
)


def test_id_grammar_roundtrips():
    sfx = id_suffix("basic", "n", 10)
    assert sfx == "basic-n=10"
    phase, subject, value, axis = parse_test_id(f"a/test_build.py::test_build[{sfx}]")
    assert (phase, subject, value, axis) == ("test_build", "basic", 10, "n")


def test_parse_non_matching_id_is_other():
    assert parse_test_id("weird::thing") == ("other", "other", None, "other")


def test_memory_snapshot_roundtrip(tmp_path):
    p = write_memory_snapshot(tmp_path / "m.json", "v1", {"x[basic-n=10]": 1.5})
    label, vals, unit = load_snapshot(p)
    assert unit == "MiB"
    assert vals == {"x[basic-n=10]": 1.5}


def test_timing_snapshot_roundtrip(tmp_path):
    p = write_timing_snapshot(tmp_path / "t.json", [("x[basic-n=10]", {"min": 0.1})])
    _, vals, unit = load_snapshot(p)
    assert unit == "s"
    assert vals == {"x[basic-n=10]": 0.1}


def test_malformed_snapshot_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(ValueError, match="not a readable JSON snapshot"):
        load_snapshot(bad)
