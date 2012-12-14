import sys, os, os.path

def compile_resource_dict(resdir):
    resdict = {}
    for dirpath, dirnames, filenames in os.walk(resdir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            respath = os.path.relpath(filepath, resdir)
            sys.stdout.write("Compiling resource: %r\n" % respath)
            with open(filepath, "rb") as f:
                resdict[respath] = f.read()
    return resdict

def compile_resources(resdir="res", resfile="res_compiled.py"):
    resdict = compile_resource_dict(resdir)

    items = "\n".join("%r: %r," % x for x in resdict.iteritems())
    code = "resources = {\n%s\n}\n" % items

    with open(resfile, "w") as f:
        f.write(code)

if __name__ == "__main__":
    compile_resources()
