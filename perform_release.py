import app_info
import subprocess

def run(*args, **kwargs):
    subprocess.check_call(args, **kwargs)

ver = "v" + app_info.version_string

run("git", "tag", "-a", ver, "-m", "Release " + ver)
run("git", "push", "--tags")
