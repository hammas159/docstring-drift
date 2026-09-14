"""Point at any Python package and see which docstrings disagree with their functions.

The scan runs live on whatever path you give it - no precomputed results, no model,
no network. Pure AST comparison, so it is safe to run over third-party code you did
not write.

Run:  streamlit run ui/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from drift import scan_path

st.set_page_config(page_title="docstring drift", layout="wide")

RED, BLUE, AMBER, GREY = "#dc2626", "#2563eb", "#f59e0b", "#94a3b8"

st.title("Documentation that quietly stopped being true")
st.caption(
    "Rename a parameter and nothing fails: no test breaks, no linter complains, and "
    "the docstring keeps describing a function that no longer exists. This compares "
    "what each docstring **claims** the parameters are against what the signature "
    "**actually says** - pure AST analysis, no imports, no execution."
)

default = str(Path(sys.executable).parent.parent / "Lib" / "site-packages")
target = st.text_input("Path to scan", value=default)
path = Path(target)

if not path.exists():
    st.error(f"Not found: {path}")
    st.stop()

subdirs = (
    sorted(p.name for p in path.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))
    if path.is_dir()
    else []
)

chosen = st.multiselect(
    "Packages (leave empty to scan the path itself)",
    subdirs,
    default=[p for p in ("numpy", "pandas", "sklearn") if p in subdirs][:3],
)

targets = [path / c for c in chosen] if chosen else [path]


@st.cache_data(show_spinner="Parsing...")
def scan(paths: list[str]):
    rows, findings = [], []
    for p in paths:
        f, s = scan_path(Path(p))
        s["package"] = Path(p).name
        rows.append(s)
        for x in f:
            findings.append({**vars(x), "package": Path(p).name})
    return rows, findings


stats, findings = scan([str(t) for t in targets])
if not stats:
    st.warning("Nothing scanned.")
    st.stop()

frame = pd.DataFrame(stats)
found = (
    pd.DataFrame(findings)
    if findings
    else pd.DataFrame(columns=["package", "file", "line", "function", "kind", "name"])
)

phantom = found[found.kind == "phantom"] if len(found) else found
undoc = found[found.kind == "undocumented"] if len(found) else found

documented_total = int(frame["with_param_docs"].sum())
rate = len(phantom) / documented_total if documented_total else 0

a, b, c, d = st.columns(4)
a.metric("Functions parsed", f"{int(frame['functions'].sum()):,}")
b.metric("With documented params", f"{documented_total:,}")
c.metric("Phantom parameters", f"{len(phantom):,}")
d.metric("Phantom rate", f"{rate:.2%}")

if len(phantom):
    st.error(
        f"**{len(phantom)} documented parameters do not exist** on the function they "
        f"describe — {rate:.2%} of every function that documents its parameters. Each "
        "one is documentation that was true once and silently stopped being true."
    )
else:
    st.success("No phantom parameters found in the selected packages.")

# --- per package ------------------------------------------------------------------------

st.subheader("By package")
frame["phantom_rate"] = frame.apply(
    lambda r: r["phantom"] / r["with_param_docs"] if r["with_param_docs"] else 0, axis=1
)
st.dataframe(
    frame[
        [
            "package",
            "files",
            "functions",
            "with_param_docs",
            "phantom",
            "undocumented",
            "phantom_rate",
        ]
    ]
    .sort_values("phantom", ascending=False)
    .rename(columns={"with_param_docs": "documented", "phantom_rate": "rate"}),
    hide_index=True,
    width="stretch",
)

left, right = st.columns(2)
with left:
    chart = (
        alt.Chart(frame)
        .mark_bar(color=RED)
        .encode(
            x=alt.X("package:N", sort="-y", title=None),
            y=alt.Y("phantom:Q", title="phantom parameters"),
            tooltip=["package", "phantom", "undocumented", "with_param_docs"],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")

with right:
    chart = (
        alt.Chart(frame)
        .mark_circle(size=200, color=BLUE, opacity=0.8)
        .encode(
            x=alt.X("with_param_docs:Q", title="functions documenting parameters"),
            y=alt.Y("phantom_rate:Q", title="phantom rate", axis=alt.Axis(format="%")),
            tooltip=[
                "package",
                "with_param_docs",
                "phantom",
                alt.Tooltip("phantom_rate:Q", format=".2%"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, width="stretch")

# --- the findings ---------------------------------------------------------------------------

st.subheader("Phantom parameters")
st.caption("A name the docstring documents that the signature does not contain.")
if len(phantom):
    st.dataframe(
        phantom[["package", "file", "line", "function", "name"]].reset_index(drop=True),
        hide_index=True,
        width="stretch",
        height=400,
    )
else:
    st.info("None in the selected packages.")

with st.expander(f"Undocumented parameters ({len(undoc)}) — a weaker signal"):
    st.caption(
        "A real parameter with no entry in a docstring that documents other "
        "parameters. Often deliberate, so it is reported separately and never counted "
        "toward the phantom rate."
    )
    if len(undoc):
        st.dataframe(
            undoc[["package", "file", "line", "function", "name"]].reset_index(drop=True),
            hide_index=True,
            width="stretch",
            height=300,
        )

st.divider()
st.caption(
    "Functions taking `*args` or `**kwargs` are excluded from phantom reporting - they "
    "can legitimately document names absent from the signature (numpy.einsum documents "
    "`dtype` and `casting`, both passed through `**kwargs`). `self` and `cls` are "
    "ignored on both sides."
)
