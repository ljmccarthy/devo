import re
import plain, cpp, makefile, python, java

syntax_list = [cpp, makefile, python, java, plain]
syntax_dict = dict((syntax.ident, syntax) for syntax in syntax_list)

def filename_syntax_re():
    patterns = []
    for syntax in syntax_list:
        ptn = "|".join(re.escape(ext).replace("\\*", ".*") for ext in syntax.extensions)
        ptn = "(?P<%s>^(%s)$)" % (syntax.ident, ptn)
        patterns.append(ptn)
    return re.compile("%s" % "|".join(patterns))

filename_syntax_re = filename_syntax_re()

def syntax_from_filename(filename):
    return syntax_dict[filename_syntax_re.match(filename).lastgroup]
