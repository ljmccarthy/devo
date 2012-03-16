import wx.stc

ident = "c"
name = "C/C++"
extensions = ["*.c", "*.cpp", "*.cxx", "*.cc", "*.h", "*.hpp", "*.hxx"]
lexer = wx.stc.STC_LEX_CPP
indent = 4
use_tabs = False
comment_token = "//"

stylespecs = (
    (wx.stc.STC_STYLE_DEFAULT,            ""),
    (wx.stc.STC_STYLE_LINENUMBER,         "back:#C0C0C0"),
    (wx.stc.STC_STYLE_BRACELIGHT,         "fore:#FFFFFF,back:#0000FF,bold"),
    (wx.stc.STC_STYLE_BRACEBAD,           "fore:#000000,back:#FF0000,bold"),
    (wx.stc.STC_C_CHARACTER,              "fore:#7F007F"),
    (wx.stc.STC_C_COMMENT,                "fore:#7F7F7F"),
    (wx.stc.STC_C_COMMENTDOC,             "fore:#7F7F7F"),
    (wx.stc.STC_C_COMMENTDOCKEYWORD,      "fore:#7F7F7F"),
    (wx.stc.STC_C_COMMENTDOCKEYWORDERROR, "fore:#7F7F7F"),
    (wx.stc.STC_C_COMMENTLINE,            "fore:#7F7F7F"),
    (wx.stc.STC_C_COMMENTLINEDOC,         "fore:#7F7F7F"),
    (wx.stc.STC_C_DEFAULT,                "fore:#000000"),
    (wx.stc.STC_C_GLOBALCLASS,            "fore:#000000"),
    (wx.stc.STC_C_IDENTIFIER,             "fore:#000000"),
    (wx.stc.STC_C_NUMBER,                 "fore:#007F7F"),
    (wx.stc.STC_C_OPERATOR,               "bold"),
    (wx.stc.STC_C_PREPROCESSOR,           "fore:#007F7F"),
    (wx.stc.STC_C_REGEX,                  "fore:#000000"),
    (wx.stc.STC_C_STRING,                 "fore:#7F007F"),
    (wx.stc.STC_C_STRINGEOL,              "fore:#000000,back:#E0C0E0,eol"),
    (wx.stc.STC_C_UUID,                   "fore:#000000"),
    (wx.stc.STC_C_UUID,                   "fore:#000000"),
    (wx.stc.STC_C_VERBATIM,               "fore:#000000"),
    (wx.stc.STC_C_WORD,                   "fore:#00007F,bold"),
    (wx.stc.STC_C_WORD2,                  "fore:#00007F,bold"),
)

keywords = """\
asm
auto
break
bool
_Bool
case
catch
char
class
_Complex
const
const_cast
continue
default
delete
do
double
dynamic_cast
else
enum
explicit
export
extern
false
float
for
friend
goto
if
_Imaginary
inline
int
long
mutable
namespace
new
operator
private
protected
public
register
reinterpret_cast
restrict
return
short
signed
sizeof
static
static_cast
struct
switch
template
this
throw
true
try
typedef
typeid
typename
typeof
union
unsigned
using
virtual
void
volatile
wchar_t
while
"""
