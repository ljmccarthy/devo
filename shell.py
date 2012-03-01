import sys, subprocess

if sys.platform == "win32":
    shell = "cmd"
else:
    shell = "bash"

def run_shell_command(cmdline, pipe_output=True, **kwargs):
    pipe = subprocess.PIPE if pipe_output else None
    process = subprocess.Popen([shell],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE if pipe_output else None,
        stderr = subprocess.STDOUT if pipe_output else None,
        bufsize = 1,
        close_fds = (sys.platform != "win32"),
        shell = False,
        **kwargs)
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
