"""CLI entry point: parse a .policy file and emit YAML."""

import sys

from policy_dsl.parser import parse_file
from policy_dsl.transformer import transform
from policy_dsl.yaml_emitter import to_yaml


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m policy_dsl.cli <path-to-policy-file>")
        sys.exit(1)

    path = sys.argv[1]
    parsed = parse_file(path)
    model = transform(parsed)
    print(to_yaml(model))


if __name__ == "__main__":
    main()
