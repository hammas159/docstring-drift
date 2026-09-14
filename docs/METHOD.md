# Method

[<- back to README](../README.md)

## The comparison

For every function that has a docstring **and** whose docstring documents at least one
parameter, compare two sets:

1. **Documented** - names the docstring claims are parameters
2. **Actual** - names in the signature, from the AST

A name in (1) but not (2) is a **phantom**. A name in (2) but not (1) is **undocumented**.

A docstring with no parameter section at all is skipped entirely: not documenting
parameters is a choice, not a defect.

## Docstring styles supported

| Style | Shape |
|---|---|
| **Google** | `Args:` then `name (type): description` |
| **NumPy** | `Parameters` / `----------` then `name : type` |
| **Sphinx** | `:param name:` or `:param type name:` |

All three are parsed from the same docstring, so a file mixing styles is handled.

## Where argument sections end

A parameter block ends at the next known section heading: `Returns`, `Yields`, `Raises`,
`Examples`, `Notes`, `See Also`, `References`, `Attributes`, `Warns`, `Warnings`, `Todo`.
Without this, entries in a `Returns:` block would be read as parameters.

## The indent rule

Parameter names sit at one fixed indent; their descriptions are indented further. The
parser records the indent of the first entry in a section and ignores anything deeper.

This is the single most important rule in the file. Without it, prose like `Default: None`
inside a description parses as a parameter named `Default` - which is how the first
version of this scanner "found" hundreds of phantom parameters across scipy that did not
exist.

## Signatures

Positional-only, positional, keyword-only, `*args` and `**kwargs` are all collected from
the AST. `self` and `cls` are dropped - and, importantly, dropped from the **docstring**
side too, so documenting `cls` does not register as a phantom.

## Catch-all exemption

A function taking `*args` or `**kwargs` is **exempt from phantom reporting**.

Such a function can legitimately document names absent from its signature: `numpy.einsum`
documents `dtype` and `casting`, both passed through `**kwargs`. Reporting those would be
a false positive.

This costs recall - drift in a kwargs-heavy API is invisible - and that trade is
deliberate. See [LIMITATIONS.md](LIMITATIONS.md).

## Determinism

No model, no embeddings, no random seed, no network, and nothing is imported from the code
being scanned. The same input always produces the same output, and scanning untrusted
third-party source is safe because nothing is executed.
