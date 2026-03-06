"""CLI entry point: parse a .policy file and emit YAML."""

import argparse

from policy_dsl.yaml_emitter import to_yaml


def _detect_format(path: str) -> str:
    """Auto-detect format from filename: *_nl.policy -> nl, else bdd."""
    if path.endswith("_nl.policy"):
        return "nl"
    return "bdd"


def _parse_and_transform(path: str, fmt: str):
    """Parse and transform using the appropriate pipeline."""
    if fmt == "nl":
        from policy_dsl.parser_nl import parse_file
        from policy_dsl.transformer_nl import transform
    else:
        from policy_dsl.parser import parse_file
        from policy_dsl.transformer import transform

    parsed = parse_file(path)
    return transform(parsed)


def main():
    parser = argparse.ArgumentParser(
        description="Parse a policy DSL file and emit YAML."
    )
    parser.add_argument("path", help="Path to a .policy file")
    parser.add_argument(
        "--format",
        choices=["bdd", "nl"],
        default=None,
        help="DSL format: bdd (Gherkin) or nl (natural language). "
        "Auto-detected from filename if omitted.",
    )
    args = parser.parse_args()

    fmt = args.format or _detect_format(args.path)
    model = _parse_and_transform(args.path, fmt)
    print(to_yaml(model))


if __name__ == "__main__":
    main()
