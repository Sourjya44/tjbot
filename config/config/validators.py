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
Configuration validators for TJBot settings.

This module provides validation functions for GPIO pins, configuration values,
credential formats, and hardware conflicts.
"""

import re
from typing import Dict, List, Tuple, Optional, Any

from jsonschema import Draft7Validator

from config.device_detection import get_system_info
from config.schema_loader import TJBotConfigSchema, load_config_schema


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, valid: bool = True, warnings: List[str] = None,
                 errors: List[str] = None, suggestions: List[str] = None):
        self.valid = valid
        self.warnings = warnings or []
        self.errors = errors or []
        self.suggestions = suggestions or []

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.valid = False

    def add_suggestion(self, message: str):
        """Add a suggestion message."""
        self.suggestions.append(message)

    def __bool__(self):
        """Return True if validation passed (no errors)."""
        return self.valid

    def __str__(self):
        """String representation of validation result."""
        parts = []
        if self.errors:
            parts.append("Errors: " + "; ".join(self.errors))
        if self.warnings:
            parts.append("Warnings: " + "; ".join(self.warnings))
        if self.suggestions:
            parts.append("Suggestions: " + "; ".join(self.suggestions))
        return " | ".join(parts) if parts else "Valid"


def _append_unique(target: List[str], values: List[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _format_jsonschema_error_path(error) -> str:
    path = '.'.join(str(part) for part in error.absolute_path)
    return path if path else '<root>'


def validate_schema_config(
    config: Dict[str, Any],
    schema: Optional[TJBotConfigSchema] = None,
) -> ValidationResult:
    """Validate config structure and types against the external JSON Schema."""
    result = ValidationResult()

    active_schema = schema or load_config_schema(required=True)
    validator = Draft7Validator(active_schema.raw_schema)
    errors = sorted(validator.iter_errors(config), key=lambda item: list(item.absolute_path))

    for error in errors:
        result.add_error(f'{_format_jsonschema_error_path(error)}: {error.message}')

    return result


class ConfigValidators:
    """Validators for TJBot configuration values."""

    # Valid GPIO pins for different purposes on different RPi models
    NEOPIXEL_PINS_RPI3_4 = [10, 12, 18, 21]
    NEOPIXEL_PINS_RPI5 = [10]
    SERVO_PINS = [12, 13, 18, 19]  # PWM-capable pins

    # Audio pin conflicts
    AUDIO_CONFLICT_PINS = [18]  # GPIO 18 used for PWM audio

    @staticmethod
    def validate_neopixel_pin(pin: int, rpi_model: str = '4') -> ValidationResult:
        """
        Validate GPIO pin for NeoPixel LED.

        Args:
            pin: GPIO pin number
            rpi_model: Raspberry Pi model ('3', '4', '5', etc.)

        Returns:
            ValidationResult with validation status and messages
        """
        result = ValidationResult()

        # Determine valid pins based on model
        if rpi_model == '5':
            valid_pins = ConfigValidators.NEOPIXEL_PINS_RPI5
        else:
            valid_pins = ConfigValidators.NEOPIXEL_PINS_RPI3_4

        if pin not in valid_pins:
            result.add_error(
                f"GPIO {pin} is not valid for NeoPixel on Raspberry Pi {rpi_model}. "
                f"Valid pins: {valid_pins}"
            )
            result.add_suggestion(f"Use GPIO {valid_pins[0]} (recommended)")
            return result

        # Check for audio conflict on GPIO 18
        if pin == 18:
            result.add_warning(
                "GPIO 18 conflicts with audio output. "
                "If using speaker, audio will be disabled or LED won't work properly."
            )
            result.add_suggestion("Use GPIO 21 instead to avoid conflicts")

        # GPIO 10 warning for RPi 5
        if pin == 10 and rpi_model == '5':
            result.add_warning(
                "On Raspberry Pi 5, GPIO 10 requires SPI interface (/dev/spidev0.0)"
            )

        return result

    @staticmethod
    def validate_servo_pin(pin: int) -> ValidationResult:
        """
        Validate GPIO pin for servo motor.

        Args:
            pin: GPIO pin number

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if pin not in ConfigValidators.SERVO_PINS:
            result.add_error(
                f"GPIO {pin} is not PWM-capable. "
                f"Valid servo pins: {ConfigValidators.SERVO_PINS}"
            )
            result.add_suggestion("Use GPIO 18 (recommended if not using audio)")
            return result

        if pin == 18:
            result.add_warning(
                "GPIO 18 conflicts with audio output. "
                "Speaker will be disabled if servo is enabled."
            )

        return result

    @staticmethod
    def validate_commonanode_pins(red: int, green: int, blue: int) -> ValidationResult:
        """
        Validate GPIO pins for common anode RGB LED.

        Args:
            red: GPIO pin for red channel
            green: GPIO pin for green channel
            blue: GPIO pin for blue channel

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        # Check for valid pin numbers (0-27 typical range)
        for color, pin in [('red', red), ('green', green), ('blue', blue)]:
            if not (0 <= pin <= 27):
                result.add_error(f"{color.capitalize()} pin GPIO {pin} is out of valid range (0-27)")

        # Check for duplicates
        pins = [red, green, blue]
        if len(pins) != len(set(pins)):
            result.add_error("Duplicate pins detected. Each color must use a different GPIO pin.")

        # Warn about PWM pins (they work but might be needed elsewhere)
        pwm_pins = set(pins) & set(ConfigValidators.SERVO_PINS)
        if pwm_pins:
            result.add_warning(
                f"GPIO {sorted(pwm_pins)} are PWM-capable. Consider using non-PWM pins "
                f"to reserve these for servo/audio."
            )

        return result

    @staticmethod
    def validate_confidence(value: float) -> ValidationResult:
        """
        Validate confidence threshold value.

        Args:
            value: Confidence threshold (should be 0.0 to 1.0)

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if not isinstance(value, (int, float)):
            result.add_error(f"Confidence must be a number, got {type(value).__name__}")
            return result

        if not (0.0 <= value <= 1.0):
            result.add_error(f"Confidence must be between 0.0 and 1.0, got {value}")
            result.add_suggestion("Use 0.5 for balanced precision/recall")

        if value < 0.3:
            result.add_warning("Very low confidence threshold may produce many false positives")
        elif value > 0.9:
            result.add_warning("Very high confidence threshold may miss valid detections")

        return result

    @staticmethod
    def validate_resolution(width: int, height: int) -> ValidationResult:
        """
        Validate camera resolution.

        Args:
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        # Check types
        if not isinstance(width, int) or not isinstance(height, int):
            result.add_error("Resolution dimensions must be integers")
            return result

        # Check reasonable ranges
        if width < 320 or height < 240:
            result.add_error("Resolution too small. Minimum recommended: 320x240")

        if width > 4096 or height > 3072:
            result.add_error("Resolution too large. Maximum supported: 4096x3072")

        # Check aspect ratio (warn if unusual)
        aspect_ratio = width / height if height > 0 else 0
        common_ratios = [
            (16/9, "16:9"), (4/3, "4:3"), (16/10, "16:10"), (1, "1:1")
        ]

        ratio_match = False
        for ratio, name in common_ratios:
            if abs(aspect_ratio - ratio) < 0.01:
                ratio_match = True
                break

        if not ratio_match and aspect_ratio > 0:
            result.add_warning(
                f"Unusual aspect ratio {width}:{height}. "
                f"Common ratios: 16:9 (1920x1080), 4:3 (1280x960)"
            )

        # Performance warnings
        if width * height > 1920 * 1080:
            result.add_warning(
                "High resolution may impact performance on Raspberry Pi. "
                "Consider 1920x1080 or lower."
            )

        return result

    @staticmethod
    def validate_sample_rate(rate: int) -> ValidationResult:
        """
        Validate audio sample rate.

        Args:
            rate: Sample rate in Hz

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if not isinstance(rate, int):
            result.add_error("Sample rate must be an integer")
            return result

        common_rates = [8000, 16000, 22050, 44100, 48000, 96000]

        if rate not in common_rates:
            result.add_warning(
                f"Unusual sample rate {rate} Hz. Common rates: {common_rates}"
            )

        if rate < 8000:
            result.add_error("Sample rate too low. Minimum: 8000 Hz")

        if rate > 96000:
            result.add_warning("Very high sample rate may impact performance")

        # Recommendations
        if rate == 8000:
            result.add_suggestion("8000 Hz is only suitable for simple voice recognition")
        elif rate == 16000:
            result.add_suggestion("16000 Hz is good for speech recognition")
        elif rate >= 44100:
            result.add_suggestion("44100+ Hz is high quality but may be overkill for speech")

        return result

    @staticmethod
    def validate_gpio_conflicts(config: Dict[str, Any], rpi_model: str = '4') -> ValidationResult:
        """
        Check for GPIO pin conflicts in full configuration.

        Args:
            config: Full configuration dictionary
            rpi_model: Raspberry Pi model ('3', '4', '5', etc.)

        Returns:
            ValidationResult with any conflicts found
        """
        result = ValidationResult()

        # Collect all GPIO pins in use
        pins_in_use = {}

        shine_cfg = config.get('shine', {})

        neopixel_enabled = bool(shine_cfg.get('hasNeopixelLED', False))
        common_anode_enabled = bool(shine_cfg.get('hasCommonAnodeLED', False))

        # Check NeoPixel
        if neopixel_enabled:
            # NeoPixel pin conflicts only apply to PWM/GPIO mode (RPi 3/4).
            # RPi 5 uses SPI interface for NeoPixel control.
            if rpi_model in ('3', '4'):
                pin = config.get('shine', {}).get('neopixel', {}).get('gpioPin')
                if pin:
                    pins_in_use[pin] = 'NeoPixel LED'

        # Check Common Anode
        if common_anode_enabled:
            ca_config = config.get('shine', {}).get('commonanode', {})
            for color in ['redPin', 'greenPin', 'bluePin']:
                pin = ca_config.get(color)
                if pin:
                    if pin in pins_in_use:
                        result.add_error(
                            f"GPIO {pin} conflict: used by both {pins_in_use[pin]} "
                            f"and Common Anode LED ({color})"
                        )
                    pins_in_use[pin] = f'Common Anode LED ({color})'

        # Check Servo
        if config.get('hardware', {}).get('servo', False):
            pin = config.get('wave', {}).get('servoPin')
            if pin:
                if pin in pins_in_use:
                    result.add_error(
                        f"GPIO {pin} conflict: used by both {pins_in_use[pin]} and Servo"
                    )
                pins_in_use[pin] = 'Servo'

        # Check speaker + GPIO 18 conflicts (RPi 3/4 only)
        if config.get('hardware', {}).get('speaker', False):
            if 18 in pins_in_use and rpi_model in ('3', '4'):
                result.add_warning(
                    f"GPIO 18 (PWM audio pin on RPi {rpi_model}) is used by {pins_in_use[18]}. "
                    f"Using both may cause audio distortion or servo jitter. "
                    f"Consider using a different servo pin (12, 13, or 19)."
                )

        return result

    @staticmethod
    def validate_ibm_api_key(api_key: str) -> ValidationResult:
        """
        Validate IBM Cloud API key format.

        Args:
            api_key: IBM Cloud API key string

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if not api_key or not api_key.strip():
            result.add_error("API key cannot be empty")
            return result

        # IBM API keys typically start with specific patterns
        # and are alphanumeric with dashes/underscores
        if len(api_key) < 20:
            result.add_warning("API key seems too short. Check if it's complete.")

        if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
            result.add_warning(
                "API key contains unusual characters. "
                "IBM keys are typically alphanumeric with dashes/underscores."
            )

        return result

    @staticmethod
    def validate_service_url(url: str) -> ValidationResult:
        """
        Validate IBM Watson service URL format.

        Args:
            url: Service URL

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if not url or not url.strip():
            result.add_error("Service URL cannot be empty")
            return result

        if not url.startswith('https://'):
            result.add_error("Service URL must start with https://")

        if 'watson' not in url.lower() and 'cloud.ibm.com' not in url.lower():
            result.add_warning(
                "URL doesn't look like an IBM Watson service URL. "
                "Expected format: https://api.{region}.{service}.watson.cloud.ibm.com"
            )

        return result

    @staticmethod
    def validate_audio_device(device_id: str) -> ValidationResult:
        """
        Validate audio device ID format.

        Args:
            device_id: Device ID (e.g., 'plughw:2,0')

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        if not device_id or not device_id.strip():
            result.add_error("Audio device ID cannot be empty")
            return result

        # Common device ID patterns
        valid_patterns = [
            r'^plughw:\d+,\d+$',  # plughw:2,0
            r'^hw:\d+,\d+$',       # hw:2,0
            r'^default$',           # default
            r'^sysdefault$',        # sysdefault
        ]

        if not any(re.match(pattern, device_id) for pattern in valid_patterns):
            result.add_warning(
                f"Device ID '{device_id}' doesn't match common formats. "
                f"Expected: plughw:X,Y or hw:X,Y or default"
            )

        return result

    @staticmethod
    def validate_log_level(level: str) -> ValidationResult:
        """
        Validate log level string.

        Args:
            level: Log level ('error', 'warning', 'info', 'verbose', 'debug')

        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult()

        valid_levels = ['error', 'warning', 'info', 'verbose', 'debug']

        if level not in valid_levels:
            result.add_error(
                f"Invalid log level '{level}'. Valid levels: {valid_levels}"
            )
            result.add_suggestion("Use 'info' for normal operation")

        return result


def validate_config(
    config: Dict[str, Any],
    schema: Optional[TJBotConfigSchema] = None,
) -> ValidationResult:
    """
    Validate entire configuration dictionary.

    Args:
        config: Full configuration dictionary

    Returns:
        ValidationResult with all validation issues found
    """
    result = ValidationResult()
    validators = ConfigValidators()

    schema_result = validate_schema_config(config, schema=schema)
    _append_unique(result.errors, schema_result.errors)

    # Get system info to determine RPi model
    system_info = get_system_info()
    rpi_model = system_info.get('raspberry_pi', {}).get('model', '4')

    # Validate log level
    log_level = config.get('log', {}).get('level')
    if log_level:
        level_result = validators.validate_log_level(log_level)
        _append_unique(result.errors, level_result.errors)
        _append_unique(result.warnings, level_result.warnings)

    # Validate GPIO conflicts
    gpio_result = validators.validate_gpio_conflicts(config, rpi_model)
    _append_unique(result.errors, gpio_result.errors)
    _append_unique(result.warnings, gpio_result.warnings)

    # Validate audio devices
    listen_device = config.get('listen', {}).get('device')
    if listen_device:
        device_result = validators.validate_audio_device(listen_device)
        _append_unique(result.warnings, device_result.warnings)

    speak_device = config.get('speak', {}).get('device')
    if speak_device:
        device_result = validators.validate_audio_device(speak_device)
        _append_unique(result.warnings, device_result.warnings)

    # Validate camera resolution
    camera_res = config.get('see', {}).get('cameraResolution')
    if camera_res and len(camera_res) == 2:
        res_result = validators.validate_resolution(camera_res[0], camera_res[1])
        _append_unique(result.errors, res_result.errors)
        _append_unique(result.warnings, res_result.warnings)

    # Validate confidence thresholds
    vision_local = config.get('see', {}).get('backend', {}).get('local', {})
    for threshold_key in ['objectDetectionConfidence', 'imageClassificationConfidence',
                           'faceDetectionConfidence']:
        threshold = vision_local.get(threshold_key)
        if threshold is not None:
            conf_result = validators.validate_confidence(threshold)
            _append_unique(result.errors, conf_result.errors)
            _append_unique(result.warnings, conf_result.warnings)

    # Update valid flag
    result.valid = len(result.errors) == 0

    return result
