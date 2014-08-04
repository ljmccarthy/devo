# Map generic token type string to STC lexer constants.
# The entry for STC_LEX_NULL is a template containing all possible token types.

from wx import stc

lexer_token_description = {
    "assembly":     "Assembly Code",
    "character":    "Character",
    "comment":      "Block Comment",
    "commentline":  "Line Comment",
    "decorator":    "Decorator",
    "default":      "Default",
    "defclass":     "Defined Class Name",
    "defun":        "Defined Function Name",
    "defmodule":    "Defined Module Name",
    "diffadded":    "Diff Added",
    "diffchanged":  "Diff Changed",
    "diffdeleted":  "Diff Deleted",
    "diffheader":   "Diff Header",
    "diffposition": "Diff Position",
    "error":        "Error",
    "identifier":   "Identifier",
    "keyword":      "Keyword",
    "label":        "Label",
    "math":         "Inline Math",
    "mathblock":    "Math Block",
    "number":       "Number",
    "operator":     "Operator",
    "preprocessor": "Preprocessor",
    "reference":    "Variable Reference",
    "regex":        "Regular Expression",
    "string":       "String",
    "stringblock":  "Block String",
    "stringeol":    "Unterminated String",
    "stringref":    "Variable Reference In String",
    "symbol":       "Symbol",
    "tag":          "Tag",
    "tagattribute": "Tag Attribute",
}

lexer_tokens_html = {
    "comment":      [stc.STC_H_COMMENT, stc.STC_H_XCCOMMENT, stc.STC_H_SGML_1ST_PARAM_COMMENT, stc.STC_H_SGML_COMMENT, stc.STC_HPHP_COMMENT, stc.STC_HJ_COMMENT, stc.STC_HJ_COMMENTDOC],
    "commentline":  [stc.STC_HPHP_COMMENTLINE, stc.STC_HJ_COMMENTLINE],
    "default":      [stc.STC_H_DEFAULT, stc.STC_H_SGML_1ST_PARAM, stc.STC_H_SGML_DEFAULT, stc.STC_H_SGML_BLOCK_DEFAULT, stc.STC_H_SGML_SPECIAL, stc.STC_HPHP_DEFAULT, stc.STC_HJ_DEFAULT],
    "error":        [stc.STC_H_SGML_ERROR],
    "keyword":      [stc.STC_HPHP_WORD, stc.STC_HJ_KEYWORD, stc.STC_HJ_WORD],
    "number":       [stc.STC_H_NUMBER, stc.STC_H_VALUE, stc.STC_HPHP_NUMBER, stc.STC_HPHP_OPERATOR, stc.STC_HJ_NUMBER],
    "operator":     [stc.STC_HJ_SYMBOLS],
    "reference":    [stc.STC_HPHP_VARIABLE],
    "regex":        [stc.STC_HJ_REGEX],
    "string":       [stc.STC_H_DOUBLESTRING, stc.STC_H_SINGLESTRING, stc.STC_H_SGML_DOUBLESTRING, stc.STC_H_SGML_SIMPLESTRING,stc.STC_HPHP_HSTRING, stc.STC_HPHP_SIMPLESTRING, stc.STC_HJ_DOUBLESTRING, stc.STC_HJ_SINGLESTRING],
    "stringblock":  [stc.STC_H_CDATA],
    "stringeol":    [stc.STC_HJ_STRINGEOL],
    "stringref":    [stc.STC_HPHP_COMPLEX_VARIABLE, stc.STC_HPHP_HSTRING_VARIABLE],
    "symbol":       [stc.STC_H_ENTITY, stc.STC_H_SGML_ENTITY],
    "tag":          [stc.STC_H_ASP, stc.STC_H_ASPAT, stc.STC_H_OTHER, stc.STC_H_QUESTION, stc.STC_H_TAG, stc.STC_H_TAGEND, stc.STC_H_TAGUNKNOWN, stc.STC_H_SCRIPT, stc.STC_H_XMLSTART, stc.STC_H_XMLEND, stc.STC_H_SGML_COMMAND],
    "tagattribute": [stc.STC_H_ATTRIBUTE, stc.STC_H_ATTRIBUTEUNKNOWN],
}

lexer_tokens_basic = {
    "assembly":     [stc.STC_B_ASM],
    "comment":      [stc.STC_B_COMMENT],
    "default":      [stc.STC_B_DEFAULT],
    "identifier":   [stc.STC_B_IDENTIFIER, stc.STC_B_CONSTANT],
    "keyword":      [stc.STC_B_KEYWORD, stc.STC_B_KEYWORD2, stc.STC_B_KEYWORD3, stc.STC_B_KEYWORD4],
    "label":        [stc.STC_B_LABEL],
    "number":       [stc.STC_B_NUMBER, stc.STC_B_BINNUMBER, stc.STC_B_HEXNUMBER, stc.STC_B_DATE],
    "operator":     [stc.STC_B_OPERATOR],
    "preprocessor": [stc.STC_B_PREPROCESSOR],
    "string":       [stc.STC_B_STRING],
    "stringeol":    [stc.STC_B_STRINGEOL, stc.STC_B_ERROR],
}

lexer_tokens_eiffel = {
    "character":    [stc.STC_EIFFEL_CHARACTER],
    "commentline":  [stc.STC_EIFFEL_COMMENTLINE],
    "default":      [stc.STC_EIFFEL_DEFAULT],
    "identifier":   [stc.STC_EIFFEL_IDENTIFIER],
    "keyword":      [stc.STC_EIFFEL_WORD],
    "number":       [stc.STC_EIFFEL_NUMBER],
    "operator":     [stc.STC_EIFFEL_OPERATOR],
    "string":       [stc.STC_EIFFEL_STRING],
    "stringeol":    [stc.STC_EIFFEL_STRINGEOL],
}

lexer_tokens_matlab = {
    "comment":      [stc.STC_MATLAB_COMMENT],
    "default":      [stc.STC_MATLAB_DEFAULT],
    "identifier":   [stc.STC_MATLAB_IDENTIFIER],
    "keyword":      [stc.STC_MATLAB_KEYWORD],
    "number":       [stc.STC_MATLAB_NUMBER],
    "operator":     [stc.STC_MATLAB_OPERATOR],
    "preprocessor": [stc.STC_MATLAB_COMMAND],
    "string":       [stc.STC_MATLAB_DOUBLEQUOTESTRING, stc.STC_MATLAB_STRING],
}

lexer_tokens_fortran = {
    "comment":      [stc.STC_F_COMMENT],
    "default":      [stc.STC_F_DEFAULT, stc.STC_F_CONTINUATION],
    "identifier":   [stc.STC_F_IDENTIFIER],
    "keyword":      [stc.STC_F_WORD, stc.STC_F_WORD2, stc.STC_F_WORD3],
    "label":        [stc.STC_F_LABEL],
    "number":       [stc.STC_F_NUMBER],
    "operator":     [stc.STC_F_OPERATOR, stc.STC_F_OPERATOR2],
    "preprocessor": [stc.STC_F_PREPROCESSOR],
    "string":       [stc.STC_F_STRING1, stc.STC_F_STRING2],
    "stringeol":    [stc.STC_F_STRINGEOL],
}

lexer_token_map = {
    stc.STC_LEX_NULL: {
        "assembly":     [],
        "character":    [],
        "comment":      [],
        "commentline":  [],
        "decorator":    [],
        "default":      [],
        "defclass":     [],
        "defun":        [],
        "defmodule":    [],
        "diffadded":    [],
        "diffchanged":  [],
        "diffdeleted":  [],
        "diffheader":   [],
        "diffposition": [],
        "error":        [],
        "identifier":   [],
        "keyword":      [],
        "label":        [],
        "math":         [],
        "mathblock":    [],
        "number":       [],
        "operator":     [],
        "preprocessor": [],
        "reference":    [],
        "regex":        [],
        "string":       [],
        "stringblock":  [],
        "stringeol":    [],
        "stringref":    [],
        "symbol":       [],
        "tag":          [],
        "tagattribute": [],
    },
    stc.STC_LEX_PYTHON: {
        "character":    [stc.STC_P_CHARACTER],
        "comment":      [stc.STC_P_COMMENTBLOCK],
        "commentline":  [stc.STC_P_COMMENTLINE],
        "decorator":    [stc.STC_P_DECORATOR],
        "default":      [stc.STC_P_DEFAULT],
        "defclass":     [stc.STC_P_CLASSNAME],
        "defun":        [stc.STC_P_DEFNAME],
        "identifier":   [stc.STC_P_IDENTIFIER],
        "keyword":      [stc.STC_P_WORD, stc.STC_P_WORD2],
        "number":       [stc.STC_P_NUMBER],
        "operator":     [stc.STC_P_OPERATOR],
        "string":       [stc.STC_P_STRING],
        "stringblock":  [stc.STC_P_TRIPLE, stc.STC_P_TRIPLEDOUBLE],
        "stringeol":    [stc.STC_P_STRINGEOL],
    },
    stc.STC_LEX_CPP: {
        "character":    [stc.STC_C_CHARACTER],
        "comment":      [stc.STC_C_COMMENT, stc.STC_C_COMMENTDOC, stc.STC_C_COMMENTDOCKEYWORD, stc.STC_C_COMMENTDOCKEYWORDERROR, stc.STC_C_PREPROCESSORCOMMENT],
        "commentline":  [stc.STC_C_COMMENTLINE, stc.STC_C_COMMENTLINEDOC],
        "default":      [stc.STC_C_DEFAULT],
        "identifier":   [stc.STC_C_GLOBALCLASS, stc.STC_C_IDENTIFIER],
        "keyword":      [stc.STC_C_WORD, stc.STC_C_WORD2],
        "number":       [stc.STC_C_NUMBER, stc.STC_C_UUID],
        "operator":     [stc.STC_C_OPERATOR],
        "preprocessor": [stc.STC_C_PREPROCESSOR],
        "regex":        [stc.STC_C_REGEX],
        "string":       [stc.STC_C_HASHQUOTEDSTRING, stc.STC_C_STRING, stc.STC_C_STRINGRAW],
        "stringblock":  [stc.STC_C_TRIPLEVERBATIM, stc.STC_C_VERBATIM],
        "stringeol":    [stc.STC_C_STRINGEOL],
    },
    stc.STC_LEX_HTML: lexer_tokens_html,
    stc.STC_LEX_XML: lexer_tokens_html,
    stc.STC_LEX_PHPSCRIPT: lexer_tokens_html,
    stc.STC_LEX_PERL: {
        "character":    [stc.STC_PL_CHARACTER],
        "commentline":  [stc.STC_PL_COMMENTLINE],
        "default":      [stc.STC_PL_DEFAULT],
        "defun":        [stc.STC_PL_SUB_PROTOTYPE],
        "identifier":   [stc.STC_PL_IDENTIFIER],
        "keyword":      [stc.STC_PL_WORD],
        "number":       [stc.STC_PL_NUMBER],
        "operator":     [stc.STC_PL_OPERATOR, stc.STC_PL_PUNCTUATION],
        "preprocessor": [stc.STC_PL_PREPROCESSOR],
        "reference":    [stc.STC_PL_ARRAY, stc.STC_PL_HASH, stc.STC_PL_SCALAR, stc.STC_PL_SYMBOLTABLE],
        "regex":        [stc.STC_PL_REGEX, stc.STC_PL_REGEX_VAR],
        "string":       [stc.STC_PL_BACKTICKS, stc.STC_PL_STRING, stc.STC_PL_REGSUBST, stc.STC_PL_FORMAT, stc.STC_PL_FORMAT_IDENT, stc.STC_PL_LONGQUOTE, stc.STC_PL_STRING_Q, stc.STC_PL_STRING_QQ, stc.STC_PL_STRING_QR, stc.STC_PL_STRING_QW, stc.STC_PL_STRING_QX, stc.STC_PL_XLAT],
        "stringblock":  [stc.STC_PL_DATASECTION, stc.STC_PL_HERE_DELIM, stc.STC_PL_HERE_Q, stc.STC_PL_HERE_QQ, stc.STC_PL_HERE_QX, stc.STC_PL_POD, stc.STC_PL_POD_VERB],
        "stringeol":    [stc.STC_PL_ERROR],
        "stringref":    [stc.STC_PL_BACKTICKS_VAR, stc.STC_PL_STRING_QQ_VAR, stc.STC_PL_STRING_QR_VAR, stc.STC_PL_STRING_QX_VAR, stc.STC_PL_REGSUBST_VAR, stc.STC_PL_STRING_VAR, stc.STC_PL_HERE_QQ_VAR, stc.STC_PL_HERE_QX_VAR],
    },
    stc.STC_LEX_SQL: {
        "character":    [stc.STC_SQL_CHARACTER],
        "comment":      [stc.STC_SQL_COMMENT, stc.STC_SQL_COMMENTDOC, stc.STC_SQL_COMMENTDOCKEYWORD, stc.STC_SQL_COMMENTDOCKEYWORDERROR, stc.STC_SQL_SQLPLUS_COMMENT],
        "commentline":  [stc.STC_SQL_COMMENTLINE, stc.STC_SQL_COMMENTLINEDOC],
        "default":      [stc.STC_SQL_DEFAULT],
        "identifier":   [stc.STC_SQL_IDENTIFIER],
        "keyword":      [stc.STC_SQL_USER1, stc.STC_SQL_USER2, stc.STC_SQL_USER3, stc.STC_SQL_USER4, stc.STC_SQL_WORD, stc.STC_SQL_WORD2],
        "number":       [stc.STC_SQL_NUMBER],
        "operator":     [stc.STC_SQL_OPERATOR],
        "preprocessor": [stc.STC_SQL_SQLPLUS, stc.STC_SQL_SQLPLUS_PROMPT],
        "string":       [stc.STC_SQL_QUOTEDIDENTIFIER, stc.STC_SQL_STRING],
    },
    stc.STC_LEX_BLITZBASIC: lexer_tokens_basic,
    stc.STC_LEX_PUREBASIC: lexer_tokens_basic,
    stc.STC_LEX_FREEBASIC: lexer_tokens_basic,
    stc.STC_LEX_POWERBASIC: lexer_tokens_basic,
    stc.STC_LEX_VB: lexer_tokens_basic,
    stc.STC_LEX_VBSCRIPT: lexer_tokens_basic,
    stc.STC_LEX_MAKEFILE: {
        "comment":      [stc.STC_MAKE_COMMENT],
        "default":      [stc.STC_MAKE_DEFAULT],
        "identifier":   [stc.STC_MAKE_IDENTIFIER],
        "label":        [stc.STC_MAKE_TARGET],
        "operator":     [stc.STC_MAKE_OPERATOR],
        "preprocessor": [stc.STC_MAKE_PREPROCESSOR],
        "stringeol":    [stc.STC_MAKE_IDEOL],
    },
    stc.STC_LEX_BATCH: {
        "comment":      [stc.STC_BAT_COMMENT],
        "default":      [stc.STC_BAT_DEFAULT],
        "identifier":   [stc.STC_BAT_IDENTIFIER],
        "keyword":      [stc.STC_BAT_COMMAND, stc.STC_BAT_WORD, stc.STC_BAT_HIDE],
        "label":        [stc.STC_BAT_LABEL],
        "operator":     [stc.STC_BAT_OPERATOR],
    },
    stc.STC_LEX_LATEX: {
        "comment":      [stc.STC_L_COMMENT2],
        "commentline":  [stc.STC_L_COMMENT],
        "default":      [stc.STC_L_DEFAULT],
        "error":        [stc.STC_L_ERROR],
        "math":         [stc.STC_L_MATH],
        "mathblock":    [stc.STC_L_MATH2],
        "reference":    [stc.STC_L_SPECIAL],
        "stringblock":  [stc.STC_L_VERBATIM],
        "tag":          [stc.STC_L_COMMAND, stc.STC_L_SHORTCMD, stc.STC_L_TAG, stc.STC_L_TAG2],
        "tagattribute": [stc.STC_L_CMDOPT],
    },
    stc.STC_LEX_LUA: {
        "character":    [stc.STC_LUA_CHARACTER],
        "comment":      [stc.STC_LUA_COMMENT, stc.STC_LUA_COMMENTDOC],
        "commentline":  [stc.STC_LUA_COMMENTLINE],
        "default":      [stc.STC_LUA_DEFAULT],
        "identifier":   [stc.STC_LUA_IDENTIFIER],
        "keyword":      [stc.STC_LUA_WORD, stc.STC_LUA_WORD2, stc.STC_LUA_WORD3, stc.STC_LUA_WORD4, stc.STC_LUA_WORD5, stc.STC_LUA_WORD6, stc.STC_LUA_WORD7, stc.STC_LUA_WORD8],
        "label":        [stc.STC_LUA_LABEL],
        "number":       [stc.STC_LUA_NUMBER],
        "operator":     [stc.STC_LUA_OPERATOR],
        "preprocessor": [stc.STC_LUA_PREPROCESSOR],
        "string":       [stc.STC_LUA_LITERALSTRING, stc.STC_LUA_STRING],
        "stringeol":    [stc.STC_LUA_STRINGEOL],
    },
    stc.STC_LEX_DIFF: {
        "comment":      [stc.STC_DIFF_COMMENT],
        "default":      [stc.STC_DIFF_DEFAULT],
        "diffadded":    [stc.STC_DIFF_ADDED],
        "diffchanged":  [stc.STC_DIFF_CHANGED],
        "diffdeleted":  [stc.STC_DIFF_DELETED],
        "diffheader":   [stc.STC_DIFF_HEADER, stc.STC_DIFF_COMMAND],
        "diffposition": [stc.STC_DIFF_POSITION],
    },
    stc.STC_LEX_PASCAL: {
        "assembly":     [stc.STC_PAS_ASM],
        "character":    [stc.STC_PAS_CHARACTER],
        "comment":      [stc.STC_PAS_COMMENT, stc.STC_PAS_COMMENT2],
        "commentline":  [stc.STC_PAS_COMMENTLINE],
        "default":      [stc.STC_PAS_DEFAULT],
        "identifier":   [stc.STC_PAS_IDENTIFIER],
        "keyword":      [stc.STC_PAS_WORD],
        "number":       [stc.STC_PAS_HEXNUMBER, stc.STC_PAS_NUMBER],
        "operator":     [stc.STC_PAS_OPERATOR],
        "preprocessor": [stc.STC_PAS_PREPROCESSOR, stc.STC_PAS_PREPROCESSOR2],
        "string":       [stc.STC_PAS_STRING],
        "stringeol":    [stc.STC_PAS_STRINGEOL],
    },
    stc.STC_LEX_ADA: {
        "character":    [stc.STC_ADA_CHARACTER],
        "commentline":  [stc.STC_ADA_COMMENTLINE],
        "default":      [stc.STC_ADA_DEFAULT],
        "error":        [stc.STC_ADA_ILLEGAL],
        "identifier":   [stc.STC_ADA_IDENTIFIER],
        "keyword":      [stc.STC_ADA_WORD],
        "label":        [stc.STC_ADA_LABEL],
        "number":       [stc.STC_ADA_NUMBER],
        "operator":     [stc.STC_ADA_DELIMITER],
        "stringblock":  [stc.STC_ADA_STRING],
        "stringeol":    [stc.STC_ADA_CHARACTEREOL, stc.STC_ADA_STRINGEOL],
    },
    stc.STC_LEX_LISP: {
        "commentline":  [stc.STC_LISP_COMMENT],
        "default":      [stc.STC_LISP_DEFAULT],
        "identifier":   [stc.STC_LISP_IDENTIFIER],
        "keyword":      [stc.STC_LISP_KEYWORD, stc.STC_LISP_KEYWORD_KW],
        "number":       [stc.STC_LISP_NUMBER],
        "operator":     [stc.STC_LISP_OPERATOR],
        "string":       [stc.STC_LISP_STRING],
        "stringeol":    [stc.STC_LISP_STRINGEOL],
        "symbol":       [stc.STC_LISP_SYMBOL],
    },
    stc.STC_LEX_RUBY: {
        "character":    [stc.STC_RB_CHARACTER],
        "commentline":  [stc.STC_RB_COMMENTLINE],
        "default":      [stc.STC_RB_DEFAULT],
        "defclass":     [stc.STC_RB_CLASSNAME],
        "defun":        [stc.STC_RB_DEFNAME],
        "defmodule":    [stc.STC_RB_MODULE_NAME],
        "error":        [stc.STC_RB_ERROR],
        "identifier":   [stc.STC_RB_GLOBAL, stc.STC_RB_IDENTIFIER],
        "keyword":      [stc.STC_RB_STDERR, stc.STC_RB_STDIN, stc.STC_RB_STDOUT, stc.STC_RB_WORD, stc.STC_RB_WORD_DEMOTED],
        "number":       [stc.STC_RB_NUMBER],
        "operator":     [stc.STC_RB_OPERATOR],
        "reference":    [stc.STC_RB_CLASS_VAR, stc.STC_RB_INSTANCE_VAR],
        "regex":        [stc.STC_RB_REGEX],
        "string":       [stc.STC_RB_BACKTICKS, stc.STC_RB_STRING, stc.STC_RB_STRING_Q, stc.STC_RB_STRING_QQ, stc.STC_RB_STRING_QR, stc.STC_RB_STRING_QW, stc.STC_RB_STRING_QX],
        "stringblock":  [stc.STC_RB_DATASECTION, stc.STC_RB_HERE_DELIM, stc.STC_RB_HERE_Q, stc.STC_RB_HERE_QQ, stc.STC_RB_HERE_QX, stc.STC_RB_POD],
        "symbol":       [stc.STC_RB_SYMBOL],
    },
    stc.STC_LEX_EIFFEL: lexer_tokens_eiffel,
    stc.STC_LEX_EIFFELKW: lexer_tokens_eiffel,
    stc.STC_LEX_TCL: {
        "comment":      [stc.STC_TCL_BLOCK_COMMENT, stc.STC_TCL_COMMENT, stc.STC_TCL_COMMENT_BOX],
        "commentline":  [stc.STC_TCL_COMMENTLINE],
        "default":      [stc.STC_TCL_DEFAULT, stc.STC_TCL_EXPAND, stc.STC_TCL_MODIFIER],
        "identifier":   [stc.STC_TCL_IDENTIFIER],
        "keyword":      [stc.STC_TCL_WORD, stc.STC_TCL_WORD2, stc.STC_TCL_WORD3, stc.STC_TCL_WORD4, stc.STC_TCL_WORD5, stc.STC_TCL_WORD6, stc.STC_TCL_WORD7, stc.STC_TCL_WORD8],
        "number":       [stc.STC_TCL_NUMBER],
        "operator":     [stc.STC_TCL_OPERATOR],
        "string":       [stc.STC_TCL_IN_QUOTE, stc.STC_TCL_WORD_IN_QUOTE],
        "stringref":    [stc.STC_TCL_SUBSTITUTION, stc.STC_TCL_SUB_BRACE],
    },
    stc.STC_LEX_MATLAB: lexer_tokens_matlab,
    stc.STC_LEX_OCTAVE: lexer_tokens_matlab,
    stc.STC_LEX_ASM: {
        "character":    [stc.STC_ASM_CHARACTER],
        "comment":      [stc.STC_ASM_COMMENT, stc.STC_ASM_COMMENTDIRECTIVE],
        "commentline":  [stc.STC_ASM_COMMENTBLOCK],
        "default":      [stc.STC_ASM_DEFAULT],
        "identifier":   [stc.STC_ASM_IDENTIFIER],
        "keyword":      [stc.STC_ASM_CPUINSTRUCTION, stc.STC_ASM_EXTINSTRUCTION, stc.STC_ASM_MATHINSTRUCTION],
        "number":       [stc.STC_ASM_NUMBER],
        "operator":     [stc.STC_ASM_OPERATOR],
        "preprocessor": [stc.STC_ASM_DIRECTIVE, stc.STC_ASM_DIRECTIVEOPERAND],
        "reference":    [stc.STC_ASM_REGISTER],
        "string":       [stc.STC_ASM_STRING],
        "stringeol":    [stc.STC_ASM_STRINGEOL],
    },
    stc.STC_LEX_FORTRAN: lexer_tokens_fortran,
    stc.STC_LEX_F77: lexer_tokens_fortran,
    stc.STC_LEX_CSS: {
        "comment":      [stc.STC_CSS_COMMENT, stc.STC_CSS_IMPORTANT],
        "default":      [stc.STC_CSS_DEFAULT],
        "identifier":   [stc.STC_CSS_IDENTIFIER2, stc.STC_CSS_IDENTIFIER3, stc.STC_CSS_TAG, stc.STC_CSS_UNKNOWN_IDENTIFIER, stc.STC_CSS_PSEUDOCLASS, stc.STC_CSS_PSEUDOELEMENT, stc.STC_CSS_EXTENDED_IDENTIFIER, stc.STC_CSS_EXTENDED_PSEUDOCLASS, stc.STC_CSS_EXTENDED_PSEUDOELEMENT, stc.STC_CSS_UNKNOWN_PSEUDOCLASS, stc.STC_CSS_VARIABLE],
        "keyword":      [stc.STC_CSS_IDENTIFIER],
        "number":       [stc.STC_CSS_VALUE],
        "operator":     [stc.STC_CSS_OPERATOR],
        "preprocessor": [stc.STC_CSS_DIRECTIVE, stc.STC_CSS_MEDIA],
        "reference":    [stc.STC_CSS_CLASS, stc.STC_CSS_ID],
        "string":       [stc.STC_CSS_SINGLESTRING, stc.STC_CSS_DOUBLESTRING],
        "tagattribute": [stc.STC_CSS_ATTRIBUTE],
    },
    stc.STC_LEX_PS: {
        "commentline":  [stc.STC_PS_COMMENT, stc.STC_PS_DSC_COMMENT, stc.STC_PS_DSC_VALUE],
        "default":      [stc.STC_PS_DEFAULT],
        "error":        [stc.STC_PS_BADSTRINGCHAR],
        "identifier":   [stc.STC_PS_NAME],
        "keyword":      [stc.STC_PS_KEYWORD],
        "number":       [stc.STC_PS_NUMBER],
        "operator":     [stc.STC_PS_PAREN_ARRAY, stc.STC_PS_PAREN_DICT, stc.STC_PS_PAREN_PROC],
        "preprocessor": [stc.STC_PS_LITERAL, stc.STC_PS_IMMEVAL],
        "string":       [stc.STC_PS_BASE85STRING, stc.STC_PS_HEXSTRING, stc.STC_PS_TEXT],
    },
    stc.STC_LEX_YAML: {
        "commentline":  [stc.STC_YAML_COMMENT, stc.STC_YAML_DOCUMENT],
        "default":      [stc.STC_YAML_DEFAULT],
        "error":        [stc.STC_YAML_ERROR],
        "identifier":   [stc.STC_YAML_IDENTIFIER],
        "keyword":      [stc.STC_YAML_KEYWORD],
        "number":       [stc.STC_YAML_NUMBER],
        "operator":     [stc.STC_YAML_OPERATOR],
        "reference":    [stc.STC_YAML_REFERENCE],
        "string":       [stc.STC_YAML_TEXT],
    },
    stc.STC_LEX_ERLANG: {
        "character":    [stc.STC_ERLANG_CHARACTER],
        "commentline":  [stc.STC_ERLANG_COMMENT, stc.STC_ERLANG_COMMENT_DOC, stc.STC_ERLANG_COMMENT_DOC_MACRO, stc.STC_ERLANG_COMMENT_FUNCTION, stc.STC_ERLANG_COMMENT_MODULE],
        "default":      [stc.STC_ERLANG_DEFAULT],
        "identifier":   [stc.STC_ERLANG_ATOM, stc.STC_ERLANG_BIFS, stc.STC_ERLANG_FUNCTION_NAME, stc.STC_ERLANG_MACRO, stc.STC_ERLANG_NODE_NAME, stc.STC_ERLANG_RECORD, stc.STC_ERLANG_VARIABLE, stc.STC_ERLANG_UNKNOWN],
        "keyword":      [stc.STC_ERLANG_KEYWORD],
        "number":       [stc.STC_ERLANG_NUMBER],
        "operator":     [stc.STC_ERLANG_OPERATOR],
        "preprocessor": [stc.STC_ERLANG_MODULES, stc.STC_ERLANG_MODULES_ATT, stc.STC_ERLANG_PREPROC],
        "string":       [stc.STC_ERLANG_ATOM_QUOTED, stc.STC_ERLANG_MACRO_QUOTED, stc.STC_ERLANG_NODE_NAME_QUOTED, stc.STC_ERLANG_RECORD_QUOTED, stc.STC_ERLANG_STRING],
    },
    stc.STC_LEX_VERILOG: {
        "comment":      [stc.STC_V_COMMENT],
        "commentline":  [stc.STC_V_COMMENTLINE, stc.STC_V_COMMENTLINEBANG],
        "default":      [stc.STC_V_DEFAULT],
        "identifier":   [stc.STC_V_IDENTIFIER, stc.STC_V_USER],
        "keyword":      [stc.STC_V_WORD, stc.STC_V_WORD2, stc.STC_V_WORD3],
        "number":       [stc.STC_V_NUMBER],
        "operator":     [stc.STC_V_OPERATOR],
        "preprocessor": [stc.STC_V_PREPROCESSOR],
        "string":       [stc.STC_V_STRING],
        "stringeol":    [stc.STC_V_STRINGEOL],
    },
    stc.STC_LEX_BASH: {
        "character":    [stc.STC_SH_CHARACTER],
        "commentline":  [stc.STC_SH_COMMENTLINE],
        "default":      [stc.STC_SH_DEFAULT],
        "error":        [stc.STC_SH_ERROR],
        "identifier":   [stc.STC_SH_IDENTIFIER, stc.STC_SH_PARAM],
        "keyword":      [stc.STC_SH_WORD],
        "number":       [stc.STC_SH_NUMBER],
        "operator":     [stc.STC_SH_OPERATOR],
        "reference":    [stc.STC_SH_SCALAR],
        "string":       [stc.STC_SH_BACKTICKS, stc.STC_SH_STRING],
        "stringblock":  [stc.STC_SH_HERE_DELIM, stc.STC_SH_HERE_Q],
    },
    stc.STC_LEX_VHDL: {
        "comment":      [stc.STC_VHDL_COMMENT],
        "commentline":  [stc.STC_VHDL_COMMENTLINEBANG],
        "default":      [stc.STC_VHDL_DEFAULT],
        "identifier":   [stc.STC_VHDL_ATTRIBUTE, stc.STC_VHDL_IDENTIFIER, stc.STC_VHDL_STDFUNCTION, stc.STC_VHDL_STDPACKAGE, stc.STC_VHDL_STDTYPE, stc.STC_VHDL_USERWORD],
        "keyword":      [stc.STC_VHDL_KEYWORD],
        "number":       [stc.STC_VHDL_NUMBER],
        "operator":     [stc.STC_VHDL_OPERATOR, stc.STC_VHDL_STDOPERATOR],
        "string":       [stc.STC_VHDL_STRING],
        "stringeol":    [stc.STC_VHDL_STRINGEOL],
    },
    stc.STC_LEX_CAML: {
        "character":    [stc.STC_CAML_CHAR],
        "comment":      [stc.STC_CAML_COMMENT, stc.STC_CAML_COMMENT1, stc.STC_CAML_COMMENT2, stc.STC_CAML_COMMENT3],
        "default":      [stc.STC_CAML_DEFAULT],
        "identifier":   [stc.STC_CAML_IDENTIFIER, stc.STC_CAML_TAGNAME],
        "keyword":      [stc.STC_CAML_KEYWORD, stc.STC_CAML_KEYWORD2, stc.STC_CAML_KEYWORD3],
        "number":       [stc.STC_CAML_NUMBER],
        "operator":     [stc.STC_CAML_OPERATOR],
        "preprocessor": [stc.STC_CAML_LINENUM],
        "string":       [stc.STC_CAML_STRING, stc.STC_CAML_WHITE],
    },
    stc.STC_LEX_HASKELL: {
        "character":    [stc.STC_HA_CHARACTER],
        "comment":      [stc.STC_HA_COMMENTBLOCK, stc.STC_HA_COMMENTBLOCK2, stc.STC_HA_COMMENTBLOCK3],
        "commentline":  [stc.STC_HA_COMMENTLINE],
        "default":      [stc.STC_HA_CAPITAL, stc.STC_HA_DEFAULT, stc.STC_HA_IMPORT],
        "defmodule":    [stc.STC_HA_CLASS, stc.STC_HA_DATA, stc.STC_HA_INSTANCE, stc.STC_HA_MODULE],
        "identifier":   [stc.STC_HA_IDENTIFIER],
        "keyword":      [stc.STC_HA_KEYWORD],
        "number":       [stc.STC_HA_NUMBER],
        "operator":     [stc.STC_HA_OPERATOR],
        "string":       [stc.STC_HA_STRING],
    },
    stc.STC_LEX_SMALLTALK: {
        "character":    [stc.STC_ST_CHARACTER],
        "commentline":  [stc.STC_ST_COMMENT],
        "default":      [stc.STC_ST_DEFAULT],
        "identifier":   [stc.STC_ST_GLOBAL, stc.STC_ST_KWSEND, stc.STC_ST_SPECIAL, stc.STC_ST_SPEC_SEL],
        "keyword":      [stc.STC_ST_BOOL, stc.STC_ST_NIL, stc.STC_ST_RETURN, stc.STC_ST_SELF, stc.STC_ST_SUPER],
        "number":       [stc.STC_ST_BINARY, stc.STC_ST_NUMBER],
        "operator":     [stc.STC_ST_ASSIGN],
        "string":       [stc.STC_ST_STRING],
        "symbol":       [stc.STC_ST_SYMBOL],
    },
    stc.STC_LEX_D: {
        "character":    [stc.STC_D_CHARACTER],
        "comment":      [stc.STC_D_COMMENT, stc.STC_D_COMMENTDOC, stc.STC_D_COMMENTDOCKEYWORD, stc.STC_D_COMMENTDOCKEYWORDERROR, stc.STC_D_COMMENTNESTED],
        "commentline":  [stc.STC_D_COMMENTLINE, stc.STC_D_COMMENTLINEDOC],
        "default":      [stc.STC_D_DEFAULT],
        "defclass":     [stc.STC_D_TYPEDEF],
        "identifier":   [stc.STC_D_IDENTIFIER],
        "keyword":      [stc.STC_D_WORD, stc.STC_D_WORD2, stc.STC_D_WORD3, stc.STC_D_WORD5, stc.STC_D_WORD6, stc.STC_D_WORD7],
        "number":       [stc.STC_D_NUMBER],
        "operator":     [stc.STC_D_OPERATOR],
        "string":       [stc.STC_D_STRING, stc.STC_D_STRINGB, stc.STC_D_STRINGR],
        "stringeol":    [stc.STC_D_STRINGEOL],
    },
    stc.STC_LEX_CMAKE: {
        "comment":      [stc.STC_CMAKE_COMMENT],
        "default":      [stc.STC_CMAKE_DEFAULT],
        "identifier":   [stc.STC_CMAKE_USERDEFINED],
        "keyword":      [stc.STC_CMAKE_COMMANDS],
        "label":        [stc.STC_CMAKE_VARIABLE],
        "number":       [stc.STC_CMAKE_NUMBER],
        "preprocessor": [stc.STC_CMAKE_FOREACHDEF, stc.STC_CMAKE_IFDEFINEDEF, stc.STC_CMAKE_MACRODEF, stc.STC_CMAKE_WHILEDEF],
        "reference":    [stc.STC_CMAKE_PARAMETERS],
        "string":       [stc.STC_CMAKE_STRINGDQ, stc.STC_CMAKE_STRINGLQ, stc.STC_CMAKE_STRINGRQ],
        "stringref":    [stc.STC_CMAKE_STRINGVAR],
    },
    stc.STC_LEX_R: {
        "comment":      [stc.STC_R_COMMENT],
        "default":      [stc.STC_R_DEFAULT],
        "identifier":   [stc.STC_R_IDENTIFIER],
        "keyword":      [stc.STC_R_BASEKWORD, stc.STC_R_KWORD, stc.STC_R_OTHERKWORD],
        "number":       [stc.STC_R_NUMBER],
        "operator":     [stc.STC_R_INFIX, stc.STC_R_OPERATOR],
        "string":       [stc.STC_R_STRING, stc.STC_R_STRING2],
        "stringeol":    [stc.STC_R_INFIXEOL],
    },
    stc.STC_LEX_SML: {
        "character":    [stc.STC_SML_CHAR],
        "comment":      [stc.STC_SML_COMMENT, stc.STC_SML_COMMENT1, stc.STC_SML_COMMENT2, stc.STC_SML_COMMENT3],
        "default":      [stc.STC_SML_DEFAULT],
        "identifier":   [stc.STC_SML_IDENTIFIER, stc.STC_SML_TAGNAME],
        "keyword":      [stc.STC_SML_KEYWORD, stc.STC_SML_KEYWORD2, stc.STC_SML_KEYWORD3],
        "number":       [stc.STC_SML_NUMBER],
        "operator":     [stc.STC_SML_OPERATOR],
        "preprocessor": [stc.STC_SML_LINENUM],
        "string":       [stc.STC_SML_STRING],
    },
    stc.STC_LEX_MODULA: {
        "character":    [stc.STC_MODULA_CHAR, stc.STC_MODULA_CHARSPEC],
        "comment":      [stc.STC_MODULA_COMMENT, stc.STC_MODULA_DOXYCOMM, stc.STC_MODULA_DOXYKEY],
        "default":      [stc.STC_MODULA_DEFAULT],
        "defun":        [stc.STC_MODULA_PROC],
        "keyword":      [stc.STC_MODULA_KEYWORD, stc.STC_MODULA_RESERVED],
        "number":       [stc.STC_MODULA_BASENUM, stc.STC_MODULA_FLOAT, stc.STC_MODULA_NUMBER],
        "operator":     [stc.STC_MODULA_OPERATOR],
        "preprocessor": [stc.STC_MODULA_PRAGMA, stc.STC_MODULA_PRGKEY],
        "string":       [stc.STC_MODULA_STRING, stc.STC_MODULA_STRSPEC],
        "stringeol":    [stc.STC_MODULA_BADSTR],
    },
    stc.STC_LEX_COFFEESCRIPT: {
        "character":    [stc.STC_COFFEESCRIPT_CHARACTER],
        "comment":      [stc.STC_COFFEESCRIPT_COMMENT, stc.STC_COFFEESCRIPT_COMMENTBLOCK, stc.STC_COFFEESCRIPT_COMMENTDOC, stc.STC_COFFEESCRIPT_COMMENTDOCKEYWORD, stc.STC_COFFEESCRIPT_COMMENTDOCKEYWORDERROR],
        "commentline":  [stc.STC_COFFEESCRIPT_COMMENTLINE, stc.STC_COFFEESCRIPT_COMMENTLINEDOC, stc.STC_COFFEESCRIPT_VERBOSE_REGEX_COMMENT],
        "default":      [stc.STC_COFFEESCRIPT_DEFAULT],
        "identifier":   [stc.STC_COFFEESCRIPT_GLOBALCLASS, stc.STC_COFFEESCRIPT_IDENTIFIER],
        "keyword":      [stc.STC_COFFEESCRIPT_WORD, stc.STC_COFFEESCRIPT_WORD2],
        "number":       [stc.STC_COFFEESCRIPT_NUMBER, stc.STC_COFFEESCRIPT_UUID],
        "operator":     [stc.STC_COFFEESCRIPT_OPERATOR],
        "preprocessor": [stc.STC_COFFEESCRIPT_PREPROCESSOR],
        "regex":        [stc.STC_COFFEESCRIPT_REGEX, stc.STC_COFFEESCRIPT_VERBOSE_REGEX],
        "string":       [stc.STC_COFFEESCRIPT_HASHQUOTEDSTRING, stc.STC_COFFEESCRIPT_STRING, stc.STC_COFFEESCRIPT_STRINGRAW],
        "stringblock":  [stc.STC_COFFEESCRIPT_TRIPLEVERBATIM, stc.STC_COFFEESCRIPT_VERBATIM],
        "stringeol":    [stc.STC_COFFEESCRIPT_STRINGEOL],
    },
}
