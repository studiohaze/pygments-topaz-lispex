import subprocess
import sys
import unittest
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import Comment, Error, Keyword, Name, Number, Operator
from pygments.token import Punctuation, String

from pygments_studiohaze import LispexLexer, TopazLexer

ROOT = Path(__file__).resolve().parents[1]


def tokens(lexer, source):
    return [(kind, value) for _, kind, value in lexer.get_tokens_unprocessed(source)]


class TopazTests(unittest.TestCase):
    def test_521_keywords_collection_heads_and_expected_markup(self):
        source = (ROOT / 'examples/keywords-521.tpz').read_text(encoding='utf-8')
        result = tokens(TopazLexer(), source)
        self.assertEqual(''.join(value for _, value in result), source)
        self.assertFalse(any(kind is Error for kind, _ in result))
        words = ('let mut const type function return if else match case for in by while '
                 'break continue defer concurrent true false null import export as record '
                 'enum newtype protocol impl derives loop using')
        for word in words.split():
            self.assertTrue(any(kind in Keyword and value == word for kind, value in result), word)
        for word in ['map', 'set']:
            self.assertEqual(sum(kind in Keyword and value == word for kind, value in result), 3)
        self.assertEqual(sum(kind is Name and value == 'map' for kind, value in result), 3)
        self.assertIn((Name, 'set'), result)
        for name in ['mapValue', 'setValue', 'map상태', 'set💎']:
            self.assertIn((Name, name), result)
        html = highlight(source, TopazLexer(), HtmlFormatter(nowrap=True))
        self.assertEqual(html, (ROOT / 'examples/keywords-521.expect.html').read_text(encoding='utf-8'))

    def test_non_nested_comment_closes_at_first_terminator(self):
        result = tokens(TopazLexer(), '/* outer /* inner */ let x = 1\n')
        self.assertEqual(''.join(v for t, v in result if t in Comment),
                         '/* outer /* inner */')
        self.assertIn((Keyword, 'let'), result)

    def test_strings_hide_comments_and_interpolate_expressions(self):
        result = tokens(TopazLexer(), '"// text {1 + 2} \\{literal\\}"')
        self.assertFalse(any(t in Comment for t, _ in result))
        self.assertIn((String.Interpol, '{'), result)
        self.assertIn((Number.Integer, '1'), result)
        self.assertIn((String.Escape, '\\{'), result)

    def test_nested_interpolation_braces_and_nested_string(self):
        source = '"value {Task {title: "inner {1 + 2}"}.title}"'
        result = tokens(TopazLexer(), source)
        self.assertEqual(''.join(v for _, v in result), source)
        self.assertFalse(any(t is Error for t, _ in result))
        self.assertEqual(sum(t is String.Interpol and v == '}' for t, v in result), 2)
        self.assertIn((Punctuation, '}'), result)

    def test_triple_strings_and_all_template_tags(self):
        for tag in ['', 'p', 'r', 'sh', 'sql']:
            with self.subTest(tag=tag):
                result = tokens(TopazLexer(), tag + '"""\ntext {value}\n"""')
                self.assertFalse(any(t is Error for t, _ in result))
                self.assertIn((String.Double, '"""'), result)
                if tag:
                    self.assertIn((String.Affix, tag), result)

    def test_unicode_and_emoji_names_are_not_keyword_prefixes(self):
        result = tokens(TopazLexer(), 'let 상태 = 1\nlet💎 true💎 _internal 💎x')
        for value in ['상태', 'let💎', 'true💎', '_internal', '💎x']:
            self.assertIn((Name, value), result)

    def test_numeric_bases_separators_and_float(self):
        result = tokens(TopazLexer(), '0XFF_FF 0b10_01 1_000 2.5 1..3')
        for item in [(Number.Hex, '0XFF_FF'), (Number.Bin, '0b10_01'),
                     (Number.Integer, '1_000'), (Number.Float, '2.5'),
                     (Operator, '..')]:
            self.assertIn(item, result)

    def test_declaration_names(self):
        result = tokens(TopazLexer(), 'function double(n: int) -> int { n * 2 }\nrecord Task {}')
        self.assertIn((Name.Function, 'double'), result)
        self.assertIn((Name.Class, 'Task'), result)


class LispexTests(unittest.TestCase):
    def test_nested_comments_end_at_matching_terminator(self):
        source = '#| outer #| inner |# still outer |# (define x 1)'
        result = tokens(LispexLexer(), source)
        self.assertEqual(''.join(v for t, v in result if t in Comment),
                         '#| outer #| inner |# still outer |#')
        self.assertIn((Keyword, 'define'), result)

    def test_exact_numbers_consume_whole_atoms(self):
        result = tokens(LispexLexer(), '1/3 -5/2 1.5 1e3 -2 +5 01 1/0 #x10')
        for item in [(Number, '1/3'), (Number, '-5/2'), (Number.Float, '1e3'),
                     (Number.Integer, '-2'), (Name, '+5'), (Name, '01'),
                     (Name, '1/0'), (Name, '#x10')]:
            self.assertIn(item, result)

    def test_characters_do_not_start_comments_or_strings(self):
        source = r'(list #\; #\" #\space #\x41 #\상) ; comment'
        result = tokens(LispexLexer(), source)
        for value in ['#\\;', '#\\"', '#\\space', '#\\x41', '#\\상']:
            self.assertIn((String.Char, value), result)
        self.assertEqual(''.join(v for t, v in result if t in Comment), '; comment')

    def test_strings_and_hex_escapes(self):
        result = tokens(LispexLexer(), r'"; #| text \x41; \""')
        self.assertFalse(any(t in Comment for t, _ in result))
        self.assertIn((String.Escape, '\\x41;'), result)

    def test_booleans_quote_vectors_and_names(self):
        result = tokens(LispexLexer(), "(list #true #f 'if #(1 2) #u8(65) else let*)")
        for item in [(Keyword.Constant, '#true'), (Keyword.Constant, '#f'),
                     (String.Symbol, 'if'), (Name, 'else'), (Keyword, 'let*')]:
            self.assertIn(item, result)


class PluginTests(unittest.TestCase):
    def test_installed_entry_points_and_filename_discovery(self):
        for alias in ['topaz', 'tpz', 'topaz-studiohaze']:
            self.assertIsInstance(get_lexer_by_name(alias), TopazLexer)
        for alias in ['lispex', 'lspx']:
            self.assertIsInstance(get_lexer_by_name(alias), LispexLexer)
        self.assertIsInstance(get_lexer_for_filename('example.tpz'), TopazLexer)
        self.assertIsInstance(get_lexer_for_filename('example.lspx'), LispexLexer)

    def test_complete_previously_cli_verified_examples(self):
        for name, lexer in [('topaz.tpz', TopazLexer()), ('lispex.lspx', LispexLexer())]:
            with self.subTest(name=name):
                source = (ROOT / 'examples' / name).read_text(encoding='utf-8')
                result = tokens(lexer, source)
                self.assertEqual(''.join(v for _, v in result), source)
                self.assertFalse(any(t is Error for t, _ in result))
                self.assertIn('<span', highlight(source, lexer, HtmlFormatter()))

    def test_real_pygmentize_cli_for_both_extensions(self):
        for name in ['topaz.tpz', 'lispex.lspx']:
            with self.subTest(name=name):
                result = subprocess.run([sys.executable, '-m', 'pygments', '-f', 'html',
                                         str(ROOT / 'examples' / name)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('<span', result.stdout)

    def test_unterminated_comments_remain_bounded_and_preserve_text(self):
        for lexer, source in [(TopazLexer(), '/*' + '*' * 20000),
                              (LispexLexer(), '#|' * 1000 + 'text')]:
            result = tokens(lexer, source)
            self.assertEqual(''.join(v for _, v in result), source)
            self.assertTrue(all(t in Comment for t, _ in result))


if __name__ == '__main__':
    unittest.main()
