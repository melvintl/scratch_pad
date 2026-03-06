"""Transform a natural-language textX parse tree into the canonical PolicyModel."""

from policy_dsl.model import PolicyModel


def transform(parsed) -> PolicyModel:
    """Convert a textX parsed NL model into a PolicyModel."""
    model = PolicyModel()

    model.id = parsed.id.value

    if parsed.description:
        model.description = parsed.description.value.value.strip()

    if parsed.enabled:
        model.enabled = parsed.enabled.value == "true"

    # Effect line carries both effect and resource types
    model.effect = parsed.effect.effect
    model.resource_types = list(parsed.effect.types)

    if parsed.taggedWith:
        model.resource_tag_key = parsed.taggedWith.tag

    if parsed.forPrincipals:
        model.entitlements = [qs.value for qs in parsed.forPrincipals.entitlements]

    if parsed.scopedTo:
        model.principal_scope_tag = parsed.scopedTo.tag

    if parsed.granting:
        model.privileges = list(parsed.granting.privileges)

    if parsed.includeParents:
        model.include_parent_grants = True

    return model
