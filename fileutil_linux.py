import os, subprocess

def run(*args):
    p = subprocess.Popen(args, close_fds=True)
    return p.wait()

def shell_open(path):
    return run("xdg-open", path) == 0

__all__ = (
    "shell_open",
)
