import sys, os, shutil

if sys.platform == "win32":
    # os.rename is broken on windows
    import win32file
    def rename(old, new):
        win32file.MoveFileEx(old, new, win32file.MOVEFILE_REPLACE_EXISTING)
else:
    rename = os.rename

def atomic_write_file(path, data):
    temp = os.path.join(os.path.dirname(path), ".tmpsave." + os.path.basename(path))
    try:
        with open(temp, "wb") as out:
            try:
                shutil.copystat(path, temp)
            except OSError:
                pass
            out.write(data)
    except IOError:
        try:
            os.remove(temp)
        except OSError:
            pass
        raise
    else:
        rename(temp, path)
