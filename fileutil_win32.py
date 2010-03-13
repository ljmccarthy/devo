import win32api, win32con, win32file, pywintypes

# os.rename is broken on windows
def rename(old, new):
    try:
        win32file.MoveFileEx(old, new, win32file.MOVEFILE_REPLACE_EXISTING)
    except pywintypes.error, e:
        raise WindowsError(*e.args)

def shell_open(path):
    return win32api.ShellExecute(None, "open", path, None, None, win32con.SW_SHOW) > 32

__all__ = (
    "rename",
    "shell_open",
)
