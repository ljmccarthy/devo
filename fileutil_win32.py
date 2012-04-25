import os
import win32api, win32con, win32file, pywintypes
from win32com.shell import shell, shellcon

from async import async_function
from fileutil_common import *

# os.rename is broken on windows
def rename(old, new):
    try:
        win32file.MoveFileEx(old, new, win32file.MOVEFILE_REPLACE_EXISTING)
    except pywintypes.error, e:
        raise WindowsError(*e.args)

def shell_open(path, workdir=None):
    return win32api.ShellExecute(None, "open", path, None, workdir, win32con.SW_SHOW) > 32

def get_user_config_dir(name=""):
    path = os.environ.get("APPDATA", "")
    if name:
        path = os.path.join(path, name)
    return os.path.realpath(path)

def is_hidden_file(path):
    return (win32file.GetFileAttributes(path) & win32file.FILE_ATTRIBUTE_HIDDEN) != 0

@async_function
def shell_remove(path):
    shell.SHFileOperation(
        (0, shellcon.FO_DELETE, path, None, shellcon.FOF_ALLOWUNDO, None, None))

@async_function
def shell_copy(srcpath, dstpath):
    if destination_is_same(srcpath, dstpath):
        return
    if ask_copy_file(srcpath, dstpath):
        shell.SHFileOperation(
            (0, shellcon.FO_COPY, srcpath, dstpath, shellcon.FOF_ALLOWUNDO, None, None))

@async_function
def shell_move(srcpath, dstpath):
    if destination_is_same(srcpath, dstpath):
        return
    if ask_move_file(srcpath, dstpath):
        shell.SHFileOperation(
            (0, shellcon.FO_MOVE, srcpath, dstpath, shellcon.FOF_ALLOWUNDO, None, None))

def shell_move_or_copy(srcpath, dstpath):
    srcdrive = os.path.splitdrive(os.path.realpath(srcpath))[0].upper()
    dstdrive = os.path.splitdrive(os.path.realpath(dstpath))[0].upper()
    if srcdrive == dstdrive:
        return shell_move(srcpath, dstpath)
    else:
        return shell_copy(srcpath, dstpath)

__all__ = (
    "rename",
    "shell_open",
    "get_user_config_dir",
    "is_hidden_file",
    "shell_remove",
    "shell_copy",
    "shell_move",
    "shell_move_or_copy",
)
