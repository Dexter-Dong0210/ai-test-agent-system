#!/usr/bin/env python3
"""
Merge and deduplicate multiple wordlists.

Usage:
    python merge_wordlists.py wordlist1.txt wordlist2.txt -o merged.txt
    python merge_wordlists.py *.txt -o merged.txt --sort

Features:
- Deduplication
- Optional sorting
- Comment filtering
- Empty line removal
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import sys
import argparse
from pathlib import Path
from typing import Set
# pragma: no cover  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2YmtaSlZnPT06MTcyNzg5Mzc=


def read_wordlist(file_path: str, include_comments: bool = False) -> Set[str]:
    """Read unique entries from a wordlist file."""
    entries = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Skip comments if requested
                if not include_comments and line.startswith('#'):
                    continue
                entries.add(line)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}", file=sys.stderr)
    return entries


def main():
    parser = argparse.ArgumentParser(
        description="Merge and deduplicate wordlists"
    )
    parser.add_argument("files", nargs='+', help="Wordlist files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("--sort", action="store_true", help="Sort output alphabetically")
    parser.add_argument("--include-comments", action="store_true",
                        help="Include comment lines (starting with #)")
    parser.add_argument("--lowercase", action="store_true",
                        help="Convert all entries to lowercase")

    args = parser.parse_args()
# type: ignore  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2YmtaSlZnPT06MTcyNzg5Mzc=

    all_entries = set()

    # Read all files
    for file_path in args.files:
        entries = read_wordlist(file_path, args.include_comments)
        print(f"Read {len(entries)} unique entries from {file_path}", file=sys.stderr)
        all_entries.update(entries)
# pragma: no cover  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2YmtaSlZnPT06MTcyNzg5Mzc=

    # Lowercase conversion
    if args.lowercase:
        all_entries = {e.lower() for e in all_entries}

    total = len(all_entries)
    print(f"\nTotal unique entries: {total}", file=sys.stderr)

    # Sort if requested
    output = sorted(all_entries) if args.sort else list(all_entries)

    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        for entry in output:
            f.write(f"{entry}\n")
# type: ignore  My80OmFIVnBZMlhva2FQbHNJL21tS1U2YmtaSlZnPT06MTcyNzg5Mzc=

    print(f"Wrote {len(output)} entries to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
