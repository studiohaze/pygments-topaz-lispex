"""Highlight public Topaz 5.21 and Lispex 1.21 syntax, without executing it."""

import re

from pygments.lexer import RegexLexer, bygroups, include, words
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation
from pygments.token import String, Whitespace


# Python's Unicode word classes cover letters and digits. Emoji are also valid
# Topaz name characters; these ranges keep their source spelling intact.
_EMOJI = r"\u2600-\u27bf\U0001f000-\U0001faff"
_IDENTIFIER = rf"(?:[^\W\d]|[{_EMOJI}])(?:\w|[{_EMOJI}\ufe0f\u200d])*"
_NAME_END = rf"(?![\w{_EMOJI}\ufe0f\u200d])"
_DECIMAL = r"[0-9](?:_?[0-9])*"


class TopazLexer(RegexLexer):
    """STUDIO HAZE's Topaz, distinct from other languages named Topaz."""

    name = "Topaz"
    aliases = ["topaz", "tpz", "topaz-studiohaze"]
    filenames = ["*.tpz"]
    url = "https://topaz.ooo/"
    flags = re.MULTILINE

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            include("comments"),
            (r'(p|r|sh|sql)(""")', bygroups(String.Affix, String.Double), "triple"),
            (r'(p|r|sh|sql)(")', bygroups(String.Affix, String.Double), "string"),
            (r'"""', String.Double, "triple"),
            (r'"', String.Double, "string"),
            (r"0[xX][0-9a-fA-F](?:_?[0-9a-fA-F])*", Number.Hex),
            (r"0[bB][01](?:_?[01])*", Number.Bin),
            (rf"{_DECIMAL}\.{_DECIMAL}", Number.Float),
            (_DECIMAL, Number.Integer),
            (rf"(function)(\s+)({_IDENTIFIER})",
             bygroups(Keyword.Declaration, Whitespace, Name.Function)),
            (rf"(record|enum|type|newtype|protocol)(\s+)({_IDENTIFIER})",
             bygroups(Keyword.Declaration, Whitespace, Name.Class)),
            (words(("import", "export", "as", "let", "mut", "const", "function",
                    "return", "if", "else", "match", "case", "for", "in", "by", "while",
                    "break", "continue", "record", "enum", "type", "newtype",
                    "protocol", "impl", "derives", "defer", "concurrent", "loop", "using"),
                   suffix=_NAME_END), Keyword),
            (r"(?<!\.)(?:map|set)(?=[ \t]*\{)", Keyword),
            (words(("true", "false", "null", "None"), suffix=_NAME_END), Keyword.Constant),
            (words(("int", "float", "bool", "string", "template", "Array", "Map",
                    "Set", "Option", "Result"), suffix=_NAME_END), Keyword.Type),
            (words(("Some", "Ok", "Err"), suffix=_NAME_END), Name.Builtin),
            (_IDENTIFIER, Name),
            (r"\.\.<|\.\.\.|\.\.|\?\.|=>|->|\|>|==|!=|<=|>=|&&|\|\||[+*/%=<>!&|?~-]", Operator),
            (r"[{}\[\](),.:;]", Punctuation),
        ],
        "comments": [
            (r"//[^\n]*", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
        ],
        # A second /* is text. The first */ always ends a Topaz block comment.
        "comment": [
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[^*]+", Comment.Multiline),
            (r"\*", Comment.Multiline),
        ],
        "escapes": [(r"\\.", String.Escape)],
        "string": [
            (r'"', String.Double, "#pop"),
            include("escapes"),
            (r"\{", String.Interpol, "interpolation"),
            (r'[^"\\{]+', String.Double),
        ],
        "triple": [
            (r'"""', String.Double, "#pop"),
            include("escapes"),
            (r"\{", String.Interpol, "interpolation"),
            (r'[^"\\{]+', String.Double),
            (r'"', String.Double),
        ],
        "interpolation": [
            (r"\}", String.Interpol, "#pop"),
            (r"\{", Punctuation, "interpolation-brace"),
            include("root"),
        ],
        "interpolation-brace": [
            (r"\}", Punctuation, "#pop"),
            (r"\{", Punctuation, "#push"),
            include("root"),
        ],
    }


_LISPEX_KEYWORDS = frozenset((
    "quote", "quasiquote", "unquote", "unquote-splicing", "lambda", "if",
    "begin", "set!", "define", "let", "let*", "letrec", "cond", "case", "guard",
    "and", "or", "when", "unless", "do", "module", "export", "import",
))
_LISPEX_BUILTINS = frozenset((
    "values", "call-with-values", "call/cc", "dynamic-wind", "+", "-", "*", "/",
    "=", "<", ">", "<=", ">=", "cons", "car", "cdr", "list", "map", "apply",
    "error", "error-object?", "error-object-message", "number?", "string?",
    "boolean?", "pair?", "null?", "vector", "vector-ref", "bytevector-u8-ref",
    "display", "newline",
))
_LISPEX_INTEGER = r"-?(?:0|[1-9][0-9]*)"


def _lispex_atom(lexer, match):
    value = match.group()
    if value in ("#t", "#f", "#true", "#false"):
        token = Keyword.Constant
    elif re.fullmatch(_LISPEX_INTEGER + r"/[1-9][0-9]*", value):
        token = Number
    elif re.fullmatch(_LISPEX_INTEGER, value):
        token = Number.Integer
    elif re.fullmatch(_LISPEX_INTEGER + r"(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?", value):
        token = Number.Float
    elif value in _LISPEX_KEYWORDS:
        token = Keyword
    elif value in _LISPEX_BUILTINS:
        token = Name.Builtin
    elif value == ".":
        token = Punctuation
    else:
        token = Name
    yield match.start(), token, value


class LispexLexer(RegexLexer):
    """Lispex's Scheme-family notation, including exact rational literals."""

    name = "Lispex"
    aliases = ["lispex", "lspx"]
    filenames = ["*.lspx"]
    url = "https://www.lispex.com/"

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r";[^\n]*", Comment.Single),
            (r"#\|", Comment.Multiline, "comment"),
            # The single-character alternative includes delimiters such as #\;.
            (r'''\#\\(?:[^\s()'`,;"]+|[^\s])''', String.Char),
            (r'"', String.Double, "string"),
            (r"#(?:u8)?(?=\()", Punctuation),
            (r"[()]", Punctuation),
            (r'''(')([^\s()'`,;"]+)''', bygroups(Operator, String.Symbol)),
            (r",@|['`,]", Operator),
            (r'''[^\s()'`,;"]+''', _lispex_atom),
        ],
        "comment": [
            (r"#\|", Comment.Multiline, "#push"),
            (r"\|#", Comment.Multiline, "#pop"),
            (r"[^#|]+", Comment.Multiline),
            (r"[#|]", Comment.Multiline),
        ],
        "string": [
            (r'"', String.Double, "#pop"),
            (r"\\x[0-9a-fA-F]+;|\\.", String.Escape),
            (r'[^"\\]+', String.Double),
        ],
    }
