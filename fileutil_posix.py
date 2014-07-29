import sys, os, subprocess

def run(args, workdir=None):
    p = subprocess.Popen(args, close_fds=True, cwd=workdir)
    return p.wait()

if sys.platform == "darwin":
    shell_open_command = "open"
else:
    shell_open_command = "xdg-open"

def shell_open(path, workdir=None):
    return run([shell_open_command, path], workdir=workdir) == 0

def get_user_config_dir(name=""):
    path = os.environ.get("XDG_CONFIG_HOME")
    if not path:
        path = os.path.join(os.environ.get("HOME", "/"), ".config")
    if name:
        path = os.path.join(path, name)
    return os.path.realpath(path)

__all__ = (
    "shell_open",
    "get_user_config_dir",
)
