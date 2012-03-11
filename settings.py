import os
import json
import fileutil

def read_settings(filename):
    return json.loads(fileutil.read_file(filename))

def write_settings(filename, settings):
    fileutil.mkpath(os.path.dirname(filename))
    data = json.dumps(settings, indent=2)
    fileutil.atomic_write_file(filename, data)
