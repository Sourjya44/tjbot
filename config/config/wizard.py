# Copyright 2026-present TJBot Contributors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Schema-driven hierarchical configuration editor for TJBot.

All editing is performed directly on the live tomlkit document so that
every comment, blank line, and ordering from the downloaded default TOML
is preserved on save.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import inquirer
import inquirer.errors
import tomlkit
from rich.console import Console

from config.device_detection import DeviceDetection, get_system_info
from config.model_registry import ModelRegistry
from config.schema_loader import ConfigSchemaError, TJBotConfigSchema, load_config_schema

console = Console()

DEFAULT_TOML_URL = (
    'https://raw.githubusercontent.com/tjbot-ce/tjbot-config'
    '/refs/heads/main/tjbot.default.toml'
)


# ── TOML document helpers ────────────────────────────────────────────────────

def _get_value(doc, path: str, default=None) -> Any:
    """Return the value at *path* (dot-separated) or *default* if absent."""
    keys = path.split('.')
    node = doc
    try:
        for key in keys:
            node = node[key]
        # Normalise tomlkit containers to plain Python for reliable comparisons
        if isinstance(node, list):
            return [v for v in node]
        return node
    except (KeyError, TypeError):
        return default


def _set_value(doc, path: str, value) -> None:
    """Set *value* at *path*, creating intermediate tomlkit tables as needed."""
    keys = path.split('.')
    node = doc
    for key in keys[:-1]:
        if key not in node:
            node[key] = tomlkit.table()
        node = node[key]
    node[keys[-1]] = value


# ── Display helpers ──────────────────────────────────────────────────────────

def _fmt_bool(v) -> str:
    if v is True:
        return 'true'
    if v is False:
        return 'false'
    return str(v)


def _fmt_current(value) -> str:
    if value is None:
        return '(not set)'
    if isinstance(value, bool):
        return _fmt_bool(value)
    if isinstance(value, list):
        return ', '.join(str(x) for x in value)
    if value == '':
        return '(empty)'
    return str(value)


# ── Editor ───────────────────────────────────────────────────────────────────

class TJBotConfigEditor:
    """Interactive hierarchical editor that operates on a tomlkit document."""

    LEGACY_SECTION_ORDER = ['log', 'hardware', 'listen', 'see', 'shine', 'speak', 'wave']

    def __init__(self, doc, schema: Optional[TJBotConfigSchema] = None):
        if schema is None:
            raise ConfigSchemaError('TJBot config schema is required to run the editor.')
        self.doc = doc
        self.schema = schema
        self.model_registry = ModelRegistry()
        self.system_info = get_system_info()
        self._modified = False

    # ── Public ──────────────────────────────────────────────────────────────

    def run(self) -> bool:
        """
        Show the top-level section menu and loop until Save or Exit.
        Returns True if the user chose to save.
        """
        console.print('\n[bold cyan]TJBot Configuration Editor[/bold cyan]')
        if self.schema is not None:
            console.print(f'[dim]Schema loaded from {self.schema.path}[/dim]')
        console.print('[dim]Arrow keys to navigate · Enter to select · Ctrl-C to cancel[/dim]\n')

        while True:
            choice = self._pick_section()
            if choice is None or choice == 'exit':
                if self._modified:
                    console.print('\n[yellow]Exited without saving. '
                                  'Run "tjbot config edit" to edit again.[/yellow]\n')
                return False
            if choice == 'save':
                return True
            self._edit_section(choice)

    # ── Navigation ──────────────────────────────────────────────────────────

    def _available_sections(self) -> List[Tuple[str, str]]:
        sections = self.schema.get_sections(self.LEGACY_SECTION_ORDER)
        description_by_key = {section.key: section.description for section in sections}
        choices: List[Tuple[str, str]] = []

        for key in self.LEGACY_SECTION_ORDER:
            if key not in description_by_key:
                continue
            description = description_by_key.get(key, key)
            choices.append((f'  {key:<8} - {description}', key))

        return choices

    def _pick_section(self) -> Optional[str]:
        status = '🟡' if self._modified else '🟢'
        choices = self._available_sections()
        choices.extend([
            (f'  💾 Save and exit {status}', 'save'),
            ('  ✖ Exit without saving', 'exit'),
        ])
        try:
            answers = inquirer.prompt(
                [inquirer.List('section', message='Select section to configure', choices=choices)],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return 'exit'
        if answers is None:
            return 'exit'
        return answers['section']

    def _edit_section(self, key: str):
        self._edit_schema_section(key)

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get(self, path: str, default=None) -> Any:
        return _get_value(self.doc, path, default)

    def _set(self, path: str, value) -> None:
        _set_value(self.doc, path, value)
        self._modified = True
        console.print(f'[green]  ✓ {path} = {_fmt_current(value)}[/green]')
        self._apply_path_side_effects(path, value)

    def _apply_path_side_effects(self, path: str, value) -> None:
        if path in ('shine.hasNeopixelLED', 'shine.hasCommonAnodeLED'):
            self._sync_led_flags()
            return

        if path == 'hardware.led' and value is False:
            _set_value(self.doc, 'shine.hasNeopixelLED', False)
            _set_value(self.doc, 'shine.hasCommonAnodeLED', False)
            console.print('[yellow]  Disabled LED hardware and cleared shine LED selections.[/yellow]')
        elif path == 'hardware.led' and value is True:
            console.print('[yellow]  Configure LED type and pins in the shine section.[/yellow]')

    def _sync_led_flags(self) -> None:
        """Keep aggregate hardware LED flag in sync with shine LED flags."""
        has_neopixel = bool(self._get('shine.hasNeopixelLED', False))
        has_common_anode = bool(self._get('shine.hasCommonAnodeLED', False))

        _set_value(self.doc, 'shine.hasNeopixelLED', has_neopixel)
        _set_value(self.doc, 'shine.hasCommonAnodeLED', has_common_anode)
        _set_value(self.doc, 'hardware.led', has_neopixel or has_common_anode)

    # ── Prompt primitives ────────────────────────────────────────────────────

    def _prompt_enum(self, name: str, message: str,
                     choices: List[Tuple[str, Any]], current) -> Optional[Any]:
        """Single-select list prompt."""
        values = [v for _, v in choices]
        default = current if current in values else (values[0] if values else None)
        try:
            answers = inquirer.prompt(
                [inquirer.List(
                    name,
                    message=f'{message}  [current: {_fmt_current(current)}]',
                    choices=choices,
                    default=default,
                )],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None
        return answers[name]

    def _prompt_bool(self, name: str, message: str, current) -> Optional[bool]:
        return self._prompt_enum(
            name, message,
            [('Yes (true)', True), ('No (false)', False)],
            bool(current) if current is not None else False,
        )

    def _prompt_string(self, name: str, message: str, current: str) -> Optional[str]:
        try:
            answers = inquirer.prompt(
                [inquirer.Text(name, message=message, default=str(current) if current else '')],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None
        return answers[name]

    def _prompt_float01(self, name: str, message: str, current) -> Optional[float]:
        def _validate(_, x):
            try:
                v = float(x)
                if not (0.0 <= v <= 1.0):
                    raise inquirer.errors.ValidationError(
                        '', reason='Value must be between 0.0 and 1.0.')
                return True
            except ValueError:
                raise inquirer.errors.ValidationError('', reason='Enter a decimal number.')
        try:
            answers = inquirer.prompt(
                [inquirer.Text(
                    name,
                    message=f'{message}  (0.0 - 1.0)  [current: {_fmt_current(current)}]',
                    default=str(current) if current is not None else '',
                    validate=_validate,
                )],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None
        return float(answers[name])

    def _prompt_number(self, name: str, message: str, current,
                       *, minimum=None, maximum=None, integral: bool = False):
        def _validate(_, x):
            try:
                value = int(x) if integral else float(x)
            except ValueError as exc:
                reason = 'Enter a whole number.' if integral else 'Enter a number.'
                raise inquirer.errors.ValidationError('', reason=reason) from exc

            if minimum is not None and value < minimum:
                raise inquirer.errors.ValidationError('', reason=f'Value must be >= {minimum}.')
            if maximum is not None and value > maximum:
                raise inquirer.errors.ValidationError('', reason=f'Value must be <= {maximum}.')
            return True

        try:
            answers = inquirer.prompt(
                [inquirer.Text(
                    name,
                    message=f'{message}  [current: {_fmt_current(current)}]',
                    default=str(current) if current is not None else '',
                    validate=_validate,
                )],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None
        return int(answers[name]) if integral else float(answers[name])

    def _prompt_array_pair(self, name: str, message: str, current) -> Optional[List[int]]:
        current_text = ''
        if isinstance(current, list) and len(current) == 2:
            current_text = f'{current[0]},{current[1]}'

        def _validate(_, x):
            parts = [part.strip() for part in x.split(',')]
            if len(parts) != 2:
                raise inquirer.errors.ValidationError('', reason='Enter two comma-separated integers.')
            try:
                int(parts[0])
                int(parts[1])
            except ValueError as exc:
                raise inquirer.errors.ValidationError('', reason='Enter two whole numbers.') from exc
            return True

        try:
            answers = inquirer.prompt(
                [inquirer.Text(
                    name,
                    message=f'{message}  [current: {_fmt_current(current)}]',
                    default=current_text,
                    validate=_validate,
                )],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None

        parts = [int(part.strip()) for part in answers[name].split(',')]
        return parts

    def _prompt_model_choice(self, path: str, label: str, current) -> Optional[str]:
        models = None

        if path == 'listen.backend.local.model':
            models = self.model_registry.get_stt_models()
        elif path == 'listen.backend.local.vad.model':
            models = self.model_registry.get_vad_models()
        elif path == 'speak.backend.local.model':
            models = self.model_registry.get_tts_models()
        elif path == 'see.backend.local.objectDetectionModel':
            models = self.model_registry.get_vision_models('object-detection')
        elif path == 'see.backend.local.imageClassificationModel':
            models = self.model_registry.get_vision_models('classification')
        elif path == 'see.backend.local.faceDetectionModel':
            models = self.model_registry.get_vision_models('face-detection')

        if not models:
            return None

        choices = [
            (self.model_registry.format_model_option(model), model['key'])
            for model in models
        ]
        return self._prompt_enum(path.replace('.', '_'), label, choices, current)

    def _schema_field_message(self, key: str, schema_node: Dict[str, Any]) -> str:
        description = schema_node.get('description')
        if description:
            return f'{key} - {description}'
        return key

    def _schema_property_value(self, path: str, schema_node: Dict[str, Any]) -> Any:
        return self._get(path, schema_node.get('default'))

    def _schema_field_summary(self, path: str, schema_node: Dict[str, Any]) -> str:
        if self._schema_is_object(schema_node):
            object_type = self._get(f'{path}.type')
            if object_type is not None:
                return str(object_type)
            return 'open'
        return _fmt_current(self._schema_property_value(path, schema_node))

    def _schema_is_object(self, schema_node: Dict[str, Any]) -> bool:
        return schema_node.get('type') == 'object' or 'properties' in schema_node

    def _schema_number_is_integral(self, schema_node: Dict[str, Any], current) -> bool:
        if schema_node.get('type') == 'integer':
            return True
        if schema_node.get('type') != 'number':
            return False

        candidates = [current, schema_node.get('default'), schema_node.get('minimum'), schema_node.get('maximum')]
        filtered = [value for value in candidates if value is not None]
        return bool(filtered) and all(isinstance(value, int) and not isinstance(value, bool) for value in filtered)

    def _edit_schema_section(self, key: str) -> None:
        section = self.schema.get_section(key)
        console.print(f'\n[bold]{key}[/bold] - {section.description}\n')
        self._edit_schema_object(key, key, section.schema)

    def _edit_schema_object(self, title: str, path_prefix: str, object_schema: Dict[str, Any]) -> None:
        properties = self.schema.get_object_properties(object_schema)
        if not properties:
            console.print('[yellow]No editable fields in this schema section.[/yellow]\n')
            return

        while True:
            label_width = max(len(prop.key) for prop in properties)
            items = [
                (
                    f'  {prop.key.ljust(label_width)}   [{self._schema_field_summary(f"{path_prefix}.{prop.key}", prop.schema)}]',
                    prop.key,
                )
                for prop in properties
            ]
            items.append(('← Back', '__back__'))

            try:
                answers = inquirer.prompt(
                    [inquirer.List(
                        'field',
                        message=f'{title} - select field to edit',
                        choices=items,
                    )],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break

            if answers is None or answers['field'] == '__back__':
                break

            prop = next((item for item in properties if item.key == answers['field']), None)
            if prop is None:
                continue

            full_path = f'{path_prefix}.{prop.key}'
            if self._schema_is_object(prop.schema):
                nested_title = f'{title}.{prop.key}'
                console.print(f'\n[bold]{nested_title}[/bold] - {prop.description}\n')
                self._edit_schema_object(nested_title, full_path, prop.schema)
                continue

            self._edit_schema_field(full_path, prop.key, prop.schema)

    def _edit_schema_field(self, path: str, key: str, schema_node: Dict[str, Any]) -> None:
        current = self._schema_property_value(path, schema_node)
        message = self._schema_field_message(key, schema_node)

        if path == 'listen.device':
            console.print('[dim]Detecting audio input devices...[/dim]')
            value = self._pick_audio_device('input')
        elif path == 'speak.device':
            console.print('[dim]Detecting audio output devices...[/dim]')
            value = self._pick_audio_device('output')
        else:
            value = self._prompt_model_choice(path, message, current)

        if value is not None:
            self._set(path, value)
            return

        if 'enum' in schema_node:
            choices = [(str(option), option) for option in schema_node['enum']]
            value = self._prompt_enum(path.replace('.', '_'), message, choices, current)
        elif schema_node.get('type') == 'boolean':
            value = self._prompt_bool(path.replace('.', '_'), message, current)
        elif schema_node.get('type') == 'string':
            value = self._prompt_string(path.replace('.', '_'), message, str(current) if current is not None else '')
        elif schema_node.get('type') in ('integer', 'number'):
            integral = self._schema_number_is_integral(schema_node, current)
            minimum = schema_node.get('minimum')
            maximum = schema_node.get('maximum')
            if not integral and minimum == 0 and maximum == 1:
                value = self._prompt_float01(path.replace('.', '_'), message, current)
            else:
                value = self._prompt_number(
                    path.replace('.', '_'),
                    message,
                    current,
                    minimum=minimum,
                    maximum=maximum,
                    integral=integral,
                )
        elif schema_node.get('type') == 'array' and schema_node.get('minItems') == 2 and schema_node.get('maxItems') == 2:
            value = self._prompt_array_pair(path.replace('.', '_'), message, current)
        else:
            console.print(f'[yellow]Unsupported schema field type for {path}.[/yellow]')
            return

        if value is not None:
            self._set(path, value)

    # ── Audio device picker ──────────────────────────────────────────────────

    def _pick_audio_device(self, direction: str) -> Optional[str]:
        """direction: 'input' for microphone, 'output' for speaker."""
        dd = DeviceDetection()
        if direction == 'input':
            devices = dd.detect_audio_input_devices()
            cmd_hint = 'arecord -l'
        else:
            devices = dd.detect_audio_output_devices()
            cmd_hint = 'aplay -l'

        if not devices:
            console.print(
                f'[yellow]  No hardware audio devices detected '
                f'(run `{cmd_hint}` to check).[/yellow]'
            )

        choices: List[Tuple[str, str]] = [
            (dd.format_device_for_display(d), d['id']) for d in devices
        ]
        choices.append(('  Enter device ID manually', '__manual__'))

        try:
            answers = inquirer.prompt(
                [inquirer.List('dev', message='Select audio device', choices=choices)],
                raise_keyboard_interrupt=True,
            )
        except KeyboardInterrupt:
            return None
        if answers is None:
            return None

        if answers['dev'] == '__manual__':
            import re as _re
            def _validate_device(_, x):
                if _re.match(r'^(plughw|hw):\d+,\d+$', x) or x in ('default', 'sysdefault', ''):
                    return True
                raise inquirer.errors.ValidationError(
                    '', reason='Use plughw:C,D format (e.g. plughw:2,0) or leave blank for auto.')
            try:
                m = inquirer.prompt(
                    [inquirer.Text(
                        'dev',
                        message='Enter device ID (e.g. plughw:2,0), or leave blank for auto',
                        default='',
                        validate=_validate_device,
                    )],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                return None
            return m['dev'] if m else None

        return answers['dev']

# ── Setup helpers ─────────────────────────────────────────────────────────

def download_default_config(config_dir: Path, config_path: Path) -> bool:
    """
    Fetch the canonical default TJBot TOML from GitHub and write it to *config_path*.
    Creates *config_dir* if necessary. Returns True on success.
    """
    import requests  # lazily imported so the module is importable without network

    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.chmod(0o755)

    console.print('[dim]Downloading default configuration from GitHub...[/dim]')
    try:
        resp = requests.get(DEFAULT_TOML_URL, timeout=15)
        resp.raise_for_status()
        config_path.write_text(resp.text, encoding='utf-8')
        config_path.chmod(0o644)
        console.print(f'[green]✓ Default configuration saved to {config_path}[/green]\n')
        return True
    except Exception as exc:
        console.print(f'[red]✗ Failed to download default config: {exc}[/red]')
        console.print(
            f'[yellow]  Check your internet connection or create {config_path} manually.[/yellow]\n')
        return False


def ensure_config_exists(config_dir: Path, config_path: Path) -> bool:
    """Return True if *config_path* already exists OR was successfully downloaded."""
    if config_path.exists():
        return True
    return download_default_config(config_dir, config_path)


# ── Editor entry point ────────────────────────────────────────────────────────

def run_editor(config_path: Path, schema: Optional[TJBotConfigSchema] = None) -> int:
    """
    Load *config_path* as a tomlkit document, run the interactive editor,
    and write back the mutated document on save — preserving all comments.
    Returns a shell exit code (0 = ok, 1 = error, 130 = cancelled).
    """
    from config.config_writer import ConfigWriter

    try:
        raw = config_path.read_text(encoding='utf-8')
        doc = tomlkit.parse(raw)
    except Exception as exc:
        console.print(f'[red]Error loading config: {exc}[/red]\n')
        return 1

    if schema is None:
        schema = load_config_schema(required=True)

    editor = TJBotConfigEditor(doc, schema=schema)
    want_save = editor.run()

    if not want_save:
        return 0

    writer = ConfigWriter()
    writer.create_backup(config_path)
    writer.cleanup_old_backups()

    try:
        config_path.write_text(tomlkit.dumps(doc), encoding='utf-8')
        config_path.chmod(0o644)
        console.print(f'\n[green]✓ Configuration saved to {config_path}[/green]\n')
        return 0
    except Exception as exc:
        console.print(f'[red]✗ Error saving configuration: {exc}[/red]\n')
        return 1

