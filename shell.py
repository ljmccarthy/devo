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

shell_prelude = {
    "darwin": """\
source ~/.bash_profile\n' \
export PATH="${PATH}:/usr/local/bin:/usr/X11/bin"
%s
""",
}

def run_shell_command(cmdline, pipe_output=True, combine_stderr=True, env=None, cwd=None, killable=True, **kwargs):
    if sys.platform == "win32":
        args = " && ".join(command.strip() for command in cmdline.split("\n") if command.strip())
    else:
        cmdline = shell_prelude.get(sys.platform, "%s") % cmdline
        args = [os.environ.get("SHELL", "/bin/sh"), "-c", cmdline]

    return (KillablePopen if killable else Popen)(
        args = args,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE if pipe_output else None,
        stderr = (subprocess.STDOUT if combine_stderr else subprocess.PIPE) if pipe_output else None,
        bufsize = 1,
        close_fds = (sys.platform != "win32"),
        shell = (sys.platform == "win32"),
        cwd = cwd,
        env = make_environment(env, cwd),
        **kwargs)
