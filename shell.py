import sys, os, subprocess, signal

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
        except LookupError:
            env["PWD"] = os.path.realpath(cwd).encode("utf-8")

    return env

setsid = None
setsid = getattr(os, "setsid", None)
if not setsid:
    setsid = getattr(os, "setpgrp", None)

def run_shell_command(cmdline, pipe_output=True, env=None, cwd=None, **kwargs):
    if sys.platform == "win32":
        args = cmdline
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        preexec_fn = None
    else:
        args = [os.environ.get("SHELL", "/bin/sh")]
        creationflags = 0
        preexec_fn = setsid

    process = subprocess.Popen(args,
        stdin = subprocess.PIPE if sys.platform != "win32" else None,
        stdout = subprocess.PIPE if pipe_output else None,
        stderr = subprocess.STDOUT if pipe_output else None,
        bufsize = 1,
        close_fds = (sys.platform != "win32"),
        shell = (sys.platform == "win32"),
        cwd = cwd,
        env = make_environment(env, cwd),
        preexec_fn = preexec_fn,
        creationflags = creationflags,
        **kwargs)

    if sys.platform != "win32":
        if sys.platform == "darwin":
            process.stdin.write(
                'source ~/.bash_profile;' +
                'export PATH="${PATH}:/usr/local/bin:/usr/X11/bin";')
        process.stdin.write(cmdline)
        process.stdin.close()

    return process

def kill_shell_process(process, force=False):
    if sys.platform == "win32":
        signum = signal.CTRL_BREAK_EVENT
    else:
        signum = signal.SIGKILL if force else signal.SIGTERM
    try:
        if setsid:
            os.killpg(os.getpgid(process.pid), signum)
        else:
            os.kill(process.pid, signum)
    except OSError:
        pass
