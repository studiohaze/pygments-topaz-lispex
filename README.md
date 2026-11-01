# Topaz and Lispex for Pygments

Pygments lexers for [Topaz](https://topaz.ooo/) and [Lispex](https://www.lispex.com/), from STUDIO HAZE. They use the standard Pygments token types, so existing styles work.

## Install

```sh
python -m pip install git+https://github.com/studiohaze/pygments-topaz-lispex.git
pygmentize -l topaz -f html example.tpz > example.html
pygmentize -l lispex -f html example.lspx > example.html
```

The package registers `topaz`, `tpz`, `topaz-studiohaze`, `lispex` and `lspx`, and recognizes `.tpz` and `.lspx` files. Tools that discover Pygments plugins, such as Sphinx, pick up the same names after installation.

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

html = highlight(source, get_lexer_by_name("lispex"), HtmlFormatter())
```

The Topaz lexer covers line and block comments, Unicode names, double and triple-quoted strings, the `p`, `r`, `sh` and `sql` template tags, and expressions inside `{...}` interpolation. The Lispex lexer covers nested block comments, semicolon comments, strings and characters, exact rational numbers, booleans, vectors, bytevectors and quotation.

## Develop

```sh
python -m pip install .
python -m unittest discover -s tests -v
```

## Links

- [Topaz documentation](https://topaz.ooo/en/docs)
- [Topaz source](https://github.com/studiohaze/topaz)
- [Topaz lexical structure](https://topaz.ooo/v5.21/en/docs/language/lexical-layout)
- [Topaz strings and templates](https://topaz.ooo/v5.21/en/docs/language/strings-templates)
- [Lispex documentation](https://www.lispex.com/en/docs)
- [Lispex reader grammar](https://www.lispex.com/v1.21/en/docs/reference/reader-grammar)
- [Lispex numbers](https://www.lispex.com/v1.21/en/docs/manual/numbers)

## License

BSD-2-Clause
