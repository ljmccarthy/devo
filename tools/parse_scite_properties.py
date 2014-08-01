# Parse SciTE properties files into something more reasonable.
# This is an awful hack, may $DEITY forgive me.

import sys
import os
import re
import wx.stc

ignored_line_re = re.compile(r"^([#\t ]|[^=]*$)")

var_reference_re = re.compile(r"\$\(([^)]+)\)")

def expand_variables(value, props):
    seen_vars = set()
    while var_reference_re.search(value):
        parts = []
        last_index = 0
        for m in var_reference_re.finditer(value):
            if m.start() > last_index:
                parts.append(value[last_index:m.start()])
            last_index = m.end()
            var_name = m.group(1).lower()
            if var_name not in seen_vars:
                seen_vars.add(var_name)
                parts.append(props.get(m.group(1).lower(), ""))
        if last_index < len(value):
            parts.append(value[last_index:])
        value = "".join(parts)
    return value

def expand_lhs(name, props):
    name = name.lower()
    m = var_reference_re.search(name)
    if m:
        prefix = name[:m.start()]
        suffix = name[m.end():]
        if m.group(1) not in props:
            return []
        patterns = expand_variables(props[m.group(1)], props).split(";")
        return [prefix + pattern + suffix for pattern in patterns]
    else:
        return [name]

class Properties(dict):
    def __init__(self, *args, **kwargs):
        super(Properties, self).__init__(*args, **kwargs)
        self.sorted_keys = self.keys()
        self.sorted_keys.sort()

    def find_prefix_keys(self, prefix):
        for key in self.sorted_keys:
            if key.startswith(prefix):
                yield key[len(prefix):]

    def find_prefix(self, prefix):
        for key in self.sorted_keys:
            if key.startswith(prefix):
                yield key[len(prefix):], self[key]

def parse_scite_properties(s):
    lines = s.replace("\\\n", "").split("\n")
    lines = [line for line in lines if line.strip() and not ignored_line_re.match(line)]
    props = {}
    for line in lines:
        name, value = line.split("=", 1)
        props[name] = value
    for name, value in props.items():
        value = expand_variables(value, props)
        for name in expand_lhs(name, props):
            props[name] = value
    return Properties(props)

stc_names = frozenset(dir(wx.stc))

known_lexers = {
    "inno": "STC_LEX_INNOSETUP",
    "php": "STC_LEX_PHPSCRIPT",
    "sorcins": "STC_LEX_SORCUS",
}

def find_lexer(props, lang_id, file_pattern):
    lexer_id = ""
    if lang_id in known_lexers:
        return (lang_id, known_lexers[lang_id])
    lexer_id = props["lexer.%s" % file_pattern]
    lexer_stc = "STC_LEX_" + lexer_id.upper()
    if lexer_stc in stc_names:
        return (lexer_id, lexer_stc)
    return ("", "")

def find_style_specs(props, lexer_id):
    for style_num, style_spec in props.find_prefix("style.%s." % lexer_id):
        yield int(style_num), style_spec

class Language(object):
    def __init__(self, lang_id, props):
        self.id = lang_id

        filter_parts = props["filter.%s" % lang_id].split("|")[:2]
        self.name = filter_parts[0].split("(", 1)[0].strip()
        self.file_patterns = filter_parts[1].split(";")

        self.lexer_id, self.lexer = find_lexer(props, lang_id, self.file_patterns[0])
        self.style_specs = sorted(find_style_specs(props, self.lexer_id))

ignored_languages = ["text", "properties", "rust", "web"]

def convert_props(props):
    langs = []
    for lang_id in props.find_prefix_keys("filter."):
        if lang_id not in ignored_languages:
            lang = Language(lang_id, props)
            if lang.lexer:
                langs.append(lang)
            else:
                sys.exit("error: unknown lexer: %s %s" % (lang.id, lang.file_patterns))

    return langs

def parse_scite_properties_file(filename):
    with open(filename) as f:
        s = f.read()
    props = parse_scite_properties(s)
    return convert_props(props)

def parse_scite_properties_dir(path):
    langs = []
    for filename in os.listdir(path):
        if filename.endswith(".properties"):
            filepath = os.path.join(path, filename)
            langs.extend(parse_scite_properties_file(filepath))
    return langs

if __name__ == "__main__":
    #langs = parse_scite_properties_dir("/home/shaurz/scite/src")
    langs = parse_scite_properties_file("/home/shaurz/scite/src/Embedded.properties")

    for lang in langs:
        print lang.id, lang.lexer, repr(lang.name)
        for spec in lang.style_specs:
            print " ", spec
