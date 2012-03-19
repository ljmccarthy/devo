import sys, os, subprocess

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
        env["PWD"] = os.path.realpath(cwd)

    return env

def run_shell_command(cmdline, pipe_output=True, env=None, cwd=None, **kwargs):
    if sys.platform == "win32":
        args = cmdline
    else:
        args = [os.environ.get("SHELL", "/bin/sh")]

    process = subprocess.Popen(args,
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
                'source ~/.bash_profile\n' +
                'export PATH="${PATH}:/usr/local/bin"\n')
        process.stdin.write(cmdline)
        process.stdin.close()

    return process

def kill_shell_process(process, force=False):
    if sys.platform[:5] == "linux":
        signal = "-KILL" if force else "-TERM"
        try:
            rc = subprocess.call(["pkill", signal, "-P", str(process.pid)])
            if rc == 0:
                return
        except OSError:
            pass

    if force:
        process.kill()
    else:
        process.terminate()
