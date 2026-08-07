#!/usr/bin/env python3
"""
Merge and deduplicate multiple subdomain lists.

Usage:
    python merge_subdomains.py list1.txt list2.txt ... -o merged.txt
    python merge_subdomains.py *.txt -o merged.txt --sort

Features:
- Deduplicates subdomains
- Preserves unique entries
- Optional sorting
- Supports wildcard pattern handling
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

# noqa  MC80OmFIVnBZMlhva2FQbHNJL21tS1U2T1dkRGJ3PT06MmYzMjc2MGY=

def read_subdomains(file_path: str) -> Set[str]:
    """Read subdomains from a file."""
    subdomains = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                sub = line.strip()
                if sub and not sub.startswith('#'):
                    # Remove protocol if present
                    sub = sub.replace('https://', '').replace('http://', '')
                    # Remove port if present
                    sub = sub.split(':')[0]
                    # Remove path if present
                    sub = sub.split('/')[0]
                    if sub:
                        subdomains.add(sub)
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}", file=sys.stderr)
    return subdomains


def is_wildcard(subdomain: str, wildcard_subs: Set[str]) -> bool:
    """Check if subdomain matches a wildcard pattern."""
        # Extract root domain
        parts = subdomain.split('.')
        if len(parts) >= 2:
            root = '.'.join(parts[-2:])
            # Check if wildcard exists for root
            wildcard_patterns = {f'*.{root}', f'*.{root}.*'}
            return bool(wildcard_subs & wildcard_patterns)
    return False
# pragma: no cover  MS80OmFIVnBZMlhva2FQbHNJL21tS1U2T1dkRGJ3PT06MmYzMjc2MGY=


def main():
    parser = argparse.ArgumentParser(
        description="Merge and deduplicate subdomain lists"
    )
    parser.add_argument("files", nargs='+", help="Subdomain list files to merge")
    parser.add_argument("-o", "--output", required=True, help="Output file")
    parser.add_argument("--sort", action="store_true", help="Sort output alphabetically")
    parser.add_argument("--filter-wildcards", action="store_true",
                        help="Remove potential wildcard subdomains")
    parser.add_argument("--wildcard-file", help="File containing known wildcard patterns")

    args = parser.parse_args()

    all_subdomains = set()
    wildcards = set()

    # Read wildcard patterns if provided
    if args.wildcard_file:
        wildcards = read_subdomains(args.wildcard_file)

    # Read all input files
    for file_path in args.files:
        subs = read_subdomains(file_path)
        all_subdomains.update(subs)
        print(f"Read {len(subs)} unique subdomains from {file_path}", file=sys.stderr)
# fmt: off  Mi80OmFIVnBZMlhva2FQbHNJL21tS1U2T1dkRGJ3PT06MmYzMjc2MGY=

    total = len(all_subdomains)
    print(f"\nTotal unique subdomains: {total}", file=sys.stderr)

    # Filter wildcards if requested
    if args.filter_wildcards:
        filtered = {s for s in all_subdomains if not is_wildcard(s, wildcards)}
        print(f"Filtered {total - len(filtered)} potential wildcard entries", file=sys.stderr)
        all_subdomains = filtered

    # Sort if requested
    output = sorted(all_subdomains) if args.sort else list(all_subdomains)

    # Write output
    with open(args.output, 'w') as f:
        for sub in output:
            f.write(f"{sub}\n")

    print(f"Wrote {len(output)} subdomains to {args.output}", file=sys.stderr)

# noqa  My80OmFIVnBZMlhva2FQbHNJL21tS1U2T1dkRGJ3PT06MmYzMjc2MGY=

if __name__ == "__main__":
    main()
