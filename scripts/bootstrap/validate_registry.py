#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_manifest_shape(manifest: dict) -> None:
    required_top = {"registry_version", "generated_at", "default_pack", "agents", "packs", "items"}
    missing = sorted(required_top - set(manifest))
    if missing:
        fail(f"manifest missing keys: {', '.join(missing)}")

    if not isinstance(manifest["agents"], dict):
        fail("manifest agents must be an object keyed by agent id")

    allowed_support_levels = {"A", "B", "C"}
    for agent_id, agent_meta in manifest["agents"].items():
        if not isinstance(agent_meta, dict):
            fail(f"agent {agent_id} metadata must be an object")
        level = agent_meta.get("support_level")
        if level not in allowed_support_levels:
            fail(f"agent {agent_id} has invalid support_level: {level}")


def validate_manifest_references(manifest: dict) -> None:
    item_ids = set()
    item_paths = set()
    pack_ids = set()
    pack_paths = set()

    for item in manifest["items"]:
        item_id = f'{item["type"]}:{item["id"]}'
        item_ids.add(item_id)
        item_paths.add(item["path"].rstrip("/"))
        item_path = ROOT / item["path"]

        if not item_path.exists():
            fail(f"missing path: {item['path']}")
        if "source" not in item:
            fail(f"item missing source: {item_id}")
        if "policy" not in item:
            fail(f"item missing policy: {item_id}")
        if item.get("checksum") == "TBD" and item["type"] not in {"reference", "addon", "skill", "script", "wrapper"}:
            fail(f"unsupported checksum placeholder item type: {item_id}")

        if item["type"] == "skill":
            if not (item_path / "SKILL.md").exists():
                fail(f"missing SKILL.md for {item['id']}")
        elif item["type"] in {"script", "wrapper"}:
            if not (item_path / "tool.yaml").exists():
                fail(f"missing tool.yaml for {item['id']}")
        elif item["type"] == "addon":
            if not (item_path / "addon.yaml").exists():
                fail(f"missing addon.yaml for {item['id']}")
        elif item["type"] == "reference":
            if not (item_path / "reference.yaml").exists():
                fail(f"missing reference.yaml for {item['id']}")

    for pack in manifest["packs"]:
        pack_ids.add(pack["id"])
        pack_paths.add(pack["path"])
        pack_path = ROOT / pack["path"]
        if not pack_path.exists():
            fail(f"missing pack file: {pack['path']}")
        pack_data = load_json(pack_path)
        if pack["items"] != pack_data["items"]:
            fail(f"pack items drift: {pack['id']}")
        for ref in pack_data["items"]:
            if ref not in item_ids:
                fail(f"pack {pack['id']} references unknown item {ref}")

    if manifest["default_pack"] not in pack_ids:
        fail(f"default_pack {manifest['default_pack']} not found in manifest packs")

    for pack_file in (ROOT / "packs").glob("*.json"):
        relpath = pack_file.relative_to(ROOT).as_posix()
        if relpath not in pack_paths:
            fail(f"pack file not indexed in manifest: {relpath}")

    resource_dirs = {
        "skills": ("skill", "SKILL.md"),
        "scripts": ("script", "tool.yaml"),
        "wrappers": ("wrapper", "tool.yaml"),
        "addons": ("addon", "addon.yaml"),
        "references": ("reference", "reference.yaml"),
    }
    for directory, (resource_type, marker) in resource_dirs.items():
        for resource_dir in (ROOT / directory).iterdir():
            if not resource_dir.is_dir():
                continue
            marker_path = resource_dir / marker
            if not marker_path.exists():
                continue
            resource_id = f"{resource_type}:{resource_dir.name}"
            resource_relpath = resource_dir.relative_to(ROOT).as_posix()
            if resource_id not in item_ids:
                fail(f"resource not indexed in manifest: {resource_id}")
            if resource_relpath not in item_paths:
                fail(f"resource path not indexed in manifest: {resource_relpath}")

    for adapter in (ROOT / "adapters").glob("*/adapter.yaml"):
        if not adapter.exists():
            fail(f"missing adapter file: {adapter}")


def compare_manifest_to_resource_files(manifest: dict) -> None:
    for item in manifest["items"]:
        item_path = ROOT / item["path"]
        item_id = f'{item["type"]}:{item["id"]}'

        if item["type"] == "addon":
            addon = load_yaml(item_path / "addon.yaml")
            for field in ("description", "source", "install", "policy"):
                if item.get(field) != addon.get(field):
                    fail(f"{item_id} drift in {field}")
            support_agents = sorted(item.get("support", {}).keys())
            canonical_agents = sorted(addon.get("agents", []))
            if support_agents != canonical_agents:
                fail(f"{item_id} drift in support agents")
        elif item["type"] == "reference":
            ref = load_yaml(item_path / "reference.yaml")
            for field in ("description", "source", "policy"):
                if item.get(field) != ref.get(field):
                    fail(f"{item_id} drift in {field}")
            support_agents = sorted(item.get("support", {}).keys())
            canonical_agents = sorted(ref.get("agents", []))
            if support_agents != canonical_agents:
                fail(f"{item_id} drift in support agents")
        elif item["type"] in {"script", "wrapper"}:
            tool = load_yaml(item_path / "tool.yaml")
            field_map = {"description": "description", "entry": "entry", "requires": "requires"}
            for manifest_field, tool_field in field_map.items():
                if item.get(manifest_field) != tool.get(tool_field):
                    fail(f"{item_id} drift in {manifest_field}")


def validate_support_levels(manifest: dict) -> None:
    adapter_levels = {}
    for adapter_path in (ROOT / "adapters").glob("*/adapter.yaml"):
        adapter = load_yaml(adapter_path)
        adapter_levels[adapter["agent_id"]] = adapter["support_level"]

    for agent_id, meta in manifest["agents"].items():
        adapter_level = adapter_levels.get(agent_id)
        if adapter_level is None:
            fail(f"manifest agent {agent_id} has no adapter")
        if adapter_level != meta["support_level"]:
            fail(f"support level drift for {agent_id}: manifest={meta['support_level']} adapter={adapter_level}")


def validate_placeholders(manifest: dict) -> None:
    for item in manifest["items"]:
        if item["type"] not in {"script", "wrapper"}:
            continue
        run_path = ROOT / item["path"] / item["entry"]
        if not run_path.exists():
            fail(f"missing runtime entry for {item['type']}:{item['id']}: {item['entry']}")
        run_text = run_path.read_text(encoding="utf-8")
        is_placeholder = "placeholder" in run_text.lower() or "TODO:" in run_text
        if is_placeholder and item["policy"]["action_on_missing"] == "install":
            fail(
                f"{item['type']}:{item['id']} is placeholder-backed but still marked installable"
            )


def main() -> int:
    manifest = load_json(ROOT / "manifest.json")
    validate_manifest_shape(manifest)
    validate_manifest_references(manifest)
    compare_manifest_to_resource_files(manifest)
    validate_support_levels(manifest)
    validate_placeholders(manifest)
    print("registry validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
