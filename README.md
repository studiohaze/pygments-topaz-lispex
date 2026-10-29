# Topaz and Lispex for Pygments

Pygments lexers for [Topaz](https://topaz.ooo/) and
[Lispex](https://www.lispex.com/), developed by STUDIO HAZE.
This is STUDIO HAZE's Topaz, distinct from m-schm's unrelated Topaz language.

This package provides highlighting rules for public language syntax. It does
not contain either language's compiler or interpreter. Highlighting does not
validate or execute a program. The lexers use standard Pygments token types
and work with existing styles.

## Install from GitHub

```sh
python -m pip install git+https://github.com/studiohaze/pygments-topaz-lispex.git
pygmentize -l topaz -f html example.tpz > example.html
pygmentize -l lispex -f html example.lspx > example.html
```

The package registers `topaz`, `tpz`, `topaz-studiohaze`, `lispex`, and `lspx`.
Filename lookup recognizes `.tpz` and `.lspx`. Applications that discover
Pygments entry points, such as Sphinx, can use the same names after installation.

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

html = highlight(source, get_lexer_by_name("lispex"), HtmlFormatter())
```

Topaz rules include non-nested block comments, line comments, Unicode names,
double and triple-quoted strings, the `p`/`r`/`sh`/`sql` template tags, and
nested expressions inside `{...}` interpolation. Lispex rules include nested
block comments, semicolon comments, strings and characters, exact rational
numbers, booleans, vectors, bytevectors, and quotation.

## Development

```sh
python -m pip install .
python -m unittest discover -s tests -v
```

Tests cover token boundaries, comments inside strings, interpolation nesting,
numeric/symbol distinctions, plugin discovery, HTML output, and complete
examples previously run with official Topaz 5.21.0 (Rust reference compiler)
and Lispex 1.21.1. The lexer tests do not rerun those language implementations.
AI assistance was used to prepare this package from the public references below.

## References

- [Topaz lexical structure](https://topaz.ooo/v5.21/en/docs/language/lexical-layout)
- [Topaz strings and templates](https://topaz.ooo/v5.21/en/docs/language/strings-templates)
- [Lispex reader grammar](https://www.lispex.com/v1.21/en/docs/reference/reader-grammar)
- [Lispex numbers](https://www.lispex.com/v1.21/en/docs/manual/numbers)
- [Lispex reserved forms](https://www.lispex.com/v1.21/en/docs/reference/reserved-and-forbidden)
- [Pygments plugin documentation](https://pygments.org/docs/plugins/)

Topaz's public source snapshot and bootstrap seed are separate distributions.
Lispex's core implementation repository is private; this package does not
publish it. This plugin is distributed separately from Pygments core.

## License

BSD-2-Clause; see [LICENSE](LICENSE).
