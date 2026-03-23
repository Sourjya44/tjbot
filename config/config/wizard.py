"""
Schema-driven hierarchical configuration editor for TJBot.

All editing is performed directly on the live tomlkit document so that
every comment, blank line, and ordering from the downloaded default TOML
is preserved on save.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import inquirer
import inquirer.errors
import tomlkit
from rich.console import Console

from config.device_detection import DeviceDetection, get_system_info

console = Console()

DEFAULT_TOML_URL = (
    'https://raw.githubusercontent.com/tjbot-ce/node-tjbotlib'
    '/refs/heads/main/src/config/tjbot.default.toml'
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

    def __init__(self, doc):
        self.doc = doc
        self.system_info = get_system_info()
        self._modified = False

    # ── Public ──────────────────────────────────────────────────────────────

    def run(self) -> bool:
        """
        Show the top-level section menu and loop until Save or Exit.
        Returns True if the user chose to save.
        """
        console.print('\n[bold cyan]TJBot Configuration Editor[/bold cyan]')
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

    def _pick_section(self) -> Optional[str]:
        dirty = ' [yellow]●[/yellow]' if self._modified else ''
        choices: List[Tuple[str, str]] = [
            ('  log      – Logging', 'log'),
            ('  hardware – Hardware components', 'hardware'),
            ('  listen   – Microphone + Speech-to-Text', 'listen'),
            ('  see      – Camera + Vision', 'see'),
            ('  shine    – LED', 'shine'),
            ('  speak    – Speaker + Text-to-Speech', 'speak'),
            ('  wave     – Servo', 'wave'),
            (f'  💾 Save and exit{dirty}', 'save'),
            ('  ✖ Exit without saving', 'exit'),
        ]
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
        dispatch = {
            'log': self._edit_log,
            'hardware': self._edit_hardware,
            'listen': self._edit_listen,
            'see': self._edit_see,
            'shine': self._edit_shine,
            'speak': self._edit_speak,
            'wave': self._edit_wave,
        }
        fn = dispatch.get(key)
        if fn:
            fn()

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get(self, path: str, default=None) -> Any:
        return _get_value(self.doc, path, default)

    def _set(self, path: str, value) -> None:
        _set_value(self.doc, path, value)
        self._modified = True
        console.print(f'[green]  ✓ {path} = {_fmt_current(value)}[/green]')

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

    def _prompt_int(self, name: str, message: str, current) -> Optional[int]:
        def _validate(_, x):
            try:
                int(x)
                return True
            except ValueError:
                raise inquirer.errors.ValidationError('', reason='Enter a whole number.')
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
        return int(answers[name])

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
                    message=f'{message}  (0.0 – 1.0)  [current: {_fmt_current(current)}]',
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

    # ── Generic fields menu ──────────────────────────────────────────────────

    def _edit_fields_menu(self, title: str,
                          fields: List[Tuple[str, str, str]]) -> None:
        """
        Present a looping menu for a list of (path, label, type_str) field entries.
        type_str: 'string' | 'integer' | 'float01' | 'boolean' | 'enum_servo'
        """
        while True:
            items = [
                (f'  {label}   [{_fmt_current(self._get(path))}]', path)
                for path, label, _ in fields
            ]
            items.append(('← Back', '__back__'))
            try:
                answers = inquirer.prompt(
                    [inquirer.List(
                        'field',
                        message=f'{title} – select field to edit',
                        choices=items,
                    )],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['field'] == '__back__':
                break
            sel = answers['field']
            entry = next((e for e in fields if e[0] == sel), None)
            if entry is None:
                break
            path, label, type_str = entry
            current = self._get(path)

            if type_str == 'boolean':
                val = self._prompt_bool(path.replace('.', '_'), label, current)
                if val is not None:
                    self._set(path, val)
            elif type_str == 'string':
                val = self._prompt_string(path.replace('.', '_'), label,
                                          str(current) if current is not None else '')
                if val is not None:
                    self._set(path, val)
            elif type_str == 'integer':
                val = self._prompt_int(path.replace('.', '_'), label, current)
                if val is not None:
                    self._set(path, val)
            elif type_str == 'float01':
                val = self._prompt_float01(path.replace('.', '_'), label, current)
                if val is not None:
                    self._set(path, val)
            elif type_str == 'enum_servo':
                val = self._prompt_enum('servo_pin', label, [
                    ('GPIO 18 – recommended PWM pin', 18),
                    ('GPIO 12 – PWM, no audio conflict', 12),
                    ('GPIO 13 – PWM', 13),
                    ('GPIO 19 – PWM', 19),
                ], current)
                if val is not None:
                    self._set(path, val)

    # ── Section editors ──────────────────────────────────────────────────────

    def _edit_log(self):
        console.print('\n[bold]log – Logging[/bold]\n')
        current = self._get('log.level', 'info')
        val = self._prompt_enum('level', 'Log level', [
            ('info    – normal operation (recommended)', 'info'),
            ('error   – errors only (quiet)', 'error'),
            ('warning – reduced verbosity', 'warning'),
            ('verbose – detailed operation logs', 'verbose'),
            ('debug   – everything (very noisy)', 'debug'),
        ], current)
        if val is not None:
            self._set('log.level', val)

    def _edit_hardware(self):
        console.print('\n[bold]hardware – Hardware components[/bold]\n')
        console.print('[dim]Select a device to toggle it on/off.[/dim]\n')
        fields = [
            ('hardware.speaker',          'Speaker     (audio output)'),
            ('hardware.microphone',       'Microphone  (audio input)'),
            ('hardware.led_neopixel',     'NeoPixel LED (addressable RGB)'),
            ('hardware.led_common_anode', 'Common Anode RGB LED'),
            ('hardware.servo',            'Servo motor (arm)'),
            ('hardware.camera',           'Camera module'),
        ]
        while True:
            choices = [
                (f'  {label}   [{_fmt_bool(self._get(path, False))}]', path)
                for path, label in fields
            ]
            choices.append(('← Back', '__back__'))
            try:
                answers = inquirer.prompt(
                    [inquirer.List('field', message='Toggle hardware device', choices=choices)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['field'] == '__back__':
                break
            path = answers['field']
            self._set(path, not bool(self._get(path, False)))

    def _edit_listen(self):
        if not self._get('hardware.microphone', False):
            console.print(
                '[yellow]  ⚠  hardware.microphone is disabled. '
                'Enable it in the hardware section or listen will be '
                'ignored at runtime.[/yellow]\n')
        while True:
            console.print('\n[bold]listen – Microphone + Speech-to-Text[/bold]\n')
            items = [
                (f'  device             [{_fmt_current(self._get("listen.device", ""))}]',
                 'device'),
                (f'  microphoneRate     [{_fmt_current(self._get("listen.microphoneRate", 44100))} Hz]',
                 'rate'),
                (f'  microphoneChannels [{_fmt_current(self._get("listen.microphoneChannels", 2))}]',
                 'channels'),
                (f'  backend.type       [{_fmt_current(self._get("listen.backend.type", "local"))}]',
                 'backend_type'),
                ('  backend settings   (expand for current backend type)', 'backend_settings'),
                ('← Back', '__back__'),
            ]
            try:
                answers = inquirer.prompt(
                    [inquirer.List('item', message='listen configuration', choices=items)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['item'] == '__back__':
                break
            item = answers['item']

            if item == 'device':
                console.print('[dim]Detecting audio input devices...[/dim]')
                val = self._pick_audio_device('input')
                if val is not None:
                    self._set('listen.device', val)

            elif item == 'rate':
                val = self._prompt_enum('rate', 'Microphone sample rate', [
                    ('16000 Hz – recommended for offline speech models', 16000),
                    ('44100 Hz – standard quality', 44100),
                    ('48000 Hz – high quality', 48000),
                    (' 8000 Hz – low bandwidth', 8000),
                ], self._get('listen.microphoneRate', 44100))
                if val is not None:
                    self._set('listen.microphoneRate', val)

            elif item == 'channels':
                val = self._prompt_enum('channels', 'Microphone channels', [
                    ('1 – mono (typical for microphones)', 1),
                    ('2 – stereo', 2),
                ], self._get('listen.microphoneChannels', 2))
                if val is not None:
                    self._set('listen.microphoneChannels', val)

            elif item == 'backend_type':
                val = self._prompt_enum('type', 'STT backend', [
                    ('none             – disable speech-to-text', 'none'),
                    ('local            – on-device Sherpa-ONNX (offline)', 'local'),
                    ('ibm-watson-stt   – IBM Cloud STT (streaming)', 'ibm-watson-stt'),
                    ('google-cloud-stt – Google Cloud STT (streaming)', 'google-cloud-stt'),
                    ('azure-stt        – Microsoft Azure STT', 'azure-stt'),
                ], self._get('listen.backend.type', 'local'))
                if val is not None:
                    self._set('listen.backend.type', val)

            elif item == 'backend_settings':
                self._edit_stt_backend_settings()

    def _edit_stt_backend_settings(self):
        backend_type = self._get('listen.backend.type', 'local')
        console.print(
            f'\n[bold]STT backend settings[/bold]  [dim](type: {backend_type})[/dim]\n')

        if backend_type == 'none':
            console.print('[yellow]  No settings for backend type "none".[/yellow]\n')
            return

        prefix = f'listen.backend.{backend_type}'
        if backend_type == 'local':
            fields = [
                (f'{prefix}.model',       'Model name',     'string'),
                (f'{prefix}.vad.enabled', 'VAD enabled',    'boolean'),
                (f'{prefix}.vad.model',   'VAD model name', 'string'),
            ]
        elif backend_type == 'ibm-watson-stt':
            fields = [
                (f'{prefix}.model',                      'Model name',                      'string'),
                (f'{prefix}.inactivityTimeout',          'Inactivity timeout (s, -1=off)',  'integer'),
                (f'{prefix}.backgroundAudioSuppression', 'Background audio suppression',    'float01'),
                (f'{prefix}.interimResults',             'Interim results',                 'boolean'),
                (f'{prefix}.credentialsPath',            'Credentials file path',           'string'),
            ]
        elif backend_type == 'google-cloud-stt':
            fields = [
                (f'{prefix}.credentialsPath',            'Credentials file path',           'string'),
                (f'{prefix}.model',                      'Model name',                      'string'),
                (f'{prefix}.languageCode',               'Language code (e.g. en-US)',       'string'),
                (f'{prefix}.enableAutomaticPunctuation', 'Automatic punctuation',           'boolean'),
                (f'{prefix}.profanityFilter',            'Profanity filter',                'boolean'),
                (f'{prefix}.interimResults',             'Interim results',                 'boolean'),
            ]
        elif backend_type == 'azure-stt':
            fields = [
                (f'{prefix}.language',       'Language (e.g. en-US)',  'string'),
                (f'{prefix}.credentialsPath', 'Credentials file path', 'string'),
                (f'{prefix}.interimResults',  'Interim results',       'boolean'),
            ]
        else:
            console.print(f'[yellow]  Unknown backend type: {backend_type}[/yellow]\n')
            return

        self._edit_fields_menu(f'STT backend ({backend_type})', fields)

    def _edit_speak(self):
        if not self._get('hardware.speaker', False):
            console.print(
                '[yellow]  ⚠  hardware.speaker is disabled. '
                'Enable it in the hardware section or speak will be '
                'ignored at runtime.[/yellow]\n')
        while True:
            console.print('\n[bold]speak – Speaker + Text-to-Speech[/bold]\n')
            items = [
                (f'  device          [{_fmt_current(self._get("speak.device", ""))}]',
                 'device'),
                (f'  backend.type    [{_fmt_current(self._get("speak.backend.type", "local"))}]',
                 'backend_type'),
                ('  backend settings (expand for current backend type)', 'backend_settings'),
                ('← Back', '__back__'),
            ]
            try:
                answers = inquirer.prompt(
                    [inquirer.List('item', message='speak configuration', choices=items)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['item'] == '__back__':
                break
            item = answers['item']

            if item == 'device':
                console.print('[dim]Detecting audio output devices...[/dim]')
                val = self._pick_audio_device('output')
                if val is not None:
                    self._set('speak.device', val)

            elif item == 'backend_type':
                val = self._prompt_enum('type', 'TTS backend', [
                    ('none             – disable text-to-speech', 'none'),
                    ('local            – on-device Sherpa-ONNX (offline)', 'local'),
                    ('ibm-watson-tts   – IBM Cloud TTS', 'ibm-watson-tts'),
                    ('google-cloud-tts – Google Cloud TTS', 'google-cloud-tts'),
                    ('azure-tts        – Microsoft Azure TTS', 'azure-tts'),
                ], self._get('speak.backend.type', 'local'))
                if val is not None:
                    self._set('speak.backend.type', val)

            elif item == 'backend_settings':
                self._edit_tts_backend_settings()

    def _edit_tts_backend_settings(self):
        backend_type = self._get('speak.backend.type', 'local')
        console.print(
            f'\n[bold]TTS backend settings[/bold]  [dim](type: {backend_type})[/dim]\n')

        if backend_type == 'none':
            console.print('[yellow]  No settings for backend type "none".[/yellow]\n')
            return

        prefix = f'speak.backend.{backend_type}'
        if backend_type == 'local':
            fields = [(f'{prefix}.model', 'Model name', 'string')]
        elif backend_type == 'ibm-watson-tts':
            fields = [
                (f'{prefix}.credentialsPath', 'Credentials file path',             'string'),
                (f'{prefix}.voice',           'Voice (e.g. en-US_MichaelV3Voice)', 'string'),
            ]
        elif backend_type == 'google-cloud-tts':
            fields = [
                (f'{prefix}.credentialsPath', 'Credentials file path',  'string'),
                (f'{prefix}.languageCode',    'Language code (e.g. en-US)', 'string'),
                (f'{prefix}.voice',           'Voice name',            'string'),
            ]
        elif backend_type == 'azure-tts':
            fields = [
                (f'{prefix}.credentialsPath', 'Credentials file path', 'string'),
                (f'{prefix}.voice',           'Voice name',            'string'),
            ]
        else:
            console.print(f'[yellow]  Unknown backend type: {backend_type}[/yellow]\n')
            return

        self._edit_fields_menu(f'TTS backend ({backend_type})', fields)

    def _edit_see(self):
        if not self._get('hardware.camera', False):
            console.print(
                '[yellow]  ⚠  hardware.camera is disabled. '
                'Enable it in the hardware section or see will be '
                'ignored at runtime.[/yellow]\n')
        while True:
            console.print('\n[bold]see – Camera + Vision[/bold]\n')
            res = self._get('see.cameraResolution', [1920, 1080])
            items = [
                (f'  cameraResolution   [{_fmt_current(res)}]', 'resolution'),
                (f'  verticalFlip       [{_fmt_bool(self._get("see.verticalFlip", False))}]',
                 'vflip'),
                (f'  horizontalFlip     [{_fmt_bool(self._get("see.horizontalFlip", False))}]',
                 'hflip'),
                (f'  backend.type       [{_fmt_current(self._get("see.backend.type", "local"))}]',
                 'backend_type'),
                ('  backend settings   (expand for current backend type)', 'backend_settings'),
                ('← Back', '__back__'),
            ]
            try:
                answers = inquirer.prompt(
                    [inquirer.List('item', message='see configuration', choices=items)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['item'] == '__back__':
                break
            item = answers['item']

            if item == 'resolution':
                val = self._prompt_enum('res', 'Camera resolution', [
                    ('1920 × 1080  Full HD', [1920, 1080]),
                    ('1280 ×  720  HD',      [1280, 720]),
                    (' 640 ×  480  VGA',     [640, 480]),
                    (' 320 ×  240  Low bandwidth', [320, 240]),
                ], res)
                if val is not None:
                    self._set('see.cameraResolution', val)

            elif item == 'vflip':
                val = self._prompt_bool(
                    'vflip', 'Flip camera image vertically',
                    self._get('see.verticalFlip', False))
                if val is not None:
                    self._set('see.verticalFlip', val)

            elif item == 'hflip':
                val = self._prompt_bool(
                    'hflip', 'Flip camera image horizontally',
                    self._get('see.horizontalFlip', False))
                if val is not None:
                    self._set('see.horizontalFlip', val)

            elif item == 'backend_type':
                val = self._prompt_enum('type', 'Vision backend', [
                    ('none                – disable vision', 'none'),
                    ('local               – on-device (offline)', 'local'),
                    ('google-cloud-vision – Google Cloud Vision', 'google-cloud-vision'),
                    ('azure-vision        – Microsoft Azure Vision', 'azure-vision'),
                ], self._get('see.backend.type', 'local'))
                if val is not None:
                    self._set('see.backend.type', val)

            elif item == 'backend_settings':
                self._edit_vision_backend_settings()

    def _edit_vision_backend_settings(self):
        backend_type = self._get('see.backend.type', 'local')
        console.print(
            f'\n[bold]Vision backend settings[/bold]  [dim](type: {backend_type})[/dim]\n')

        if backend_type == 'none':
            console.print('[yellow]  No settings for backend type "none".[/yellow]\n')
            return

        prefix = f'see.backend.{backend_type}'
        if backend_type == 'local':
            fields = [
                (f'{prefix}.objectDetectionModel',          'Object detection model',          'string'),
                (f'{prefix}.imageClassificationModel',      'Image classification model',      'string'),
                (f'{prefix}.faceDetectionModel',            'Face detection model',            'string'),
                (f'{prefix}.objectDetectionConfidence',     'Object detection confidence',     'float01'),
                (f'{prefix}.imageClassificationConfidence', 'Image classification confidence', 'float01'),
                (f'{prefix}.faceDetectionConfidence',       'Face detection confidence',       'float01'),
            ]
        elif backend_type in ('google-cloud-vision', 'azure-vision'):
            fields = [(f'{prefix}.credentialsPath', 'Credentials file path', 'string')]
        else:
            console.print(f'[yellow]  Unknown backend type: {backend_type}[/yellow]\n')
            return

        self._edit_fields_menu(f'Vision backend ({backend_type})', fields)

    def _edit_shine(self):
        while True:
            console.print('\n[bold]shine – LED[/bold]\n')
            items = [
                ('  NeoPixel LED settings',        'neopixel'),
                ('  Common Anode RGB LED settings', 'commonanode'),
                ('← Back', '__back__'),
            ]
            try:
                answers = inquirer.prompt(
                    [inquirer.List('item', message='shine configuration', choices=items)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['item'] == '__back__':
                break
            if answers['item'] == 'neopixel':
                self._edit_neopixel()
            elif answers['item'] == 'commonanode':
                self._edit_commonanode()

    def _edit_neopixel(self):
        rpi_model = self.system_info['raspberry_pi']['model']
        if not self._get('hardware.led_neopixel', False):
            console.print(
                '[yellow]  ⚠  hardware.led_neopixel is disabled. '
                'Enable it in the hardware section or NeoPixel will be '
                'ignored at runtime.[/yellow]\n')
        while True:
            console.print('\n[bold]shine.neopixel – NeoPixel LED[/bold]\n')
            if rpi_model == '5':
                items = [
                    (f'  spiInterface   [{_fmt_current(self._get("shine.neopixel.spiInterface", "/dev/spidev0.0"))}]',
                     'spi'),
                    (f'  useGRBFormat   [{_fmt_bool(self._get("shine.neopixel.useGRBFormat", False))}]',
                     'grb'),
                    ('← Back', '__back__'),
                ]
            else:
                items = [
                    (f'  gpioPin        [{_fmt_current(self._get("shine.neopixel.gpioPin", 21))}]',
                     'pin'),
                    (f'  useGRBFormat   [{_fmt_bool(self._get("shine.neopixel.useGRBFormat", False))}]',
                     'grb'),
                    ('← Back', '__back__'),
                ]
            try:
                answers = inquirer.prompt(
                    [inquirer.List('item', message='NeoPixel settings', choices=items)],
                    raise_keyboard_interrupt=True,
                )
            except KeyboardInterrupt:
                break
            if answers is None or answers['item'] == '__back__':
                break

            if answers['item'] == 'pin':
                val = self._prompt_enum('pin', 'GPIO pin for NeoPixel (RPi 3/4)', [
                    ('GPIO 21 – recommended (no audio/servo conflicts)', 21),
                    ('GPIO 10 – works on all models (SPI MOSI)',         10),
                    ('GPIO 12 – PWM, may conflict with servo',           12),
                    ('GPIO 18 – conflicts with audio output',            18),
                ], self._get('shine.neopixel.gpioPin', 21))
                if val is not None:
                    if val == 18:
                        console.print(
                            '[yellow]  ⚠  GPIO 18 conflicts with audio output. '
                            'Use GPIO 21 to avoid issues.[/yellow]')
                    self._set('shine.neopixel.gpioPin', val)

            elif answers['item'] == 'spi':
                val = self._prompt_enum('spi', 'SPI interface for NeoPixel (RPi 5)', [
                    ('/dev/spidev0.0 – primary SPI bus (GPIO 10, recommended)', '/dev/spidev0.0'),
                    ('/dev/spidev0.1 – secondary SPI bus', '/dev/spidev0.1'),
                ], self._get('shine.neopixel.spiInterface', '/dev/spidev0.0'))
                if val is not None:
                    self._set('shine.neopixel.spiInterface', val)

            elif answers['item'] == 'grb':
                val = self._prompt_bool(
                    'grb',
                    'Use GRB color format (enable if colors appear swapped)',
                    self._get('shine.neopixel.useGRBFormat', False))
                if val is not None:
                    self._set('shine.neopixel.useGRBFormat', val)

    def _edit_commonanode(self):
        if not self._get('hardware.led_common_anode', False):
            console.print(
                '[yellow]  ⚠  hardware.led_common_anode is disabled. '
                'Enable it in the hardware section or the common anode LED will be '
                'ignored at runtime.[/yellow]\n')
        console.print('\n[bold]shine.commonanode – Common Anode RGB LED[/bold]\n')
        self._edit_fields_menu('Common Anode LED', [
            ('shine.commonanode.redPin',   'Red channel GPIO pin',   'integer'),
            ('shine.commonanode.greenPin', 'Green channel GPIO pin', 'integer'),
            ('shine.commonanode.bluePin',  'Blue channel GPIO pin',  'integer'),
        ])

    def _edit_wave(self):
        if not self._get('hardware.servo', False):
            console.print(
                '[yellow]  ⚠  hardware.servo is disabled. '
                'Enable it in the hardware section or wave will be '
                'ignored at runtime.[/yellow]\n')
        console.print('\n[bold]wave – Servo[/bold]\n')
        self._edit_fields_menu('Wave (Servo)', [
            ('wave.servoPin', 'Servo GPIO pin', 'enum_servo'),
        ])


# ── Bootstrap helpers ─────────────────────────────────────────────────────────

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

def run_editor(config_path: Path) -> int:
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

    editor = TJBotConfigEditor(doc)
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

