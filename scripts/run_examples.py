#!/usr/bin/env python3

import glob
import subprocess
import sys


def main():
    for path in sorted(glob.glob("examples/[0-9][0-9]*.py")):
        print(f"Running {path}...")
        result = subprocess.run(["uv", "run", path], check=False)

        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
