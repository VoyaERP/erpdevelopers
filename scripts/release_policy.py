"""Pure, shared release-branch policy. Never edits Git or a Frappe site."""
import argparse
import re

RELEASE_BRANCHES = ("version-16", "production-v16")


def validate_transition(current, target, sha, allow_switch=False):
    """Only an explicit, pinned integration-to-production switch is permitted."""
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Supply an exact 40-character EXPECTED_SHA")
    if current not in RELEASE_BRANCHES or target not in RELEASE_BRANCHES:
        raise ValueError("Only version-16 and production-v16 are deployment branches")
    if current != target and not (
        current == "version-16" and target == "production-v16" and allow_switch
    ):
        raise ValueError("Branch switch needs explicit ALLOW_BRANCH_SWITCH=1; production downgrade is refused")


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
