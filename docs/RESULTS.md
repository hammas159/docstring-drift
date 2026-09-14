# Results

[<- back to README](../README.md)

Scanned the installed source of eight widely used packages. Every number here was produced
by `src/drift.py`; nothing is estimated.

## Full breakdown

| Package | files | functions | documenting params | **phantom** | undocumented | phantom rate |
|---|---:|---:|---:|---:|---:|---:|
| pandas | 1,421 | 28,295 | 1,653 | **40** | 187 | 2.42% |
| scipy | 988 | 24,004 | 1,953 | **27** | 1,015 | 1.38% |
| huggingface_hub | 183 | 1,937 | 399 | **13** | 49 | 3.26% |
| scikit-learn | 671 | 11,158 | 1,665 | **9** | 73 | 0.54% |
| numpy | 407 | 11,215 | 761 | **8** | 258 | 1.05% |
| altair | 55 | 2,507 | 118 | **3** | 12 | 2.54% |
| PIL | 97 | 1,228 | 205 | **1** | 13 | 0.49% |
| streamlit | 376 | 3,415 | 486 | **0** | 18 | 0.00% |
| **Total** | **4,198** | **83,759** | **7,240** | **101** | **1,625** | **1.40%** |

## What the two columns mean

**Phantom** - the docstring documents a name the signature does not contain. Almost always
a rename or a removal the docs missed. This is the headline number.

**Undocumented** - a real parameter with no entry in a docstring that documents the others.
Reported separately and **never counted toward the phantom rate**, because omitting a
parameter is frequently a deliberate choice.

## A verified example

`pandas/_testing/_io.py`, `round_trip_pickle`:

```python
def round_trip_pickle(obj, tmp_path):     # <- the parameter is tmp_path
    """
    Pickle an object and then read it again.

    Parameters
    ----------
    obj : any object
        The object to pickle and then re-read.
    path : str, path object or file-like object, default None    # <- documents `path`
        The path where the pickled object is written and then read.
    """
```

The parameter was renamed to `tmp_path`; the docstring still documents `path`.

This was checked by hand against the real source **before** the numbers in this repo were
published - because the first version of the scanner produced findings that looked
publishable and were not. See [PROBLEMS.md](PROBLEMS.md).

## Reproducing

```bash
python src/drift.py "path/to/site-packages/pandas"
streamlit run ui/app.py     # pick packages interactively
```

Results depend on the installed versions of the packages scanned. The raw output of the
run above is in [`results/scan.json`](../results/scan.json).
