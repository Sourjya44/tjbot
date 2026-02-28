"""
Configuration file writing for TJBot.

Handles writing TOML configuration files with comments and formatting preservation.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import tomlkit
from tomlkit import TOMLDocument, document, comment, nl


class ConfigWriter:
    """Write TJBot configuration files with comments."""

    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / '.tjbot'
        self.user_config_path = self.config_dir / 'tjbot.toml'

    def create_config_directory(self) -> bool:
        """
        Create ~/.tjbot directory if it doesn't exist.

        Returns:
            True if created or already exists, False on error
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Set appropriate permissions (755)
            self.config_dir.chmod(0o755)
            return True
        except Exception as e:
            print(f"Error creating config directory: {e}")
            return False

    def create_backup(self, path: Optional[Path] = None) -> Optional[Path]:
        """
        Create a timestamped backup of configuration file.

        Args:
            path: Path to file to backup (default: user config)

        Returns:
            Path to backup file or None on error
        """
        if path is None:
            path = self.user_config_path

        if not path.exists():
            return None

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = path.parent / f"{path.stem}.backup.{timestamp}{path.suffix}"
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    def cleanup_old_backups(self, keep: int = 5):
        """
        Remove old backup files, keeping only the most recent.

        Args:
            keep: Number of backups to keep
        """
        try:
            # Find all backup files
            backup_pattern = f"{self.user_config_path.stem}.backup.*{self.user_config_path.suffix}"
            backups = sorted(
                self.config_dir.glob(backup_pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Delete old backups
            for backup in backups[keep:]:
                backup.unlink()

        except Exception as e:
            print(f"Error cleaning up backups: {e}")

    def add_comments_to_config(self, config: Dict[str, Any]) -> TOMLDocument:
        """
        Add helpful comments to configuration document.

        Args:
            config: Configuration dictionary

        Returns:
            TOMLDocument with comments added
        """
        doc = document()

        # Add file header comment
        doc.add(comment("TJBot Configuration File"))
        doc.add(comment(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
        doc.add(comment(""))
        doc.add(comment("This file overrides TJBot's default configuration."))
        doc.add(comment("Edit with 'config edit' or manually."))
        doc.add(nl())

        # Log section
        if 'log' in config:
            doc.add(comment("Logging Configuration"))
            doc.add(comment("level: error | warning | info | verbose | debug"))
            doc['log'] = config['log']
            doc.add(nl())

        # Hardware section
        if 'hardware' in config:
            doc.add(comment("Hardware Capabilities"))
            doc.add(comment("Enable hardware components that are physically connected"))
            doc['hardware'] = config['hardware']
            doc.add(nl())

        # Listen (STT) section
        if 'listen' in config:
            doc.add(comment("Speech-to-Text Configuration"))
            doc.add(comment("device: Audio input device (e.g., 'plughw:2,0')"))
            doc.add(comment("backend.type: local | ibm-watson-stt | google-cloud-stt | azure-stt"))
            doc['listen'] = config['listen']
            doc.add(nl())

        # Speak (TTS) section
        if 'speak' in config:
            doc.add(comment("Text-to-Speech Configuration"))
            doc.add(comment("device: Audio output device (e.g., 'plughw:0,0')"))
            doc.add(comment("backend.type: local | ibm-watson-tts | google-cloud-tts | azure-tts"))
            doc['speak'] = config['speak']
            doc.add(nl())

        # See (Vision) section
        if 'see' in config:
            doc.add(comment("Computer Vision Configuration"))
            doc.add(comment("cameraResolution: [width, height] in pixels"))
            doc.add(comment("backend.type: local | google-cloud-vision | azure-vision"))
            doc['see'] = config['see']
            doc.add(nl())

        # Shine (LED) section
        if 'shine' in config:
            doc.add(comment("LED Configuration"))
            doc.add(comment("neopixel.gpioPin: GPIO pin number (recommended: 21 for RPi 3/4, 10 for RPi 5)"))
            doc.add(comment("commonanode: RGB LED pins"))
            doc['shine'] = config['shine']
            doc.add(nl())

        # Wave (Servo) section
        if 'wave' in config:
            doc.add(comment("Servo Motor Configuration"))
            doc.add(comment("servoPin: PWM-capable GPIO pin (recommended: 18)"))
            doc['wave'] = config['wave']
            doc.add(nl())

        # Models section
        if 'models' in config:
            doc.add(comment("Custom Model Registry"))
            doc.add(comment("Define custom AI models for local processing"))
            doc['models'] = config['models']
            doc.add(nl())

        # Recipe section
        if 'recipe' in config:
            doc.add(comment("Recipe-Specific Configuration"))
            doc.add(comment("Custom settings for your TJBot application"))
            doc['recipe'] = config['recipe']
            doc.add(nl())

        # Add any remaining sections not specifically handled
        handled_sections = {'log', 'hardware', 'listen', 'speak', 'see', 'shine', 'wave', 'models', 'recipe'}
        for key, value in config.items():
            if key not in handled_sections:
                doc[key] = value

        return doc

    def write_config(self, config: Dict[str, Any], path: Optional[Path] = None,
                     add_comments: bool = True, create_backup: bool = True) -> bool:
        """
        Write configuration to TOML file.

        Args:
            config: Configuration dictionary to write
            path: Path to write to (default: user config)
            add_comments: Whether to add explanatory comments
            create_backup: Whether to backup existing file

        Returns:
            True if successful, False on error
        """
        if path is None:
            path = self.user_config_path

        try:
            # Create directory if needed
            if not self.create_config_directory():
                return False

            # Create backup if file exists and backup requested
            if create_backup and path.exists():
                self.create_backup(path)
                self.cleanup_old_backups()

            # Prepare document
            if add_comments:
                doc = self.add_comments_to_config(config)
            else:
                # Use existing TOMLDocument if available, else create new
                if isinstance(config, TOMLDocument):
                    doc = config
                else:
                    doc = document()
                    for key, value in config.items():
                        doc[key] = value

            # Write to file
            with open(path, 'w', encoding='utf-8') as f:
                tomlkit.dump(doc, f)

            # Set appropriate permissions (644 - readable by all, writable by owner)
            path.chmod(0o644)

            return True

        except Exception as e:
            print(f"Error writing config: {e}")
            return False

    def set_file_permissions(self, path: Path, mode: int = 0o600):
        """
        Set file permissions (especially for credential files).

        Args:
            path: Path to file
            mode: Permission mode (default: 600 - owner read/write only)
        """
        try:
            path.chmod(mode)
        except Exception as e:
            print(f"Warning: Could not set permissions on {path}: {e}")

    def get_user_config_path(self) -> Path:
        """Get path to user configuration file."""
        return self.user_config_path

    def get_config_dir(self) -> Path:
        """Get path to configuration directory."""
        return self.config_dir


def write_tjbot_config(config: Dict[str, Any]) -> bool:
    """
    Convenience function to write TJBot configuration.

    Args:
        config: Configuration dictionary

    Returns:
        True if successful, False on error
    """
    writer = ConfigWriter()
    return writer.write_config(config)
