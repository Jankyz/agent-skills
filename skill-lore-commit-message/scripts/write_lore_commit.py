#!/usr/bin/env python3
"""Build and optionally submit a Lore commit payload."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_SCOPE_RISK = {"narrow", "moderate", "wide"}
VALID_REVERSIBILITY = {"clean", "migration-needed", "irreversible"}
LORE_ID_RE = re.compile(r"^[0-9a-f]{8}$")


def repeated_text(values: list[str] | None) -> list[str]:
    return [value.strip() for value in values or [] if value.strip()]


def validate_rejected(values: list[str]) -> None:
    for value in values:
        if " | " not in value:
            raise SystemExit(
                f"Rejected entry must use 'alternative | reason' format: {value!r}"
            )


def validate_lore_ids(field_name: str, values: list[str]) -> None:
    for value in values:
        if not LORE_ID_RE.fullmatch(value):
            raise SystemExit(
                f"{field_name} entries must be 8-character lowercase hex Lore IDs: {value!r}"
            )


def load_body(args: argparse.Namespace) -> str | None:
    body_parts = repeated_text(args.body)
    if args.body_file:
        file_text = Path(args.body_file).read_text(encoding="utf-8").strip()
        if file_text:
            body_parts.append(file_text)
    if not body_parts:
        return None
    return "\n".join(body_parts)


def parse_command(command: str) -> list[str]:
    return shlex.split(command)


def detect_lore_command(explicit: str | None) -> list[str]:
    if explicit:
        return parse_command(explicit)
    if shutil.which("lore"):
        return ["lore"]
    if shutil.which("npx"):
        return ["npx", "lore"]
    raise SystemExit("Could not find lore or npx. Install lore-protocol first.")


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    if len(args.intent) > 72:
        print(
            "Warning: the intent line exceeds 72 characters.",
            file=sys.stderr,
        )

    constraints = repeated_text(args.constraint)
    rejected = repeated_text(args.rejected)
    directives = repeated_text(args.directive)
    tested = repeated_text(args.tested)
    not_tested = repeated_text(args.not_tested)
    supersedes = repeated_text(args.supersedes)
    depends_on = repeated_text(args.depends_on)
    related = repeated_text(args.related)

    validate_rejected(rejected)
    validate_lore_ids("Supersedes", supersedes)
    validate_lore_ids("Depends-on", depends_on)
    validate_lore_ids("Related", related)

    trailers: dict[str, object] = {}
    if constraints:
        trailers["Constraint"] = constraints
    if rejected:
        trailers["Rejected"] = rejected
    if args.confidence:
        trailers["Confidence"] = args.confidence
    if args.scope_risk:
        trailers["Scope-risk"] = args.scope_risk
    if args.reversibility:
        trailers["Reversibility"] = args.reversibility
    if directives:
        trailers["Directive"] = directives
    if tested:
        trailers["Tested"] = tested
    if not_tested:
        trailers["Not-tested"] = not_tested
    if supersedes:
        trailers["Supersedes"] = supersedes
    if depends_on:
        trailers["Depends-on"] = depends_on
    if related:
        trailers["Related"] = related

    payload: dict[str, object] = {"intent": args.intent}
    body = load_body(args)
    if body:
        payload["body"] = body
    if trailers:
        payload["trailers"] = trailers
    return payload


def write_payload(path: str, payload: dict[str, object]) -> None:
    Path(path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def commit_payload(command: list[str], payload: dict[str, object]) -> None:
    completed = subprocess.run(
        [*command, "commit"],
        input=json.dumps(payload, ensure_ascii=True),
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a Lore protocol commit payload and optionally send it to lore commit."
    )
    parser.add_argument("--intent", required=True, help="Commit intent line: explain why.")
    parser.add_argument(
        "--body",
        action="append",
        help="Body paragraph or line. Repeat to add multiple lines.",
    )
    parser.add_argument(
        "--body-file",
        help="Path to a UTF-8 text file with additional body content.",
    )
    parser.add_argument("--constraint", action="append", help="Repeatable Constraint trailer.")
    parser.add_argument(
        "--rejected",
        action="append",
        help="Repeatable Rejected trailer in 'alternative | reason' format.",
    )
    parser.add_argument(
        "--confidence",
        choices=sorted(VALID_CONFIDENCE),
        help="Confidence trailer.",
    )
    parser.add_argument(
        "--scope-risk",
        choices=sorted(VALID_SCOPE_RISK),
        help="Scope-risk trailer.",
    )
    parser.add_argument(
        "--reversibility",
        choices=sorted(VALID_REVERSIBILITY),
        help="Reversibility trailer.",
    )
    parser.add_argument("--directive", action="append", help="Repeatable Directive trailer.")
    parser.add_argument("--tested", action="append", help="Repeatable Tested trailer.")
    parser.add_argument(
        "--not-tested",
        dest="not_tested",
        action="append",
        help="Repeatable Not-tested trailer.",
    )
    parser.add_argument(
        "--supersedes",
        action="append",
        help="Repeatable Supersedes Lore ID.",
    )
    parser.add_argument(
        "--depends-on",
        dest="depends_on",
        action="append",
        help="Repeatable Depends-on Lore ID.",
    )
    parser.add_argument("--related", action="append", help="Repeatable Related Lore ID.")
    parser.add_argument(
        "--json-out",
        help="Write the generated payload to a JSON file.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the generated payload to stdout.",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Send the payload to lore commit.",
    )
    parser.add_argument(
        "--lore-bin",
        help='Lore command to execute, e.g. "lore" or "npx lore".',
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    payload = build_payload(args)

    if args.json_out:
        write_payload(args.json_out, payload)

    if args.print_json or (not args.commit and not args.json_out):
        print(json.dumps(payload, indent=2, ensure_ascii=True))

    if args.commit:
        lore_command = detect_lore_command(args.lore_bin)
        commit_payload(lore_command, payload)


if __name__ == "__main__":
    main()
