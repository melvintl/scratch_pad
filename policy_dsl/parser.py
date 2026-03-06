"""Parse BDD-style policy DSL files using textX."""

import os
from textx import metamodel_from_file


GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "grammar", "policy.tx")


def get_metamodel():
    """Return the textX metamodel for the policy DSL."""
    return metamodel_from_file(GRAMMAR_PATH)


def parse_file(path: str):
    """Parse a .policy file and return the textX model."""
    mm = get_metamodel()
    return mm.model_from_file(path)


def parse_string(text: str):
    """Parse a policy DSL string and return the textX model."""
    mm = get_metamodel()
    return mm.model_from_str(text)
