"""Helpers for loading the TJBot configuration schema.

The schema is maintained in the external tjbot-config repository and vendored
into this repository as a git submodule at vendor/tjbot-config.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

SCHEMA_ENV_VAR = 'TJBOT_CONFIG_SCHEMA_PATH'
SCHEMA_REPO_DIRNAME = 'tjbot-config'
SCHEMA_FILENAME = 'tjbot-config.schema.yaml'


class ConfigSchemaError(RuntimeError):
    """Raised when the TJBot config schema cannot be loaded or parsed."""


@dataclass(frozen=True)
class SchemaSection:
    """Resolved top-level section metadata used by the editor UI."""

    key: str
    description: str
    schema: Dict[str, Any]


@dataclass(frozen=True)
class SchemaProperty:
    """Resolved property metadata for an object schema."""

    key: str
    description: str
    schema: Dict[str, Any]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_schema_path() -> Path:
    """Return the expected submodule-backed schema path."""
    return _repo_root() / 'vendor' / SCHEMA_REPO_DIRNAME / SCHEMA_FILENAME


def resolve_schema_path(explicit_path: Optional[Path] = None) -> Path:
    """Resolve the schema path from an explicit path, env var, or default."""
    if explicit_path is not None:
        return Path(explicit_path).expanduser().resolve()

    env_path = os.environ.get(SCHEMA_ENV_VAR)
    if env_path:
        return Path(env_path).expanduser().resolve()

    return default_schema_path().resolve()


class TJBotConfigSchema:
    """Lightweight wrapper around the TJBot JSON Schema document."""

    def __init__(self, path: Path, raw_schema: Dict[str, Any]):
        self.path = path
        self.raw_schema = raw_schema
        self.definitions = raw_schema.get('definitions', {})

    def get_sections(self, allowed_keys: Optional[Iterable[str]] = None) -> List[SchemaSection]:
        """Return resolved top-level sections in schema declaration order."""
        allowed = set(allowed_keys) if allowed_keys is not None else None
        properties = self.raw_schema.get('properties', {})
        sections: List[SchemaSection] = []

        for key, value in properties.items():
            if allowed is not None and key not in allowed:
                continue
            resolved = self.resolve_node(value)
            if not isinstance(resolved, dict):
                continue
            description = str(resolved.get('description') or value.get('description') or key)
            sections.append(SchemaSection(key=key, description=description, schema=resolved))

        return sections

    def get_section(self, key: str) -> SchemaSection:
        """Return one resolved top-level section by key."""
        properties = self.raw_schema.get('properties', {})
        if key not in properties:
            raise ConfigSchemaError(f'Missing top-level schema section: {key}')

        raw_section = properties[key]
        resolved = self.resolve_node(raw_section)
        if not isinstance(resolved, dict):
            raise ConfigSchemaError(f'Invalid schema section payload: {key}')

        description = str(resolved.get('description') or raw_section.get('description') or key)
        return SchemaSection(key=key, description=description, schema=resolved)

    def get_object_properties(self, node: Dict[str, Any]) -> List[SchemaProperty]:
        """Return resolved properties for an object schema in declaration order."""
        resolved_node = self.resolve_node(node)
        properties = resolved_node.get('properties', {}) if isinstance(resolved_node, dict) else {}

        items: List[SchemaProperty] = []
        for key, value in properties.items():
            resolved_value = self.resolve_node(value)
            if not isinstance(resolved_value, dict):
                continue
            description = str(resolved_value.get('description') or value.get('description') or key)
            items.append(SchemaProperty(key=key, description=description, schema=resolved_value))

        return items

    def resolve_node(self, node: Any) -> Any:
        """Resolve local definition references in a schema node."""
        if not isinstance(node, dict):
            return node

        ref = node.get('$ref')
        if ref:
            return self._resolve_ref(ref)

        return node

    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        if not ref.startswith('#/definitions/'):
            raise ConfigSchemaError(f'Unsupported schema reference: {ref}')

        key = ref.split('/', 2)[-1]
        if key not in self.definitions:
            raise ConfigSchemaError(f'Missing schema definition: {key}')

        target = self.definitions[key]
        if not isinstance(target, dict):
            raise ConfigSchemaError(f'Invalid schema definition payload for: {key}')

        return target


def load_config_schema(
    schema_path: Optional[Path] = None,
    *,
    required: bool = False,
) -> Optional[TJBotConfigSchema]:
    """Load the external TJBot configuration schema if available."""
    resolved_path = resolve_schema_path(schema_path)

    if not resolved_path.exists():
        if required:
            raise ConfigSchemaError(
                'TJBot config schema not found at '
                f'{resolved_path}. Initialize the schema submodule with '
                '"git submodule update --init --recursive" or set '
                f'{SCHEMA_ENV_VAR}.'
            )
        return None

    try:
        raw = yaml.safe_load(resolved_path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise ConfigSchemaError(
            f'Failed to load TJBot config schema from {resolved_path}: {exc}'
        ) from exc

    if not isinstance(raw, dict) or raw.get('type') != 'object':
        raise ConfigSchemaError(
            f'Invalid TJBot config schema at {resolved_path}: expected a top-level object schema.'
        )

    properties = raw.get('properties')
    if not isinstance(properties, dict) or not properties:
        raise ConfigSchemaError(
            f'Invalid TJBot config schema at {resolved_path}: missing top-level properties.'
        )

    return TJBotConfigSchema(resolved_path, raw)
