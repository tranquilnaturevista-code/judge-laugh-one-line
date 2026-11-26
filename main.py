#!/usr/bin/env python3
"""One-line comedy entry for the make.fun bounty
"Make the Judge Laugh in One Line".

The program writes a single hand-written funny line to
/output/entry.txt (or $OUTPUT_DIR/entry.txt). Before writing it
checks the line against the competition gate: UTF-8 text, 1-200
characters, not only whitespace, and a single line (no newline).
"""

import argparse
import os
import sys

LINE = (
    "The barista misspelled my name so badly on my cup "
    "that I legally changed it to match."
)

MIN_CHARS = 1
MAX_CHARS = 200


def validate_entry(text):
    """Check `text` against the gate; return a list of problems (empty = valid)."""
    problems = []
    if not text.strip():
        problems.append("entry is blank")
    # The gate counts characters, not bytes: a line with non-ASCII
    # characters may be within 200 characters yet over 200 UTF-8
    # bytes, and it still has to pass.
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        problems.append(
            f"entry is {len(text)} characters, gate needs 1-200"
        )
    if "\n" in text or "\r" in text:
        problems.append("entry must be a single line")
    return problems


def fail(problems, where=""):
    """Print each problem to stderr and exit non-zero."""
    prefix = f"gate failure{where}: " if where else "gate failure: "
    for problem in problems:
        print(prefix + problem, file=sys.stderr)
    sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Write the Make the Judge Laugh in One Line entry."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="check the gate and print the line without writing it",
    )
    args = parser.parse_args(argv)

    problems = validate_entry(LINE)
    if problems:
        fail(problems)

    if args.dry_run:
        # Only validate, without touching the disk, so the entry can
        # be tested where /output is not writable.
        print(f"gate ok: {len(LINE)} characters")
        print(LINE)
        return

    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(LINE)

    with open(path, encoding="utf-8") as handle:
        written = handle.read()
    if written != LINE:
        print("entry mismatch after write", file=sys.stderr)
        sys.exit(1)
    # Check the gate again against what actually landed on disk, so
    # a write that silently changed the text can never pass quietly.
    problems = validate_entry(written)
    if problems:
        fail(problems, where=" on disk")

    print(
        f"Wrote entry.txt: {len(written)} characters "
        f"({len(written.encode('utf-8'))} bytes)"
    )


if __name__ == "__main__":
    main()
