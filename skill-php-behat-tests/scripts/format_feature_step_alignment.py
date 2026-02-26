#!/usr/bin/env python3
"""Format Gherkin step indentation so step text starts in one aligned column."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Iterable, List, Tuple

STEP_RE = re.compile(r'^(?P<indent>[ \t]*)(?P<kw>Given|When|Then|And|But)\s+(?P<rest>.*?)(?P<nl>\r?\n)?$')
BLOCK_RE = re.compile(r'^(?P<indent>[ \t]*)(Scenario(?: Outline)?|Background):')
KEYWORD_OFFSET = {
    'Given': 0,
    'When': 1,
    'Then': 1,
    'And': 2,
    'But': 2,
}


def collect_feature_files(paths: Iterable[str]) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []

    for raw_path in paths:
        path = pathlib.Path(raw_path)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob('*.feature') if p.is_file()))
            continue

        if path.is_file():
            if path.suffix != '.feature':
                raise ValueError(f'Expected a .feature file, got: {path}')
            files.append(path)
            continue

        raise FileNotFoundError(f'Path does not exist: {path}')

    return files


def format_feature_lines(lines: List[str]) -> Tuple[List[str], bool]:
    current_base_indent: int | None = None
    changed = False
    output: List[str] = []

    for line in lines:
        block_match = BLOCK_RE.match(line)
        if block_match:
            current_base_indent = len(block_match.group('indent').expandtabs(4)) + 4
            output.append(line)
            continue

        step_match = STEP_RE.match(line)
        if step_match and current_base_indent is not None:
            keyword = step_match.group('kw')
            rest = step_match.group('rest')
            newline = step_match.group('nl') or ''

            target_line = (
                ' ' * (current_base_indent + KEYWORD_OFFSET[keyword])
                + keyword
                + ' '
                + rest
                + newline
            )

            if target_line != line:
                changed = True

            output.append(target_line)
            continue

        output.append(line)

    return output, changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Align Given/When/Then/And/But step text in .feature files.'
    )
    parser.add_argument(
        'paths',
        nargs='*',
        default=['features'],
        help='Feature files or directories (default: features)',
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check formatting only (non-zero exit if changes are needed)',
    )

    args = parser.parse_args()

    try:
        files = collect_feature_files(args.paths)
    except (FileNotFoundError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if not files:
        print('No .feature files found.', file=sys.stderr)
        return 2

    changed_files: List[pathlib.Path] = []

    for file_path in files:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)
        formatted_lines, changed = format_feature_lines(lines)

        if changed:
            changed_files.append(file_path)
            if not args.check:
                file_path.write_text(''.join(formatted_lines), encoding='utf-8')

    if args.check:
        if changed_files:
            for file_path in changed_files:
                print(file_path)
            print(f'{len(changed_files)} file(s) require formatting.', file=sys.stderr)
            return 1

        print('All feature files are correctly formatted.')
        return 0

    print(f'Formatted {len(changed_files)} file(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
