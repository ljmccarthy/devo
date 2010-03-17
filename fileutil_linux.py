import os, subprocess

def run(*args):
    p = subprocess.Popen(args, close_fds=True)
    return p.wait()

def shell_open(path):
    return run("xdg-open", path) == 0

def get_user_config_dir(name=""):
    path = os.environ["HOME"]
    if name:
        path = os.path.join(path, "." + name)
    return path

__all__ = (
    "shell_open",
    "get_user_config_dir",
)
