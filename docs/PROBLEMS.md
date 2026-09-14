# Problems hit while building this

[<- back to README](../README.md)

**The first version reported roughly 400 phantom parameters in scipy alone, and almost
none were real.** Finding and removing those was most of the work on this project.

## 1. Prose parsed as parameters

`Default: None` inside a description matched the name pattern and became a parameter
called `Default`. So did `Note:`, `Example:`, and any sentence starting with a capitalised
word followed by a colon.

**This alone caused most of the scipy noise.**

**Fix:** track the indent of the first entry in a section. Parameter names sit at one
indent; descriptions are indented further, so anything deeper is skipped.

**Test:** `test_prose_in_a_description_is_not_a_parameter`

## 2. Catch-all signatures

`numpy.einsum` documents `dtype` and `casting`. Neither appears in its signature - both
are passed through `**kwargs`. The scanner reported both as phantom. So did
`pandas.set_option`, which takes `*args`.

**Fix:** functions taking `*args` or `**kwargs` are exempt from phantom reporting.

**Tests:** `test_kwargs_function_does_not_report_phantoms`,
`test_vararg_function_does_not_report_phantoms`

## 3. self / cls asymmetry

`self` and `cls` were stripped from signatures but not from docstrings, so any docstring
documenting `cls` produced a phantom.

**Fix:** ignored on both sides.

**Test:** `test_self_and_cls_are_never_parameters`

## 4. Trusting the first run

The initial numbers looked plausible and publishable. They were wrong.

What caught it was reading the *output* rather than the total: `Default` is not a credible
parameter name, and seeing it repeatedly was the signal that the parser - not scipy - was
at fault.

**Fix in process, not code:** a finding was verified by hand against real source before any
number was written down. That is how the pandas `round_trip_pickle` case was confirmed.

## The effect of the fixes

| Package | before | after |
|---|---:|---:|
| scipy | 434 | **27** |
| pandas | 106 | **40** |
| numpy | 55 | **8** |

The numbers in this repository are the post-fix ones.
