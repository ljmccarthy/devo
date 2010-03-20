import sys, os, errno, shutil

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

def mkpath(path):
    dirpath = path
    parts = []
    while True:
        try:
            os.mkdir(dirpath)
            break
        except OSError, e:
            if e.errno == errno.EEXIST:
                break
            parts.append(os.path.basename(dirpath))
            dirpath = os.path.dirname(dirpath)
    for part in reversed(parts):
        dirpath = os.path.join(dirpath, part)
        os.mkdir(dirpath)

if sys.platform == "win32":
    from fileutil_win32 import *
elif sys.platform == "linux2":
    from fileutil_linux import *
else:
    raise ImportError("Unsupported platform: %s" % sys.platform)
