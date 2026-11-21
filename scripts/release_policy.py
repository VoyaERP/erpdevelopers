"""Pure, shared release-branch policy. Never edits Git or a Frappe site."""
import argparse
import re

RELEASE_BRANCHES = ("version-15", "version-16")
LEGACY_V16_BRANCHES = ("production-v16", "release/v16-final-20261121")


def validate_transition(current, target, sha, allow_switch=False):
    """Permit pinned same-branch updates or an explicit legacy-v16 migration.

    Version 15 and 16 installations are never interchangeable. The caller must
    independently validate the installed Frappe major version and target site.
    """
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Supply an exact 40-character EXPECTED_SHA")
    if target not in RELEASE_BRANCHES:
        raise ValueError("Only version-15 and version-16 are release targets")
    if current == target:
        return
    if current in LEGACY_V16_BRANCHES and target == "version-16" and allow_switch:
        return
    raise ValueError("Only an explicit legacy-v16 to version-16 switch is permitted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current")
    parser.add_argument("target")
    parser.add_argument("sha")
    parser.add_argument("--allow-switch", choices=("0", "1"), default="0")
    args = parser.parse_args()
    try:
        validate_transition(args.current, args.target, args.sha, args.allow_switch == "1")
    except ValueError as exc:
        parser.exit(2, f"STOP: {exc}\n")


if __name__ == "__main__":
    main()
