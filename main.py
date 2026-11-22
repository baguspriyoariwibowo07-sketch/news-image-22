"""Entry point: draw the 22 November 2026 front page to entry.png.

Standard library only. Writes to $MAKEFUN_OUTPUT_DIR (the grader's
/output) when set, otherwise to /output, falling back to ./out.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from draw22 import build_png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "out")
        os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(build_png())
    print("wrote", path)


if __name__ == "__main__":
    main()
