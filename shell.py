import sys, os, subprocess, signal
from subprocess import Popen
from killableprocess import Popen as KillablePopen

remove_vars = (
    "PYTHONHOME", "PYTHONPATH", "VERSIONER_PYTHON_PREFER_32_BIT",
    "EXECUTABLEPATH", "RESOURCEPATH", "ARGVZERO",
)

def make_environment(env=None, cwd=None):
    if env is None:
        env = os.environ
    env = env.copy()

    for var in remove_vars:
        if var in env:
            del env[var]

    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "UTF-8"

    if cwd is None:
        env["PWD"] = os.getcwd()
    else:
        try:
            env["PWD"] = os.path.realpath(cwd).encode(sys.getfilesystemencoding())
        except (LookupError, UnicodeEncodeError):
            env["PWD"] = os.path.realpath(cwd).encode("utf-8")

    return env

def run_shell_command(cmdline, pipe_output=True, env=None, cwd=None, killable=True, **kwargs):
    if sys.platform == "win32":
        args = cmdline
    else:
        args = [os.environ.get("SHELL", "/bin/sh")]

    process = (KillablePopen if killable else Popen)(args,
        stdin = subprocess.PIPE if sys.platform != "win32" else None,
        stdout = subprocess.PIPE if pipe_output else None,
        stderr = subprocess.STDOUT if pipe_output else None,
        bufsize = 1,
        close_fds = (sys.platform != "win32"),
        shell = (sys.platform == "win32"),
        cwd = cwd,
        env = make_environment(env, cwd),
        **kwargs)

    if sys.platform != "win32":
        if sys.platform == "darwin":
            process.stdin.write(
                'source ~/.bash_profile;' +
                'export PATH="${PATH}:/usr/local/bin:/usr/X11/bin";')
        process.stdin.write(cmdline)
        process.stdin.close()

    return process
