# appauto/runners/ui_runner.py
import subprocess


def run(testpaths: str, extra_args: tuple):
    cmd = ["playwright", "test", testpaths] + list(extra_args)
    subprocess.run(cmd)
