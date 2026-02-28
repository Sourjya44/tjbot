# TJBot Configuration Tool

Interactive configuration management for TJBot - an open-source Do-It-Yourself robot powered by IBM Watson AI.

## Overview

`tj-config` is a command-line tool that helps you configure your TJBot hardware and cloud services through an intuitive interactive interface. It supports both beginner-friendly guided setup and advanced menu-driven configuration.

## Features

- 🎯 **Guided Setup**: Step-by-step wizard for first-time configuration
- 🔧 **Advanced Editor**: Menu-driven interface for fine-tuning settings
- 🔌 **Auto-Detection**: Automatic discovery of audio devices, camera, and Raspberry Pi model
- 🔑 **Credential Management**: Guided setup for IBM Cloud, Google Cloud, and Azure services
- ✅ **Validation**: Real-time validation of GPIO pins, credentials, and configuration
- 🧪 **Hardware Testing**: Built-in hardware test integration
- 📝 **TOML Preservation**: Maintains comments and formatting when editing configuration

## Installation

### Prerequisites

`tj-config` uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python dependency management.

**Install uv** (if not already installed):

```bash
# Recommended method (standalone installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Alternative (using pip)
pip3 install uv --user
```

After installing, restart your shell or run `source ~/.bashrc` (or `~/.zshrc`).

### Via Bootstrap

If you're setting up TJBot for the first time, `tj-config` is automatically configured by the bootstrap script:

```bash
cd ~/Desktop/tjbot/bootstrap
sudo ./bootstrap.sh
```

The bootstrap script will:
- Check for `uv` and provide installation instructions if needed
- Set up the Python environment with `uv sync`
- Offer to run the configuration wizard

### Manual Setup

To set up `tj-config` on an existing system:

```bash
cd ~/Desktop/tjbot/tj-config
uv sync
```

## Usage

### Initialize Configuration (Beginner Mode)

Run the guided setup wizard:

```bash
cd ~/Desktop/tjbot/tj-config
uv run tj-config init
```

Or use the convenience wrapper from anywhere:

```bash
~/Desktop/tjbot/tj-config-wrapper.sh init
```

This will walk you through:
- Hardware selection (LED, servo, camera, speaker, microphone)
- GPIO pin configuration with conflict detection
- Audio device selection
- Backend service configuration (local vs cloud)
- Credential setup for cloud services
- Model selection for local AI services

### Edit Configuration (Advanced Mode)

Open the menu-driven editor:

```bash
cd ~/Desktop/tjbot/tj-config
uv run tj-config edit
```

Navigate through menus to:
- Enable/disable hardware
- Change backend services
- Manage credentials
- Configure models
- Test hardware
- Edit raw TOML

### Other Commands

All commands should be run from the `tj-config` directory with `uv run`:

```bash
cd ~/Desktop/tjbot/tj-config

# Validate configuration and credentials
uv run tj-config validate

# Test specific hardware
uv run tj-config test speaker
uv run tj-config test microphone
uv run tj-config test led
uv run tj-config test all

# Show current configuration
uv run tj-config show

# Reset to defaults
uv run tj-config reset

# Backup configuration
uv run tj-config backup

# Version information
uv run tj-config --version
uv run tj-config --help
```

**Tip**: Create a shell alias for convenience:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias tj-config='cd ~/Desktop/tjbot/tj-config && uv run tj-config'

# Then use it anywhere:
tj-config init
tj-config validate
```

## Configuration File

The configuration is stored in `~/.tjbot/tjbot.toml` and follows the TOML format. This file overrides defaults from `node-tjbotlib` and can be edited manually or through `tj-config`.

Example structure:

```toml
[log]
level = 'info'

[hardware]
speaker = true
microphone = true
led_neopixel = true

[listen]
device = 'plughw:2,0'

[listen.backend]
type = 'local'

[listen.backend.local]
model = 'whisper-base'

[speak]
device = 'plughw:0,0'

[speak.backend]
type = 'local'

[speak.backend.local]
model = 'vits-piper-en_US-ryan-medium'

[shine.neopixel]
gpioPin = 21
```

## Cloud Service Setup

### IBM Cloud (Watson AI)

1. Create a free account at [IBM Cloud](https://cloud.ibm.com/registration)
2. Create service instances for:
   - Watson Speech to Text
   - Watson Text to Speech
   - Watson Assistant (optional)
3. Copy API keys and service URLs
4. `tj-config` will guide you through saving credentials to `~/.tjbot/ibm-credentials.env`

### Google Cloud Platform

1. Create account and project at [Google Cloud Console](https://console.cloud.google.com)
2. Enable billing (credit card required, but free tier available)
3. Enable APIs: Speech-to-Text, Text-to-Speech, Vision
4. Create service account and download JSON credentials
5. `tj-config` will help you save to `~/.tjbot/google-credentials.json`

### Microsoft Azure

1. Create account at [Azure Portal](https://portal.azure.com)
2. Create resource group
3. Create Cognitive Services for Speech and Vision
4. Copy keys and endpoints
5. `tj-config` will save to `~/.tjbot/azure-credentials.env`

## GPIO Pin Reference

### Raspberry Pi 3/4

- **NeoPixel LED**: GPIO 10, 12, 18, 21 (21 recommended)
- **Servo**: GPIO 12, 13, 18, 19 (18 recommended if not using audio)
- **Common Anode LED**: Any GPIO pins

### Raspberry Pi 5

- **NeoPixel LED**: GPIO 10 only (via SPI `/dev/spidev0.0`)
- **Servo**: GPIO 12, 13, 18, 19
- **Common Anode LED**: Any GPIO pins

**Note**: GPIO 18 conflicts with audio output. If using both speaker and NeoPixel, use GPIO 21.

## Troubleshooting

### Configuration file not found

Run `tj-config init` to create a new configuration.

### Credential validation fails

Check that:
- API keys are correctly copied
- Service URLs are correct
- Network connection is working
- Services are active in your cloud account

Run `tj-config validate` for detailed error messages.

### GPIO conflicts

`tj-config` automatically detects pin conflicts. Common issues:
- Using GPIO 18 for NeoPixel while audio is enabled
- Same pin assigned to multiple devices

### Audio devices not detected

Ensure USB audio devices are connected. Run:
```bash
aplay -L  # List output devices
arecord -L  # List input devices
```

You can manually specify device IDs in the format `plughw:X,Y`.

## Development

### Project Structure

```
tj-config/
├── tj-config                    # Main executable
├── pyproject.toml               # Project metadata and dependencies
├── README.md                    # This file
└── tjconfig/                    # Python package
    ├── __init__.py
    ├── cli.py                   # Command-line interface
    ├── wizard.py                # Init mode (beginner)
    ├── editor.py                # Edit mode (advanced)
    ├── config_loader.py         # TOML loading/merging
    ├── config_writer.py         # TOML writing with comments
    ├── validators.py            # GPIO, credential validation
    ├── device_detection.py      # Hardware auto-detection
    ├── model_registry.py        # Model registry integration
    ├── credential_guides/       # Cloud service wizards
    │   ├── __init__.py
    │   ├── ibm_cloud.py
    │   ├── google_cloud.py
    │   ├── azure.py
    │   └── validator.py
    └── templates/               # Configuration templates
        ├── ibm-credentials.env.template
        ├── google-credentials.json.template
        ├── azure-credentials.env.template
        └── tjbot.toml.template
```

### Development Setup

```bash
cd ~/Desktop/tjbot/tj-config

# Install dependencies
uv sync

# Run in development mode
uv run tj-config --help

# Add a new dependency
uv add package-name

# Update dependencies
uv sync --upgrade
```

### Why uv?

This project uses [uv](https://docs.astral.sh/uv/) for dependency management because:
- **Fast**: 10-100x faster than pip
- **Reliable**: Reproducible installs with lockfile
- **Modern**: Uses `pyproject.toml` standard
- **Isolated**: Each project has its own environment
- **No system pollution**: Doesn't require system-level Python packages

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## Resources

- [TJBot GitHub](https://github.com/ibmtjbot/tjbot)
- [TJBot Recipes](../recipes/)
- [node-tjbotlib Documentation](https://github.com/ibmtjbot/node-tjbotlib)
- [IBM Watson Services](https://www.ibm.com/watson)
