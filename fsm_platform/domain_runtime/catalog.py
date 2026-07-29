"""Catalog Contract API из локальных реестров + manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fsm_platform.domain_runtime import registry


def load_manifest(package_dir: Path) -> dict[str, Any]:
    path = package_dir / "manifest.yaml"
    if not path.is_file():
        return {}
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _parse_simple_yaml(path.read_text(encoding="utf-8"))


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_list_key: Optional[str] = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list_key is None:
                continue
            item = line.split("-", 1)[1].strip().strip("\"'")
            result.setdefault(current_list_key, []).append(item)
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            current_list_key = key
            result[key] = []
            continue
        current_list_key = None
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        result[key] = value
    return result


def package_dir_from_entry(entry: str) -> Path:
    """domains.courier.processes:register_all → domains/courier."""
    module_name = entry.split(":", 1)[0].strip()
    parts = module_name.split(".")
    if len(parts) < 2:
        raise ValueError(f"cannot resolve package dir from entry={entry!r}")
    root = Path(__file__).resolve().parents[2]
    return root.joinpath(*parts[:2])


def build_catalog(service_id: str, *, entry: Optional[str] = None) -> dict[str, Any]:
    sid = str(service_id or "").strip()
    manifest: dict[str, Any] = {}
    if entry:
        try:
            manifest = load_manifest(package_dir_from_entry(entry))
        except Exception:
            manifest = {}

    procs = registry.processes.list_for_service(sid)
    context_builders: list[str] = []
    seen_cb: set[str] = set()
    process_items: list[dict[str, Any]] = []
    for p in procs:
        cb_name = p.context_builder_name
        if cb_name and cb_name not in seen_cb:
            seen_cb.add(cb_name)
            context_builders.append(cb_name)
        process_items.append(
            {
                "process_name": p.process_name,
                "entity_type": p.entity_type,
                "event_name": p.event_name or p.process_name,
                "initial_state": p.initial_state,
                "context_builder": cb_name,
                "on_failed": p.on_failed is not None,
            }
        )

    return {
        "cartridge_type": str(manifest.get("cartridge_type") or "domain"),
        "version": str(manifest.get("version") or "0.1.0"),
        "service_id": sid,
        "operations": registry.operations.list(sid),
        "processes": process_items,
        "guards": registry.guards.list_names(sid),
        "effects": registry.effects.list_names(sid),
        "context_builders": context_builders,
        "hooks": registry.hooks.list_channels(sid),
    }
