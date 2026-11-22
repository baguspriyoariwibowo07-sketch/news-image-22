"""Entry program for news-image-20261122.

Copies the pre-rendered front page (entry.png, held in this repository)
to the grader's output directory, byte for byte. Standard library only;
no network, no randomness, no clock: two runs write identical bytes.
"""
import os
import shutil
import sys


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    dest_dir = output_dir()
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "entry.png")
    shutil.copyfile(src, dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
