"""benchkit CLI — ``plot`` and ``compare`` over snapshot files.

These are the registry-free commands (they read JSON only). A consumer that
wants ``run`` / ``sweep`` / ``list`` builds those on its own ``Case`` source and
adds them to this app (or its own).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Annotated

import typer

from benchkit.snapshot import Metric, discover_snapshots

app = typer.Typer(
    help="benchkit — plot and compare benchmark snapshots.",
    no_args_is_help=True,
)


def _need_plotly() -> None:
    if importlib.util.find_spec("plotly") is None:
        typer.secho(
            "plotting needs extras: pip install 'benchkit[plot]'",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=2)


@app.command()
def plot(
    snapshots: Annotated[list[Path], typer.Argument(help="Snapshot JSON file(s).")],
    view: Annotated[
        str | None,
        typer.Option(help="compare | scatter | sweep | scaling (default: by count)."),
    ] = None,
    metric: Annotated[Metric, typer.Option(help="Timing stat (memory ignores it).")] = "min",
    output: Annotated[Path | None, typer.Option("--output", "-o", help="HTML out path.")] = None,
    open_browser: Annotated[bool, typer.Option("--open/--no-open")] = False,
) -> None:
    """Render an interactive plotly view from one or more snapshots."""
    missing = [p for p in snapshots if not p.exists()]
    if missing:
        typer.secho(f"missing: {[str(p) for p in missing]}", fg=typer.colors.RED, err=True)
        found = discover_snapshots()
        if found:
            typer.echo("available:\n  " + "\n  ".join(str(p) for p in found), err=True)
        raise typer.Exit(code=2)

    chosen = view or (
        "scaling" if len(snapshots) == 1 else "scatter" if len(snapshots) == 2 else "sweep"
    )
    _need_plotly()
    from benchkit.plotting import RENDERERS

    if chosen not in RENDERERS:
        typer.secho(f"unknown view {chosen!r}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    try:
        fig, n = RENDERERS[chosen](snapshots, metric, "absolute", None, None)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    output = output or Path(".benchmarks") / "plots" / f"{chosen}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output)
    typer.secho(f"{chosen} ({metric}): {n} tests → {output}", fg=typer.colors.GREEN)
    if open_browser:
        import webbrowser

        webbrowser.open(output.resolve().as_uri())


@app.command()
def compare(
    a: Annotated[Path, typer.Argument(help="Baseline snapshot.")],
    b: Annotated[Path, typer.Argument(help="Candidate snapshot.")],
    metric: Annotated[Metric, typer.Option()] = "min",
) -> None:
    """Print a per-id delta table for two snapshots (timing or memory)."""
    for p in (a, b):
        if not p.exists():
            typer.secho(f"missing: {p}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=2)
    from benchkit.compare import compare_snapshots

    try:
        compare_snapshots(a, b, metric=metric)
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc
