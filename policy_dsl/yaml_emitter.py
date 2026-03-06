"""Generate YAML output from a PolicyModel."""

import yaml

from policy_dsl.model import PolicyModel

# Version stamped into every generated YAML
SCHEMA_VERSION = "1.0.0"


def to_dict(model: PolicyModel) -> dict:
    """Convert a PolicyModel to the target YAML dict structure."""
    return {
        "version": SCHEMA_VERSION,
        "metadata": {
            "id": model.id,
            "description": model.description,
            "enabled": model.enabled,
        },
        "policy": {
            "type": model.effect,
        },
        "object_selector": {
            "object_types": model.resource_types,
            "match": {
                "tag": {
                    "key": model.resource_tag_key,
                },
            },
        },
        "principal_selector": {
            "entitlement": model.entitlements,
            "match": {
                "scope": {
                    "from_tag_value": model.principal_scope_tag,
                },
            },
        },
        "actions": {
            "grant": {
                "privileges": model.privileges,
                "include_parents": model.include_parent_grants,
            },
        },
    }


def to_yaml(model: PolicyModel) -> str:
    """Render a PolicyModel as a YAML string."""
    return yaml.dump(
        to_dict(model),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
