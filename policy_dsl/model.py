"""Canonical Python model for a parsed policy."""

from dataclasses import dataclass, field


@dataclass
class PolicyModel:
    """Internal representation of a parsed policy spec."""

    # Metadata
    id: str = ""
    description: str = ""
    enabled: bool = True

    # Policy
    effect: str = "allow"

    # Object selector
    resource_types: list[str] = field(default_factory=list)
    resource_tag_key: str = ""

    # Principal selector
    entitlements: list[str] = field(default_factory=list)
    principal_scope_tag: str = ""

    # Actions
    privileges: list[str] = field(default_factory=list)
    include_parent_grants: bool = False

    # Narrative (informational only)
    feature_title: str = ""
    scenario_title: str = ""
    role: str = ""
    desire: str = ""
    benefit: str = ""
