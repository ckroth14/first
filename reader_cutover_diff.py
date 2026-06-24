#!/usr/bin/env python3
"""Compare two access-control "Card Holders Associated With A Door" reports.

Used during a reader cutover: run the report against the OLD reader, add the
access codes / reader groups to the NEW reader, run the report against the
NEW reader, then diff the two. Cardholders who only show up on one side were
granted access through the third mechanism (direct cardholder assignment)
and need to be added to the new reader by hand.

Single-file, stdlib-only script. Works on Windows via:
    python reader_cutover_diff.py old_report.txt new_report.txt
"""
import argparse
import csv
import re
import sys

HEADER_MARKER = "Last Name:"
TOTAL_MARKER = "Total Number of Records:"
READER_RE = re.compile(r"Reader/Door:\s*(.+?)\s*-\s*Owned By:")


def parse_report(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    reader_name = None
    records = {}
    in_data = False

    for line in lines:
        if reader_name is None:
            m = READER_RE.search(line)
            if m:
                reader_name = m.group(1).strip()
                continue

        if not in_data:
            if line.startswith(HEADER_MARKER):
                in_data = True
            continue

        if line.startswith(TOTAL_MARKER):
            break
        if not line.strip():
            continue

        fields = line.split("\t")
        fields += [""] * (7 - len(fields))
        last, first, card_no = fields[0].strip(), fields[1].strip(), fields[2].strip()
        fac_code, emp_ref, company, time_code = (
            fields[3].strip(), fields[4].strip(), fields[5].strip(), fields[6].strip()
        )
        if not card_no:
            continue
        records[card_no] = {
            "last": last,
            "first": first,
            "card_no": card_no,
            "fac_code": fac_code,
            "emp_ref": emp_ref,
            "company": company,
            "time_code": time_code,
        }

    if reader_name is None:
        reader_name = path
    return reader_name, records


def main():
    parser = argparse.ArgumentParser(
        description="Diff two reader cardholder reports and list cardholders missing from one side."
    )
    parser.add_argument("old_report", help="Report run against the OLD reader")
    parser.add_argument("new_report", help="Report run against the NEW reader")
    parser.add_argument("-o", "--output", default="cutover_diff_report.csv",
                         help="Output CSV path (default: cutover_diff_report.csv)")
    args = parser.parse_args()

    try:
        old_name, old_records = parse_report(args.old_report)
        new_name, new_records = parse_report(args.new_report)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    old_keys = set(old_records)
    new_keys = set(new_records)
    missing_from_new = old_keys - new_keys
    extra_on_new = new_keys - old_keys

    rows = []
    for card_no in sorted(missing_from_new):
        r = old_records[card_no]
        rows.append([r["card_no"], r["last"], r["first"], r["emp_ref"], r["time_code"],
                     "Missing from new reader", old_name, new_name])
    for card_no in sorted(extra_on_new):
        r = new_records[card_no]
        rows.append([r["card_no"], r["last"], r["first"], r["emp_ref"], r["time_code"],
                     "Extra on new reader (not on old)", old_name, new_name])

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Card No.", "Last Name", "First Name", "Employee Ref",
                          "Time Code", "Status", "Old Reader", "New Reader"])
        writer.writerows(rows)

    print(f"Old reader: {old_name} ({len(old_records)} cardholders)")
    print(f"New reader: {new_name} ({len(new_records)} cardholders)")
    print(f"Missing from new reader: {len(missing_from_new)}")
    print(f"Extra on new reader (not on old): {len(extra_on_new)}")
    print(f"Report written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
