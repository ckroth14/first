#!/usr/bin/env python3
"""Compare two plain .txt files by line content, ignoring order.

Treats each file as a multiset of lines: reports which lines appear only
in file1, only in file2, and in both, along with counts. Makes no
assumptions about file format, structure, or domain (no columns, no
headers, no special markers) — just raw line content.

Single-file, stdlib-only script. Works on Windows, macOS, and Linux.

Usage:
    python compare_files.py file1.txt file2.txt
"""
import argparse
import sys
from collections import Counter


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        return f.read().splitlines()


def main():
    parser = argparse.ArgumentParser(
        description="Compare two .txt files by line content, ignoring order."
    )
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()

    try:
        left_lines = read_lines(args.file1)
        right_lines = read_lines(args.file2)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    left_count = Counter(left_lines)
    right_count = Counter(right_lines)

    only_left = left_count - right_count
    only_right = right_count - left_count
    common = left_count & right_count

    def report(title, counter):
        print(f"{title} ({sum(counter.values())} line(s)):")
        for line, n in counter.items():
            for _ in range(n):
                print(f"  {line}")

    report(f"Only in {args.file1}", only_left)
    print()
    report(f"Only in {args.file2}", only_right)
    print()
    print(f"Common to both: {sum(common.values())} line(s)")

    print()
    if not only_left and not only_right:
        print("Files contain identical lines (order ignored).")
    else:
        print(f"{sum(only_left.values()) + sum(only_right.values())} differing line(s) found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
