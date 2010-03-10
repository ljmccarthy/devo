import os, shutil

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
        os.rename(temp, path)
