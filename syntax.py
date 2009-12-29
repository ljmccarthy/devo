import re

import syntax_c
import syntax_makefile
import syntax_py

syntax_list = [syntax_c, syntax_makefile, syntax_py]
syntax_dict = dict((syntax.ident, syntax) for syntax in syntax_list)

def filename_syntax_re():
    patterns = []
    for syntax in syntax_list:
        ptn = "|".join("^%s$" % re.escape(ext).replace("\\*", ".*") for ext in syntax.extensions)
        ptn = "(?P<%s>%s)" % (syntax.ident, ptn)
        patterns.append(ptn)
    return re.compile("%s" % "|".join(patterns))

filename_syntax_re = filename_syntax_re()
