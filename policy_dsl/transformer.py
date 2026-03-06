"""Transform a textX parse tree into the canonical PolicyModel."""

from policy_dsl.model import PolicyModel


def _clause_body(clause):
    """Extract the body from a Given/And/When/Then clause."""
    return clause.body


def _strip_table_item(item) -> str:
    """Strip whitespace from a table item value."""
    return item.value.strip()


def transform(parsed) -> PolicyModel:
    """Convert a textX parsed model into a PolicyModel."""
    model = PolicyModel()

    # Narrative metadata
    model.feature_title = parsed.featureTitle.strip()
    model.scenario_title = parsed.scenarioTitle.strip()
    model.role = parsed.narrative.role.strip()
    model.desire = parsed.narrative.desire.strip()
    model.benefit = parsed.narrative.benefit.strip()

    # Walk clauses
    for clause in parsed.clauses:
        body = _clause_body(clause)
        cls_name = body.__class__.__name__

        if cls_name == "PolicyIdClause":
            model.id = body.value.value

        elif cls_name == "PolicyDescriptionClause":
            # Normalize multi-line description: collapse inner whitespace
            lines = body.value.value.strip().splitlines()
            model.description = "\n".join(line.strip() for line in lines)

        elif cls_name == "PolicyEnabledClause":
            model.enabled = body.value == "enabled"

        elif cls_name == "EffectClause":
            model.effect = body.value

        elif cls_name == "ResourceTypeClause":
            model.resource_types = [_strip_table_item(i) for i in body.items]

        elif cls_name == "ResourceTagClause":
            model.resource_tag_key = body.value.value

        elif cls_name == "PrincipalEntitlementClause":
            model.entitlements = [_strip_table_item(i) for i in body.items]

        elif cls_name == "PrincipalScopeClause":
            model.principal_scope_tag = body.value.value

        elif cls_name == "PrivilegeClause":
            model.privileges.append(body.value.value)

        elif cls_name == "AllowAccessClause":
            pass  # Effect already captured; this is the Then assertion

        elif cls_name == "IncludeParentGrantsClause":
            model.include_parent_grants = body.value == "true"

    return model
