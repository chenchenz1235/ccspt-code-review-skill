# Sanitized feedback package

Generate YAML with these fields:

```yaml
skill_version:
finding_id:
rule_id:
language:
engineer_judgement: correct | false-positive | unclear
engineer_comment:
suggested_rule_change:
contains_source_code: false
approved_destination:
```

Remove source code, diffs, repository URLs, customer names, credentials, device identifiers, and logs unless the user explicitly authorizes each item and destination. Leave `approved_destination` empty until approval is given.
