import os, csv, uuid

class UUIDFile(object):
    def __init__(self, filename=""):
        self.filename = filename
        self.key_uuids = {}
        if filename:
            try:
                self.load(filename)
            except IOError:
                pass

    def load(self, filename=""):
        if filename:
            self.filename = filename
        key_uuids = {}
        with open(self.filename, "rb") as f:
            for key_uuid, key in csv.reader(f):
                key_uuids[key] = key_uuid
        self.key_uuids = key_uuids

    def save(self, filename=""):
        if filename:
            self.filename = filename
        with open(self.filename, "wb") as f:
            writer = csv.writer(f)
            key_uuids = sorted(self.key_uuids.iteritems())
            for key, key_uuid in key_uuids:
                writer.writerow((key_uuid, key))

    def get_uuid(self, key):
        key_uuid = self.key_uuids.get(key)
        if key_uuid is None:
            key_uuid = self.key_uuids[key] = str(uuid.uuid4()).upper()
        return key_uuid

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

def walk(top):
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            yield os.path.relpath(os.path.join(dirpath, filename), top)

if __name__ == "__main__":
    with UUIDFile("uuids.csv") as uuidfile:
        for path in walk("../dist/linux2"):
            print path, uuidfile.get_uuid(path)
