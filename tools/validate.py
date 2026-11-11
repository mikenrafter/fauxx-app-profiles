#!/usr/bin/env python3
"""Check app behavior profiles against the draft rules.

Stdlib only, so it runs anywhere without installing a JSON Schema library.
It enforces the structural rules in schema/profile.schema.json that matter for
safety (no unknown fields, ranges ordered, domains bare) plus rules a schema
cannot express (invasive apps publish host kinds only; real profiles need a
real signer). Exit status 0 means every file passed.

Usage: python3 tools/validate.py [FILE ...]   (default: every profiles/**/*.json)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schema" / "profile.schema.json").read_text())


def check(node, schema, path, errors):
    if "$ref" in schema:
        schema = SCHEMA["$defs"][schema["$ref"].rsplit("/", 1)[-1]]
    if "const" in schema and node != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} is not one of {schema['enum']}")
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(node, dict):
            errors.append(f"{path}: must be an object")
            return
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in node:
                errors.append(f"{path}: missing {key}")
        for key, value in node.items():
            if key not in props:
                errors.append(f"{path}: unknown field {key!r} (data only; unknown fields are rejected)")
            else:
                check(value, props[key], f"{path}.{key}", errors)
        if set(props) == {"min", "max"} and {"min", "max"} <= set(node) and node["min"] > node["max"]:
            errors.append(f"{path}: min is greater than max")
    elif kind == "array":
        if not isinstance(node, list):
            errors.append(f"{path}: must be an array")
            return
        if len(node) < schema.get("minItems", 0) or len(node) > schema.get("maxItems", 10**9):
            errors.append(f"{path}: has {len(node)} items, outside the allowed range")
        for index, item in enumerate(node):
            check(item, schema["items"], f"{path}[{index}]", errors)
    elif kind == "string":
        if not isinstance(node, str):
            errors.append(f"{path}: must be a string")
        else:
            if "pattern" in schema and not re.fullmatch(schema["pattern"], node):
                errors.append(f"{path}: {node!r} does not match {schema['pattern']}")
            if len(node) > schema.get("maxLength", 10**9):
                errors.append(f"{path}: too long")
    elif kind == "number":
        if isinstance(node, bool) or not isinstance(node, (int, float)):
            errors.append(f"{path}: must be a number")
        elif node < schema.get("minimum", float("-inf")):
            errors.append(f"{path}: below minimum")
    elif kind == "boolean" and not isinstance(node, bool):
        errors.append(f"{path}: must be true or false")


def policy(profile, errors):
    app = profile.get("app", {})
    provenance = profile.get("provenance", {})
    if app.get("invasiveness") == "high" and any(
        "domain" in host for phase in profile.get("phases", []) for host in phase.get("hosts", [])
    ):
        errors.append("high-invasiveness profiles publish host kinds only; remove every domain")
    synthetic = provenance.get("synthetic")
    if synthetic is False and set(provenance.get("signer_sha256", "")) == {"0"}:
        errors.append("a real profile needs the app's real signer fingerprint")
    if synthetic is False and provenance.get("method") == "synthetic-example":
        errors.append("method synthetic-example requires synthetic: true")


def main(argv):
    files = [Path(a) for a in argv] or sorted((ROOT / "profiles").rglob("*.json"))
    failed = 0
    for file in files:
        errors = []
        try:
            profile = json.loads(file.read_text())
        except (OSError, ValueError) as error:
            errors.append(f"cannot read: {error.__class__.__name__}")
        else:
            check(profile, SCHEMA, "$", errors)
            policy(profile, errors)
        status = "ok" if not errors else "FAIL"
        print(f"{status}  {file}")
        for line in errors:
            print(f"      {line}")
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
