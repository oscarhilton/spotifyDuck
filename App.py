#!/usr/bin/python3

import subprocess

from Hub import Hub

main = subprocess.Popen(["python3", "Main.py"])
rmps = subprocess.Popen(["python3", "RumpsApp.py"])

try:
    while True:
        pass
except KeyboardInterrupt:
    main.terminate()
    rmps.terminate()
