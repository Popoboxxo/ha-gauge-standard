#!/usr/bin/env python3
"""Conventional Commits check for pre-commit (commit-msg stage).

Usage: check_commit_msg.py <commit-msg-file>
"""
import re
import sys

PATTERN = re.compile(
    r"^(feat|fix|docs|chore|refactor|test|perf|build|ci|revert)"
    r"(\([a-z0-9-]+\))?!?: .{10,}"
)


def main() -> int:
    subject = ""
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as fh:
            lines = fh.read().splitlines()
            subject = lines[0] if lines else ""
    else:
        return 0
    if subject.startswith(("Merge ", "Revert ")):
        return 0
    if PATTERN.match(subject):
        return 0
    print("ERROR: commit message must follow Conventional Commits:")
    print("  <type>(<scope>): <subject>  (type: feat|fix|docs|chore|refactor|test|perf|build|ci|revert)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
