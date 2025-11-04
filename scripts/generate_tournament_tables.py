#!/usr/bin/env python3
"""
Generate tournament tables for release notes and full markdown output.

Usage: run this from the repository root after `final_release/tournament_results.csv` exists.
It writes:
 - final_release/tournament_results.md  (full markdown table)
 - final_release/table_part1.txt        (engines 1-10)
 - final_release/table_part2.txt        (engines 11-20)
 - final_release/table_part3.txt        (engines 21+)

It prints nothing on success. Exit with non-zero if input is missing or malformed.
"""
import csv
import sys
from pathlib import Path

CSV_PATH = Path('final_release/tournament_results.csv')
MD_PATH = Path('final_release/tournament_results.md')
# write split parts into final_release/ so workflow can upload them easily
PART1 = Path('final_release/table_part1.txt')
PART2 = Path('final_release/table_part2.txt')
PART3 = Path('final_release/table_part3.txt')
FULL_BODY = Path('final_release/table_full_for_body.txt')

if not CSV_PATH.exists():
    print('Tournament results not available: final_release/tournament_results.csv not found', file=sys.stderr)
    sys.exit(2)

with CSV_PATH.open(newline='') as f:
    reader = csv.reader(f)
    rows = [r for r in reader]

if not rows:
    print('Tournament results CSV is empty', file=sys.stderr)
    sys.exit(3)

header = rows[0]
data = rows[1:]

def escape_cell(c):
    return str(c).replace('|', '\\|')

# Full markdown
with MD_PATH.open('w', encoding='utf-8') as out:
    out.write('| ' + ' | '.join(header) + ' |\n')
    out.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
    for r in data:
        out.write('| ' + ' | '.join(escape_cell(c) for c in r) + ' |\n')

# Split into parts
part1 = data[0:10]
part2 = data[10:20]
part3 = data[20:]

def write_part(path: Path, title: str, rows_part):
    with path.open('w', encoding='utf-8') as out:
        # For part1 we include title and header. For part2/part3 we only include rows
        if title.startswith('Tournament Results (Part 1'):
            out.write(f'### {title}\n\n')
            out.write('| ' + ' | '.join(header) + ' |\n')
            out.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
        for r in rows_part:
            out.write('| ' + ' | '.join(escape_cell(c) for c in r) + ' |\n')

write_part(PART1, 'Tournament Results (Part 1 of 3: Engines 1-10)', part1)
write_part(PART2, 'Tournament Results (Part 2 of 3: Engines 11-20)', part2)
write_part(PART3, f'Tournament Results (Part 3 of 3: Engines 21-{len(data)})', part3)

# Create a single combined table for the release body. This keeps one title/header
# at the top and then prints all rows without repeating the header between parts.
with FULL_BODY.open('w', encoding='utf-8') as out:
    out.write('# Tournament Results\n\n')
    # write header once
    out.write('| ' + ' | '.join(header) + ' |\n')
    out.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
    for r in data:
        out.write('| ' + ' | '.join(escape_cell(c) for c in r) + ' |\n')

# Exit success
sys.exit(0)
