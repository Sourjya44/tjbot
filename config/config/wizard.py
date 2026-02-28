"""
Initialization wizard for TJBot configuration.

Guides users through hardware and service setup with interactive prompts.
"""

import inquirer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from config.config_writer import ConfigWriter
from config.config_loader import ConfigLoader
from config.device_detection import DeviceDetection, get_system_info
from config.validators import ConfigValidators
from config.model_registry import ModelRegistry
from config.credential_guides.ibm_cloud import run_ibm_wizard
from config.credential_guides.google_cloud import run_google_wizard
from config.credential_guides.azure import run_azure_wizard

console = Console()


class InitWizard:
    """Interactive initialization wizard for TJBot configuration."""

    def __init__(self):
        self.config = {}
        self.system_info = dict()
        self.config_dir = Path.home() / '.tjbot'
        self.config_file = self.config_dir / 'tjbot.toml'
        self.detector = DeviceDetection()
        self.validators = ConfigValidators()
        self.existing_config = None

    def run(self):
        """Run the complete initialization wizard."""
        console.print("\n[bold cyan]TJBot Configuration Wizard[/bold cyan]\n")

        # Check for existing configuration
        if self.config_file.exists():
            console.print("[yellow]Existing configuration found![/yellow]")
            console.print("Current settings will be used as defaults.\n")
            self._load_existing_config()
        else:
            console.print("This wizard will help you configure your TJBot hardware and services.")

        console.print("Press Ctrl+C at any time to cancel.\n")

        # Detect system
        console.print("[dim]Detecting your system...[/dim]")
        self.system_info = get_system_info()
        rpi_model = self.system_info['raspberry_pi']['model']
        console.print(f"[dim]✓ Detected Raspberry Pi {rpi_model}[/dim]\n")

        # Hardware selection
        self._configure_hardware()

        # Backend selection
        if self.config.get('hardware', {}).get('microphone'):
            self._configure_listen_backend()

        if self.config.get('hardware', {}).get('speaker'):
            self._configure_speak_backend()

        if self.config.get('hardware', {}).get('camera'):
            self._configure_see_backend()

        # Logging level
        self._configure_logging()

        # Write configuration
        if self._write_configuration():
            console.print("\n[bold green]✓ Configuration complete![/bold green]")
            console.print(f"[green]Configuration saved to: {self.config_dir / 'tjbot.toml'}[/green]\n")
            return True
        else:
            console.print("\n[red]✗ Failed to save configuration[/red]\n")
            return False

    def _load_existing_config(self):
        """Load existing configuration file."""
        try:
            loader = ConfigLoader()
            self.existing_config = loader.load_user_config()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load existing config: {e}[/yellow]")
            self.existing_config = None

    def _get_existing(self, path: str, default=None):
        """Get value from existing config using dot notation."""
        if not self.existing_config:
            return default

        keys = path.split('.')
        value = self.existing_config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def _configure_hardware(self):
        """Ask about hardware devices."""
        console.print("[bold]Hardware Setup[/bold]\n")

        hardware_choices = [
            ('Speaker (audio output)', 'speaker'),
            ('Microphone (audio input)', 'microphone'),
            ('LED (NeoPixel)', 'led_neopixel'),
            ('LED (Common Anode RGB)', 'led_common_anode'),
            ('Servo motor (arm)', 'servo'),
            ('Camera', 'camera'),
        ]

        # Build defaults from existing config or use reasonable defaults
        defaults = []
        if self._get_existing('hardware.speaker', False):
            defaults.append('speaker')
        if self._get_existing('hardware.microphone', False):
            defaults.append('microphone')
        if self._get_existing('hardware.led_neopixel', False):
            defaults.append('led_neopixel')
        if self._get_existing('hardware.led_common_anode', False):
            defaults.append('led_common_anode')
        if self._get_existing('hardware.servo', False):
            defaults.append('servo')
        if self._get_existing('hardware.camera', False):
            defaults.append('camera')

        # If no existing config, use reasonable defaults
        if not defaults:
            defaults = ['speaker', 'microphone', 'led_neopixel', 'servo', 'camera']

        questions = [
            inquirer.Checkbox(
                'hardware',
                message='Select the hardware you want to enable (press space to select, enter to confirm)',
                choices=hardware_choices,
                default=defaults
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        # Initialize hardware config
        self.config['hardware'] = {
            'speaker': 'speaker' in answers['hardware'],
            'microphone': 'microphone' in answers['hardware'],
            'led_neopixel': 'led_neopixel' in answers['hardware'],
            'led_common_anode': 'led_common_anode' in answers['hardware'],
            'servo': 'servo' in answers['hardware'],
            'camera': 'camera' in answers['hardware'],
        }

        # Configure GPIO for LEDs
        if self.config['hardware']['led_neopixel']:
            self._configure_neopixel()

        if self.config['hardware']['led_common_anode']:
            self._configure_common_anode()

        # Configure servo
        if self.config['hardware']['servo']:
            self._configure_servo()

        # Configure audio devices
        if self.config['hardware']['speaker']:
            self._configure_speaker()

        if self.config['hardware']['microphone']:
            self._configure_microphone()

        # Configure camera
        if self.config['hardware']['camera']:
            self._configure_camera()

        console.print()

    def _configure_neopixel(self):
        """Configure NeoPixel LED GPIO pin."""
        rpi_model = self.system_info['raspberry_pi']['model']
        recommended_pin = self.system_info['recommended_led_pin']

        if rpi_model == '5':
            valid_pins = [10]
            console.print("[yellow]Note: Raspberry Pi 5 only supports GPIO 10 for NeoPixel[/yellow]")
            pin = 10
        else:
            valid_pins = [10, 12, 18, 21]
            existing_pin = self._get_existing('shine.neopixel.gpioPin', recommended_pin)
            questions = [
                inquirer.List(
                    'neopixel_pin',
                    message='Select GPIO pin for NeoPixel LED',
                    choices=[
                        (f'GPIO {recommended_pin} (recommended)', recommended_pin),
                        *[(f'GPIO {p}', p) for p in valid_pins if p != recommended_pin]
                    ],
                    default=existing_pin
                )
            ]
            answers = inquirer.prompt(questions)
            if not answers:
                return
            pin = answers['neopixel_pin']

        self.config.setdefault('shine', {}).setdefault('neopixel', {})['gpioPin'] = pin

        if pin == 18:
            console.print("[yellow]⚠ Warning: GPIO 18 may conflict with audio output[/yellow]")

    def _configure_common_anode(self):
        """Configure common anode RGB LED pins."""
        questions = [
            inquirer.Text('red_pin', message='GPIO pin for RED channel',
                         default=str(self._get_existing('shine.commonanode.redPin', 19))),
            inquirer.Text('green_pin', message='GPIO pin for GREEN channel',
                         default=str(self._get_existing('shine.commonanode.greenPin', 13))),
            inquirer.Text('blue_pin', message='GPIO pin for BLUE channel',
                         default=str(self._get_existing('shine.commonanode.bluePin', 12))),
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config.setdefault('shine', {}).setdefault('commonanode', {})['redPin'] = int(answers['red_pin'])
        self.config['shine']['commonanode']['greenPin'] = int(answers['green_pin'])
        self.config['shine']['commonanode']['bluePin'] = int(answers['blue_pin'])

    def _configure_servo(self):
        """Configure servo GPIO pin."""
        existing_servo_pin = self._get_existing('wave.servoPin', 18)
        questions = [
            inquirer.List(
                'servo_pin',
                message='Select GPIO pin for servo motor',
                choices=[
                    ('GPIO 18 (recommended)', 18),
                    ('GPIO 12', 12),
                    ('GPIO 13', 13),
                    ('GPIO 19', 19),
                ],
                default=existing_servo_pin
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config.setdefault('wave', {})['servoPin'] = answers['servo_pin']

    def _configure_speaker(self):
        """Configure speaker audio device."""
        output_devices = self.system_info['audio_output']

        existing_device = self._get_existing('speak.device', '')

        if not output_devices:
            console.print("[yellow]No audio output devices detected. Using default.[/yellow]")
            self.config['speak'] = {'device': existing_device}
            return

        # Create choices from detected devices
        choices = [(self.detector.format_device_for_display(dev), dev['id'])
                   for dev in output_devices[:5]]  # Limit to first 5
        choices.append(('Manual entry', 'manual'))

        # Try to find existing device in choices, otherwise use first choice
        default_choice = choices[0][1]
        for label, device_id in choices:
            if device_id == existing_device:
                default_choice = device_id
                break

        questions = [
            inquirer.List(
                'speaker_device',
                message='Select audio output device for speaker',
                choices=choices,
                default=default_choice
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        if answers['speaker_device'] == 'manual':
            manual_q = [inquirer.Text('device', message='Enter device ID (e.g., plughw:0,0)')]
            manual_a = inquirer.prompt(manual_q)
            device = manual_a['device'] if manual_a else ''
        else:
            device = answers['speaker_device']

        self.config['speak'] = {'device': device}

    def _configure_microphone(self):
        """Configure microphone audio device."""
        input_devices = self.system_info['audio_input']

        existing_device = self._get_existing('listen.device', '')

        if not input_devices:
            console.print("[yellow]No audio input devices detected. Using default.[/yellow]")
            self.config['listen'] = {'device': existing_device, 'microphoneRate': 44100, 'microphoneChannels': 2}
            return

        # Create choices from detected devices
        choices = [(self.detector.format_device_for_display(dev), dev['id'])
                   for dev in input_devices[:5]]
        choices.append(('Manual entry', 'manual'))

        # Try to find existing device in choices, otherwise use first choice
        default_choice = choices[0][1]
        for label, device_id in choices:
            if device_id == existing_device:
                default_choice = device_id
                break

        questions = [
            inquirer.List(
                'mic_device',
                message='Select audio input device for microphone',
                choices=choices,
                default=default_choice
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        if answers['mic_device'] == 'manual':
            manual_q = [inquirer.Text('device', message='Enter device ID (e.g., plughw:2,0)')]
            manual_a = inquirer.prompt(manual_q)
            device = manual_a['device'] if manual_a else ''
        else:
            device = answers['mic_device']

        self.config.setdefault('listen', {})['device'] = device
        self.config['listen']['microphoneRate'] = 44100
        self.config['listen']['microphoneChannels'] = 2

    def _configure_camera(self):
        """Configure camera settings."""
        existing_resolution = self._get_existing('see.cameraResolution', [1920, 1080])
        questions = [
            inquirer.List(
                'resolution',
                message='Select camera resolution',
                choices=[
                    ('1920x1080 (Full HD)', [1920, 1080]),
                    ('1280x720 (HD)', [1280, 720]),
                    ('640x480 (VGA)', [640, 480]),
                ],
                default=existing_resolution
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config['see'] = {
            'cameraResolution': answers['resolution'],
            'verticalFlip': False,
            'horizontalFlip': False
        }

    def _configure_listen_backend(self):
        """Configure speech-to-text backend."""
        console.print("\n[bold]Speech-to-Text Backend[/bold]\n")

        existing_backend = self._get_existing('listen.backend.type', 'local')
        questions = [
            inquirer.List(
                'backend',
                message='Choose speech-to-text backend',
                choices=[
                    ('Local (offline, free, private)', 'local'),
                    ('IBM Watson (cloud, accurate)', 'ibm-watson-stt'),
                    ('Google Cloud (cloud, requires billing)', 'google-cloud-stt'),
                    ('Microsoft Azure (cloud, requires billing)', 'azure-stt'),
                ],
                default=existing_backend
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config.setdefault('listen', {}).setdefault('backend', {})['type'] = answers['backend']

        if answers['backend'] == 'local':
            self._configure_local_stt()
        elif answers['backend'] == 'ibm-watson-stt':
            console.print("\n[cyan]IBM Watson credentials will be configured...[/cyan]")
            run_ibm_wizard(self.config_dir, ['speech-to-text'])
        elif answers['backend'] == 'google-cloud-stt':
            console.print("\n[cyan]Google Cloud credentials will be configured...[/cyan]")
            run_google_wizard(self.config_dir)
        elif answers['backend'] == 'azure-stt':
            console.print("\n[cyan]Azure credentials will be configured...[/cyan]")
            run_azure_wizard(self.config_dir, ['speech'])

        console.print()

    def _configure_local_stt(self):
        """Configure local STT model."""
        registry = ModelRegistry()
        models = registry.get_stt_models()

        choices = [(registry.format_model_option(m), m['key']) for m in models]
        existing_model = self._get_existing('listen.backend.local.model', models[0]['key'] if models else None)

        questions = [
            inquirer.List(
                'model',
                message='Select speech recognition model',
                choices=choices,
                default=existing_model
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config['listen']['backend']['local'] = {'model': answers['model']}
        self.config['listen']['backend']['local']['vad'] = {'enabled': True, 'model': 'silero-vad'}

    def _configure_speak_backend(self):
        """Configure text-to-speech backend."""
        console.print("\n[bold]Text-to-Speech Backend[/bold]\n")

        existing_backend = self._get_existing('speak.backend.type', 'local')
        questions = [
            inquirer.List(
                'backend',
                message='Choose text-to-speech backend',
                choices=[
                    ('Local (offline, free, private)', 'local'),
                    ('IBM Watson (cloud, natural)', 'ibm-watson-tts'),
                    ('Google Cloud (cloud, requires billing)', 'google-cloud-tts'),
                    ('Microsoft Azure (cloud, requires billing)', 'azure-tts'),
                ],
                default=existing_backend
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config.setdefault('speak', {}).setdefault('backend', {})['type'] = answers['backend']

        if answers['backend'] == 'local':
            self._configure_local_tts()
        elif answers['backend'] == 'ibm-watson-tts':
            console.print("\n[cyan]IBM Watson credentials will be configured...[/cyan]")
            run_ibm_wizard(self.config_dir, ['text-to-speech'])
        elif answers['backend'] == 'google-cloud-tts':
            if 'google-credentials.json' not in [f.name for f in self.config_dir.glob('*')]:
                console.print("\n[cyan]Google Cloud credentials will be configured...[/cyan]")
                run_google_wizard(self.config_dir)
        elif answers['backend'] == 'azure-tts':
            if 'azure-credentials.env' not in [f.name for f in self.config_dir.glob('*')]:
                console.print("\n[cyan]Azure credentials will be configured...[/cyan]")
                run_azure_wizard(self.config_dir, ['speech'])

        console.print()

    def _configure_local_tts(self):
        """Configure local TTS model."""
        registry = ModelRegistry()
        models = registry.get_tts_models()

        choices = [(registry.format_model_option(m), m['key']) for m in models]
        existing_model = self._get_existing('speak.backend.local.model', models[0]['key'] if models else None)

        questions = [
            inquirer.List(
                'model',
                message='Select voice model',
                choices=choices,
                default=existing_model
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config['speak']['backend']['local'] = {'model': answers['model']}

    def _configure_see_backend(self):
        """Configure computer vision backend."""
        console.print("\n[bold]Computer Vision Backend[/bold]\n")

        existing_backend = self._get_existing('see.backend.type', 'local')
        questions = [
            inquirer.List(
                'backend',
                message='Choose computer vision backend',
                choices=[
                    ('Local (offline, free, private)', 'local'),
                    ('Google Cloud (cloud, requires billing)', 'google-cloud-vision'),
                    ('Microsoft Azure (cloud, requires billing)', 'azure-vision'),
                ],
                default=existing_backend
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config.setdefault('see', {}).setdefault('backend', {})['type'] = answers['backend']

        if answers['backend'] == 'local':
            self.config['see']['backend']['local'] = {
                'objectDetectionModel': 'ssd-mobilenet-v2',
                'imageClassificationModel': 'mobilenetv3',
                'faceDetectionModel': 'scrfd-2.5g',
                'objectDetectionConfidence': 0.8,
                'imageClassificationConfidence': 0.8,
                'faceDetectionConfidence': 0.5,
            }
        elif answers['backend'] == 'google-cloud-vision':
            if 'google-credentials.json' not in [f.name for f in self.config_dir.glob('*')]:
                console.print("\n[cyan]Google Cloud credentials will be configured...[/cyan]")
                run_google_wizard(self.config_dir)
        elif answers['backend'] == 'azure-vision':
            if 'azure-credentials.env' not in [f.name for f in self.config_dir.glob('*')]:
                console.print("\n[cyan]Azure credentials will be configured...[/cyan]")
                run_azure_wizard(self.config_dir, ['vision'])

        console.print()

    def _configure_logging(self):
        """Configure logging level."""
        existing_log_level = self._get_existing('log.level', 'info')
        questions = [
            inquirer.List(
                'log_level',
                message='Select logging verbosity',
                choices=[
                    ('Info (recommended)', 'info'),
                    ('Verbose (detailed)', 'verbose'),
                    ('Debug (everything)', 'debug'),
                    ('Error (quiet)', 'error'),
                ],
                default=existing_log_level
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return

        self.config['log'] = {'level': answers['log_level']}

    def _write_configuration(self):
        """Write configuration to file."""
        writer = ConfigWriter()
        return writer.write_config(self.config, add_comments=True, create_backup=False)


def run_init_wizard():
    """Run the initialization wizard."""
    wizard = InitWizard()
    return wizard.run()
