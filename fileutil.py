import sys, os, shutil

def atomic_write_file(path, data):
    temp = os.path.join(os.path.dirname(path), ".saving." + os.path.basename(path))
    try:
        with open(temp, "wb") as out:
            try:
                shutil.copystat(path, temp)
            except OSError:
                pass
            out.write(data)
    except (IOError, OSError):
        try:
            os.remove(temp)
        except OSError:
            pass
        raise
    else:
        rename(temp, path)

rename = os.rename

def remove(path):
    # TODO: move to recycle bin
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

if sys.platform == "win32":
    from fileutil_win32 import *
elif sys.platform == "linux2":
    from fileutil_linux import *
else:
    raise ImportError("Unsupported platform: %s" % sys.platform)
