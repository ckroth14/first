#!/usr/bin/env python3
"""Side-by-side comparison of two text files.

Single-file, stdlib-only script. Works on Windows, macOS, and Linux
(no platform-specific calls).

Usage:
    python compare_files.py file1.txt file2.txt
    python compare_files.py file1.txt file2.txt --width 40
"""
import argparse
import difflib
import shutil
import sys


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        return f.read().splitlines()


def fit(text, width):
    if len(text) > width:
        return text[: width - 1] + "…"
    return text.ljust(width)


def side_by_side(left_lines, right_lines, width):
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)
    rows = []
    diff_count = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        left_chunk = left_lines[i1:i2]
        right_chunk = right_lines[j1:j2]
        if tag == "equal":
            for l, r in zip(left_chunk, right_chunk):
                rows.append((l, " ", r))
        else:
            marker = {"replace": "|", "delete": "<", "insert": ">"}[tag]
            for l, r in zip_longest(left_chunk, right_chunk):
                rows.append((l if l is not None else "", marker, r if r is not None else ""))
                diff_count += 1
    return rows, diff_count


def zip_longest(a, b):
    la, lb = len(a), len(b)
    n = max(la, lb)
    for k in range(n):
        yield (a[k] if k < la else None, b[k] if k < lb else None)


def main():
    parser = argparse.ArgumentParser(description="Compare two text files side by side.")
    parser.add_argument("file1")
    parser.add_argument("file2")
    parser.add_argument("--width", type=int, default=0,
                         help="Width of each column (default: auto-fit to terminal)")
    args = parser.parse_args()

    try:
        left_lines = read_lines(args.file1)
        right_lines = read_lines(args.file2)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    if args.width:
        col_width = args.width
    else:
        term_width = shutil.get_terminal_size(fallback=(120, 24)).columns
        col_width = max(20, (term_width - 3) // 2)

    rows, diff_count = side_by_side(left_lines, right_lines, col_width)

    print(f"{fit(args.file1, col_width)} | {fit(args.file2, col_width)}")
    print("-" * col_width + "-+-" + "-" * col_width)
    for left, marker, right in rows:
        print(f"{fit(left, col_width)} {marker} {fit(right, col_width)}")

    print()
    if diff_count == 0:
        print("Files are identical.")
    else:
        print(f"{diff_count} differing line group(s) found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
