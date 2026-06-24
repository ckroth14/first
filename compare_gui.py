#!/usr/bin/env python3
"""GUI to compare two .txt files (old vs new) and save the result to a .txt file.

Pick an old file and a new file, click Compare, then choose where to save
the report. Comparison is by line content, ignoring order: it lists lines
only in the old file, only in the new file, and a count of lines common
to both.

Single-file, stdlib-only (tkinter). Works on Windows, macOS, and Linux.

Usage:
    python compare_gui.py
"""
import sys
import tkinter as tk
from collections import Counter
from tkinter import filedialog, messagebox, ttk


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        return f.read().splitlines()


def build_report(old_path, new_path):
    left_count = Counter(read_lines(old_path))
    right_count = Counter(read_lines(new_path))

    only_old = left_count - right_count
    only_new = right_count - left_count
    common = left_count & right_count

    lines = []

    def section(title, counter):
        lines.append(f"{title} ({sum(counter.values())} line(s)):")
        for line, n in counter.items():
            for _ in range(n):
                lines.append(f"  {line}")

    section(f"Only in {old_path}", only_old)
    lines.append("")
    section(f"Only in {new_path}", only_new)
    lines.append("")
    lines.append(f"Common to both: {sum(common.values())} line(s)")
    lines.append("")
    if not only_old and not only_new:
        lines.append("Files contain identical lines (order ignored).")
    else:
        lines.append(f"{sum(only_old.values()) + sum(only_new.values())} differing line(s) found.")

    return "\n".join(lines) + "\n"


class CompareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Compare")
        self.resizable(False, False)

        self.old_path = tk.StringVar()
        self.new_path = tk.StringVar()

        pad = {"padx": 8, "pady": 6}

        ttk.Label(self, text="Old file:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self.old_path, width=50).grid(row=0, column=1, **pad)
        ttk.Button(self, text="Browse...", command=self.browse_old).grid(row=0, column=2, **pad)

        ttk.Label(self, text="New file:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(self, textvariable=self.new_path, width=50).grid(row=1, column=1, **pad)
        ttk.Button(self, text="Browse...", command=self.browse_new).grid(row=1, column=2, **pad)

        ttk.Button(self, text="Compare", command=self.compare).grid(row=2, column=1, **pad)

        self.status = ttk.Label(self, text="")
        self.status.grid(row=3, column=0, columnspan=3, sticky="w", **pad)

    def browse_old(self):
        path = filedialog.askopenfilename(title="Select old file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.old_path.set(path)

    def browse_new(self):
        path = filedialog.askopenfilename(title="Select new file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.new_path.set(path)

    def compare(self):
        old_path = self.old_path.get()
        new_path = self.new_path.get()
        if not old_path or not new_path:
            messagebox.showerror("Missing file", "Please select both an old file and a new file.")
            return

        try:
            report = build_report(old_path, new_path)
        except OSError as e:
            messagebox.showerror("Error reading file", str(e))
            return

        save_path = filedialog.asksaveasfilename(
            title="Save comparison result",
            defaultextension=".txt",
            initialfile="comparison_result.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(report)
        except OSError as e:
            messagebox.showerror("Error saving file", str(e))
            return

        self.status.config(text=f"Saved to {save_path}")
        messagebox.showinfo("Done", f"Comparison saved to:\n{save_path}")


def main():
    app = CompareApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
