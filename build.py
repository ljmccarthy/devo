#!/usr/bin/env python2.7
#coding=UTF-8

import sys, os, shutil, subprocess
import app_info

project_root = os.path.dirname(os.path.realpath(__file__))

project_syspath = [
    project_root,
    os.path.join(project_root, "fsmonitor")
] + sys.path

target_name = "devo"
main_script = "main.py"
dist_dir = "dist"
platform_dir = os.path.join(dist_dir, sys.platform)
target_dir = os.path.join(platform_dir, "%s-%s" % (target_name, app_info.version_string))

includes = []

excludes = ["pywin", "pywin.debugger"]

encodings = ["ascii", "latin_1", "utf_8", "utf_16", "utf_32", "hex_codec", "mbcs"]

win32com_includes = ["win32com.shell"]

dll_excludes = [
    "w9xpopen.exe",
    "MSVCR71.DLL",
    "MFC71.DLL",
    "MSVCP71.DLL",
    "gdiplus.dll",
    "MSVCP90.dll",
    "OLEACC.dll",
    "mswsock.dll",
    "powrprof.dll",
    "UxTheme.dll",
    "CRYPT32.dll",
]

def run(*args, **kwargs):
    subprocess.Popen(args, **kwargs).communicate()

class Attributes(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def get_encodings_modules(encodings):
    return ["encodings"] + ["encodings." + encoding for encoding in encodings]

def add_win32com_modules(win32com_modules):
    # see http://www.py2exe.org/index.cgi/WinShell
    try:
        import py2exe.mf as modulefinder
        import win32com
        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath("win32com", p)
        for module_name in win32com_modules:
            __import__(module_name)
            m = sys.modules[module_name]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(module_name, p)
    except ImportError:
        pass

def find_program_files(rel_path):
    for envvar in ["PROGRAMW6432", "PROGRAMFILES", "PROGRAMFILES(X86)"]:
        if envvar in os.environ:
            path = os.path.join(os.environ[envvar], rel_path)
            if os.path.exists(path):
                return path
    return ""

def build_py2exe():
    from distutils.core import setup
    import py2exe

    class target(object):
        script         = main_script
        dest_base      = target_name
        name           = app_info.name
        description    = app_info.name
        version        = app_info.version_string
        company_name   = app_info.company_name
        copyright      = app_info.copyright.encode("latin-1")
        icon_resources = [(1, "icons/devo.ico")]

    sys.argv.append("py2exe")
    sys.path = project_syspath

    add_win32com_modules(win32com_includes)

    setup(
        options = {
            "py2exe" : dict(
                dist_dir     = target_dir,
                ascii        = True,
                includes     = includes + get_encodings_modules(encodings),
                excludes     = excludes,
                optimize     = 1,
                bundle_files = 3,
                dll_excludes = dll_excludes,
                compressed   = True,
            )
        },
        zipfile = None,
        windows = [target],
    )

    sevenzip = find_program_files(r"7-Zip\7z.exe")
    if sevenzip:
        run(sevenzip, "a", "-tzip", "-y",
            "%s-%s.zip" % (target_name, app_info.version_string),
            "%s-%s" % (target_name, app_info.version_string),
            cwd = platform_dir)
    else:
        print "Error: 7-zip not found"

def build_py2app():
    from distutils.core import setup
    import py2app

    sys.argv.append("py2app")
    sys.path = project_syspath

    setup(
        name = target_name,
        setup_requires = "py2app",
        app = [main_script],
        data_files = [],
        options = dict(
            py2app = dict(
                dist_dir = target_dir,
                includes = includes + get_encodings_modules(encodings),
                excludes = excludes,
                optimize = 1,
                compressed = True,
                site_packages = True,
                iconfile = "icons/devo.icns",
                plist = dict(
                    CFBundleName = app_info.name,
                    CFBundleShortVersionString = app_info.version_string,
                    CFBundleGetInfoString = "%s %s" % (app_info.name, app_info.version_string),
                    CFBundleExecutable = target_name,
                    CFBundleIdentifier = app_info.identifier,
                    LSArchitecturePriority = ["x86_64", "i386"],
                ),
            ),
        ),
    )

    run("hdiutil", "create", "-srcfolder", target_dir, "-volname", app_info.name,
        "-format", "UDBZ", "-ov", os.path.join(dist_dir, "%s-%s.dmg" % (target_name, app_info.version_string)))

def build_cxfreeze():
    import cx_Freeze

    cx_Freeze.Freezer(
        [cx_Freeze.Executable(main_script, targetName=target_name)],
        targetDir = target_dir,
        includes = includes + get_encodings_modules(encodings),
        excludes = excludes,
        optimizeFlag = 1,
        appendScriptToExe = True,
        createLibraryZip = False,
        copyDependentFiles = True,
        binPathExcludes = ["/usr"],
        path = project_syspath,
        compress = True,
        silent = False
    ).Freeze()

def make_tar_archive():
    run("tar", "cvjf",
        "%s-%s.tar.bz2" % (target_name, app_info.version_string),
        "%s-%s" % (target_name, app_info.version_string),
        cwd = platform_dir)

def build():
    os.chdir(project_root)
    shutil.rmtree(target_dir, True)

    from get_components import get_components
    try:
        get_components()
    except OSError:
        pass

    from compile_resources import compile_resources
    compile_resources()

    syspath = sys.path[:]
    try:
        if sys.platform == "win32":
            build_py2exe()
        elif sys.platform == "darwin":
            build_py2app()
        else:
            build_cxfreeze()
    finally:
        sys.path = syspath

if __name__ == "__main__":
    build()
