import re
import plain, cpp, makefile, python

syntax_list = [cpp, makefile, python, plain]
syntax_dict = dict((syntax.ident, syntax) for syntax in syntax_list)

def filename_syntax_re():
    patterns = []
    for syntax in syntax_list:
        ptn = "|".join(re.escape(ext).replace("\\*", ".*") for ext in syntax.extensions)
        ptn = "(?P<%s>^%s$)" % (syntax.ident, ptn)
        patterns.append(ptn)
    return re.compile("%s" % "|".join(patterns))

filename_syntax_re = filename_syntax_re()