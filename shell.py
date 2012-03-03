import sys, subprocess

def run_shell_command(cmdline, pipe_output=True, **kwargs):
    args = ["bash"] if sys.platform != "win32" else cmdline

    process = subprocess.Popen(args,
        stdin = subprocess.PIPE if sys.platform != "win32" else None,
        stdout = subprocess.PIPE if pipe_output else None,
        stderr = subprocess.STDOUT if pipe_output else None,
        bufsize = 1,
        close_fds = (sys.platform != "win32"),
        shell = (sys.platform == "win32"),
        **kwargs)

    if sys.platform != "win32":
        process.stdin.write(cmdline)
        process.stdin.close()

    return process

def kill_shell_process(process, force=False):
    if sys.platform != "win32":
        signal = "-KILL" if force else "-TERM"
        subprocess.call(["pkill", signal, "-P", str(process.pid)])
    else:
        if force:
            process.kill()
        else:
            process.terminate()
