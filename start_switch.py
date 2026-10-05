import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
UI = ROOT / "switch-ui"

PYTHON = sys.executable


print("Starting SWITCH...")


print("Starting SWITCH backend...")

python_process = subprocess.Popen(
    [PYTHON, "main.py"],
    cwd=ROOT
)


time.sleep(2)


print("Starting React UI...")

react_process = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd=UI,
    shell=True
)


time.sleep(3)


print("Starting SWITCH desktop UI...")

electron_process = subprocess.Popen(
    ["npm", "run", "electron"],
    cwd=UI,
    shell=True
)


print()
print("================================")
print("       SWITCH IS RUNNING")
print("================================")
print()


try:
    while True:

        # Python backend has exited.
        # Shut down the UI stack too.
        if python_process.poll() is not None:

            print()
            print("SWITCH backend stopped.")
            print("Closing SWITCH UI...")

            break

        time.sleep(0.5)


except KeyboardInterrupt:

    print()
    print("Shutting down SWITCH...")


finally:

    for process in [
        electron_process,
        react_process,
    ]:

        try:
            process.terminate()
        except Exception:
            pass


    time.sleep(1)


    try:
        if python_process.poll() is None:
            python_process.terminate()
    except Exception:
        pass


    print("SWITCH stopped.")