#%%
#!/usr/bin/python3

import subprocess
from subprocess import Popen, PIPE

res = Popen(["node", "start.js"], stdin=PIPE, stdout=PIPE)

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line)
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    print(return_code)
    if return_code:
        print(return_code)
        raise subprocess.CalledProcessError(return_code, cmd)

# Example
for path in execute(["soulseek", "login"]):
    print(path, end="")
# %%