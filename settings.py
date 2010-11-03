import os
import json
import fileutil

def read_settings(filename):
    with open(filename, "rb") as f:
        return json.loads(f.read())

def write_settings(filename, settings):
    fileutil.mkpath(os.path.dirname(filename))
    data = json.dumps(settings, indent=2)
    fileutil.atomic_write_file(filename, data)
