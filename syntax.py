import os.path
import re
from wx import stc

from sci_lexer_map import sci_lexer_map

class Syntax(object):
    def __init__(self, name, description, lexer, file_patterns, comment_token="",
                 keywords="", indent_width=4, tab_width=8, use_tabs=False):
        self.name = name
        self.description = description
        self.lexer = lexer
        self.file_patterns = file_patterns
        self.comment_token = comment_token
        self.indent_width = indent_width
        self.tab_width = tab_width
        self.use_tabs = use_tabs
        self.keywords = keywords

    def get_style_specs(self, theme):
        if self.lexer in sci_lexer_map:
            lexer_constants = sci_lexer_map[self.lexer]
            for token_type_name, style_spec in theme:
                if token_type_name in lexer_constants:
                    yield (lexer_constants[token_type_name], style_spec)

keywords_c = """\
auto break case char const continue default do double else enum extern float
for goto if inline int long register restrict return short signed sizeof
static struct switch typedef union unsigned void volatile while _Alignas
_Alignof _Atomic _Bool _Complex _Generic _Imaginary _Noreturn _Static_assert
_Thread_local"""

keywords_cpp = """\
alignas alignof and and_eq asm auto bitand bitor bool break case catch char
char16_t char32_t class compl const constexpr const_cast continue decltype
default delete do double dynamic_cast else enum explicit export extern false
float for friend goto if inline int long mutable namespace new noexcept not
not_eq nullptr operator or or_eq private protected public register
reinterpret_cast return short signed sizeof static static_assert static_cast
struct switch template this thread_local throw true try typedef typeid typename
union unsigned using virtual void volatile wchar_t while xor xor_eq"""

keywords_java = """\
abstract continue for new switch assert default goto package synchronized
boolean do if private this break double implements protected throw byte else
import public throws case enum instanceof return transient catch extends int
short try char final interface static void class finally long strictfp volatile
const float native super while"""

keywords_python = """\
and as assert break class continue def del elif else except exec finally for
from global if import in is lambda not or pass print raise return try
while with yield None True False"""

syntax_plain = Syntax("plain", "Plain Text", stc.STC_LEX_NULL, "*")

syntax_list = [
    Syntax("c", "C", stc.STC_LEX_CPP, "*.c;*.h", "//", keywords_c),
    Syntax("cpp", "C++", stc.STC_LEX_CPP, "*.cpp;*.cxx;*.cc;*.hpp;*.hxx;*.hh", "//", keywords_cpp),
    Syntax("objc", "Objective-C", stc.STC_LEX_CPP, "*.m", "//", keywords_c),
    Syntax("objcpp", "Objective-C++", stc.STC_LEX_CPP, "*.mm", "//", keywords_cpp),
    Syntax("java", "Java", stc.STC_LEX_CPP, "*.java", "//", keywords_java),
    Syntax("python", "Python", stc.STC_LEX_PYTHON, "*.py", "#", keywords_python),
    Syntax("html", "HTML", stc.STC_LEX_HTML, "*.html;*.htm"),
    Syntax("sgml", "SGML", stc.STC_LEX_HTML, "*.sgml"),
    Syntax("xml", "XML", stc.STC_LEX_XML, "*.xml;*.xslt;*.rdf;*.rss;*.atom"),
    Syntax("makefile", "Makefile", stc.STC_LEX_MAKEFILE, "Makefile*;makefile*;GNUmakefile*;*.mk", "#",
           indent_width = 8, tab_width = 8, use_tabs = True),
    syntax_plain,
]

syntax_dict = dict((syntax.name, syntax) for syntax in syntax_list)

def filename_syntax_re():
    patterns = []
    for syntax in syntax_list:
        ptn = "|".join(re.escape(ext).replace("\\*", ".*") for ext in syntax.file_patterns.split(";"))
        ptn = "(?P<%s>^(%s)$)" % (syntax.name, ptn)
        patterns.append(ptn)
    return re.compile("%s" % "|".join(patterns))

filename_syntax_re = filename_syntax_re()

def syntax_from_filename(filename):
    return syntax_dict[filename_syntax_re.match(os.path.basename(filename)).lastgroup]
