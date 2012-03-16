import wx.stc

ident = "py"
name = "Python"
extensions = ["*.py"]
lexer = wx.stc.STC_LEX_PYTHON
indent = 4
use_tabs = False
comment_token = "#"

stylespecs = (
    (wx.stc.STC_STYLE_DEFAULT,    ""),
    (wx.stc.STC_STYLE_LINENUMBER, "back:#C0C0C0"),
    (wx.stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold"),
    (wx.stc.STC_STYLE_BRACEBAD,   "fore:#000000,back:#FF0000,bold"),
    (wx.stc.STC_P_DEFAULT,        "fore:#000000"),
    (wx.stc.STC_P_COMMENTLINE,    "fore:#007F00"),
    (wx.stc.STC_P_NUMBER,         "fore:#007F7F"),
    (wx.stc.STC_P_STRING,         "fore:#7F007F"),
    (wx.stc.STC_P_CHARACTER,      "fore:#7F007F"),
    (wx.stc.STC_P_WORD,           "fore:#00007F,bold"),
    (wx.stc.STC_P_TRIPLE,         "fore:#7F0000"),
    (wx.stc.STC_P_TRIPLEDOUBLE,   "fore:#7F0000"),
    (wx.stc.STC_P_CLASSNAME,      "fore:#0000FF,bold"),
    (wx.stc.STC_P_DEFNAME,        "fore:#007F7F,bold"),
    (wx.stc.STC_P_OPERATOR,       "bold"),
    (wx.stc.STC_P_IDENTIFIER,     "fore:#000000"),
    (wx.stc.STC_P_COMMENTBLOCK,   "fore:#7F7F7F"),
    (wx.stc.STC_P_STRINGEOL,      "fore:#000000,back:#E0C0E0,eol"),
)

keywords = """\
and
as
assert
break
class
continue
def
del
elif
else
except
exec
finally
for
from
global
if
import
in
is
lambda
None
not
or
pass
print
raise
return
try
while
with
yield
True
False
"""
