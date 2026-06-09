"""The atomic primitive: a :class:`Case` — one measurable unit of work.

Everything downstream (the memray engine, snapshots, plots) consumes only
``Case``; how cases are *generated* is the consumer's business. A case is a
context manager so setup (build inputs, scratch files) runs untimed/untracked
before the measured ``action`` and teardown runs after::

    @contextmanager
    def build_case(n):
        data = make_input(n)            # setup — not measured
        yield lambda: transform(data)   # the measured action

    Case(id="transform[n=1000]", dims={"op": "transform", "n": 1000},
         run=lambda: build_case(1000))
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from typing import NamedTuple, TypeVar

#: A value of a dim axis — categorical (str) or numeric (int/float).
DimValue = str | int | float

#: A zero-arg callable doing the work that gets timed / memory-tracked.
Action = Callable[[], object]

#: A factory returning a fresh context manager that yields an :data:`Action`.
CaseFactory = Callable[[], AbstractContextManager[Action]]


class Case(NamedTuple):
    """One measurable unit of work.

    - ``id``  — stable identity, the key in snapshots (and, in pytest, the
      node id CodSpeed tracks). Opaque to peakbench.
    - ``dims`` — structured axes for analysis (e.g. ``{"op": "to_lp",
      "subject": "basic", "n": 10}``). Plots facet/scale by these instead of
      parsing the id.
    - ``run`` — a factory returning a context manager: setup → yield the
      measured ``action`` → teardown.
    """

    id: str
    dims: Mapping[str, DimValue]
    run: CaseFactory


_T = TypeVar("_T")


def build_once(
    setup: Callable[[], _T],
    action: Callable[[_T], object],
    *,
    teardown: Callable[[_T], None] | None = None,
) -> CaseFactory:
    """A :data:`CaseFactory` for the build-once shape, untimed setup and all.

    Folds the boilerplate ``@contextmanager`` away: ``setup()`` runs once
    (untracked), the measured action is ``action(obj)``, and ``teardown(obj)``
    runs after — even if the action raises::

        Case(id="to_lp[n=1000]", dims={"op": "to_lp", "n": 1000},
             run=build_once(lambda: model.build(1000), lambda m: m.to_file("/tmp/m.lp")))

    For scratch resources, build them in ``setup`` and clean up in ``teardown``
    (e.g. ``tempfile.TemporaryDirectory`` — keep the handle on the built object
    or close over it).
    """

    @contextmanager
    def factory() -> Iterator[Action]:
        obj = setup()
        try:
            yield lambda: action(obj)
        finally:
            if teardown is not None:
                teardown(obj)

    return factory
