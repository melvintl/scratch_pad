# Prompt for a POC: BDD-Style Policy DSL with textX

I want to build a proof of concept in Python for a custom policy DSL using textX.

## Context

I am designing a custom ABAC/PBAC-like policy framework for Databricks / Unity Catalog style access control. The business domain is clinical trial data access. The goal is to author policies in a human-readable BDD-style DSL, then parse that DSL into a structured internal model, and from that model generate an underlying YAML representation.

This is a POC, so keep the design pragmatic, simple, and easy to extend.

## What I want

1. Design a small BDD-style DSL for policy authoring.
2. Use textX in Python to define and parse the DSL.
3. Convert the parsed DSL into a canonical Python object model.
4. Generate YAML output from that model.
5. Keep the implementation easy to understand and suitable for extension later into SQL / Databricks grants / row filters / masks.

## Important design intent

- The BDD-style DSL is for human authoring and review.
- The YAML is the underlying machine-friendly representation.
- The BDD syntax should be constrained and deterministic, not free-form English.
- The DSL should be readable by business stakeholders, governance stakeholders, and engineers.
- The DSL should map closely to the underlying policy concepts:
  - metadata
  - policy type / effect
  - object selector
  - principal selector
  - match conditions
  - actions

## Domain concepts

- Principal: the requesting user / group / service principal
- Resource: table or view
- Entitlement: business role such as Clinical Data Programmer
- Scope: study-level access
- Tag: STUDYID tag on a table or view
- Action / privilege: SELECT
- Policy effect: allow

## Target YAML shape

Use this as the target output structure:

```yaml
version: 1.0.0
metadata:
  id: trial_team_access_by_studyid
  description: >
    Grants select access to users assigned to a clinical trial in CTMS.
    The trial is determined by tagging STUDYID on the table.
  enabled: true

policy:
  type: allow

object_selector:
  object_types:
    - table
    - view
  match:
    tag:
      key: STUDYID

principal_selector:
  entitlement:
    - "Clinical Data Programmer"
    - "Clinical Trial Data Manager"
  match:
    scope:
      from_tag_value: STUDYID

actions:
  grant:
    privileges:
      - SELECT
    include_parents: true
```

## BDD-style DSL idea

I want the user-facing DSL to look something like this:

```gherkin
Feature: Study-scoped trial team access

  Scenario: Trial team can select study-tagged tables and views
    As a clinical data programmer
    I want to read tables and views tagged with STUDYID
    So that I can access only data for studies assigned to me

    Given policy id is "trial_team_access_by_studyid"
    And policy description is """
      Grants select access to users assigned to a clinical trial in CTMS.
      The trial is determined by tagging STUDYID on the table.
    """
    And policy is enabled
    And effect is allow
    And resource type is one of:
      | table |
      | view  |
    And resource has tag "STUDYID"
    And principal entitlement is one of:
      | Clinical Data Programmer      |
      | Clinical Trial Data Manager   |
    And principal scope matches resource tag "STUDYID"
    When requested privilege is "SELECT"
    Then allow access
    And include parent grants is true
```

## Important modeling guidance

- Treat "As a / I want / So that" as descriptive narrative metadata, not executable logic.
- The executable logic should come from controlled Given / When / Then clause patterns.
- Define only a small set of allowed clause patterns for the POC.
- The parser should be strict enough that the DSL is deterministic.
- The internal canonical model should be simple and explicit.

## What I want you to produce

1. A recommended project structure for the POC.
2. A textX grammar for the DSL.
3. Python code to parse the DSL into a model.
4. Python code to transform the parsed model into the target YAML structure.
5. A sample input DSL file.
6. The generated YAML output.
7. Explanations of key design choices.
8. Suggestions for how this could later be extended to support:
   - more entitlements
   - multiple privileges
   - additional tags
   - multiple resource types
   - richer boolean conditions
   - SQL generation for Databricks enforcement

## Implementation preferences

- Keep the code concise and readable.
- Prefer a POC-quality implementation, not an enterprise-heavy design.
- Use standard Python libraries where possible.
- It is fine to use PyYAML for YAML output.
- Do not over-engineer validation initially.
- Focus on proving the concept end-to-end.

## Expected response format

Please provide the solution as:
- a clear explanation
- complete Python code
- the textX grammar
- example DSL input
- generated YAML output
- and a short note on limitations of this first POC
