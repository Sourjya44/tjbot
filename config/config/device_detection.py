"""
Hardware device detection for TJBot configuration.

This module provides functions to detect audio devices, camera, Raspberry Pi model,
and GPIO pin usage.
"""

import subprocess
import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class DeviceDetection:
    """Detect and enumerate TJBot hardware devices."""
    
    @staticmethod
    def detect_audio_input_devices() -> List[Dict[str, any]]:
        """
        Detect audio input devices using arecord.
        
        Returns:
            List of dictionaries with device information:
            [{'id': 'plughw:2,0', 'name': 'USB Audio Device', 'default': bool}]
        """
        devices = []
        
        try:
            result = subprocess.run(
                ['arecord', '-L'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return devices
            
            # Parse arecord output
            lines = result.stdout.split('\n')
            current_device = None
            current_desc = []
            
            for line in lines:
                if not line.startswith(' ') and line.strip():
                    # New device ID
                    if current_device and current_desc:
                        # Save previous device
                        name = ' '.join(current_desc).strip()
                        devices.append({
                            'id': current_device,
                            'name': name,
                            'default': 'default' in current_device.lower()
                        })
                    
                    current_device = line.strip()
                    current_desc = []
                elif line.strip():
                    # Description line
                    current_desc.append(line.strip())
            
            # Add last device
            if current_device and current_desc:
                name = ' '.join(current_desc).strip()
                devices.append({
                    'id': current_device,
                    'name': name,
                    'default': 'default' in current_device.lower()
                })
            
            # Filter to keep useful devices (plughw, hw, default, sysdefault)
            useful_devices = []
            for dev in devices:
                dev_id = dev['id']
                if any(prefix in dev_id for prefix in ['plughw:', 'hw:', 'default', 'sysdefault']):
                    useful_devices.append(dev)
            
            return useful_devices
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            # arecord not found or error
            return []
    
    @staticmethod
    def detect_audio_output_devices() -> List[Dict[str, any]]:
        """
        Detect audio output devices using aplay.
        
        Returns:
            List of dictionaries with device information:
            [{'id': 'plughw:0,0', 'name': 'Built-in Audio', 'default': bool}]
        """
        devices = []
        
        try:
            result = subprocess.run(
                ['aplay', '-L'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return devices
            
            # Parse aplay output (same format as arecord)
            lines = result.stdout.split('\n')
            current_device = None
            current_desc = []
            
            for line in lines:
                if not line.startswith(' ') and line.strip():
                    # New device ID
                    if current_device and current_desc:
                        # Save previous device
                        name = ' '.join(current_desc).strip()
                        devices.append({
                            'id': current_device,
                            'name': name,
                            'default': 'default' in current_device.lower()
                        })
                    
                    current_device = line.strip()
                    current_desc = []
                elif line.strip():
                    # Description line
                    current_desc.append(line.strip())
            
            # Add last device
            if current_device and current_desc:
                name = ' '.join(current_desc).strip()
                devices.append({
                    'id': current_device,
                    'name': name,
                    'default': 'default' in current_device.lower()
                })
            
            # Filter to keep useful devices
            useful_devices = []
            for dev in devices:
                dev_id = dev['id']
                if any(prefix in dev_id for prefix in ['plughw:', 'hw:', 'default', 'sysdefault']):
                    useful_devices.append(dev)
            
            return useful_devices
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return []
    
    @staticmethod
    def detect_camera() -> Dict[str, bool]:
        """
        Detect camera module using vcgencmd.
        
        Returns:
            Dictionary with camera status:
            {'detected': bool, 'supported': bool, 'enabled': bool}
        """
        result = {
            'detected': False,
            'supported': False,
            'enabled': False
        }
        
        try:
            cmd_result = subprocess.run(
                ['vcgencmd', 'get_camera'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if cmd_result.returncode == 0:
                output = cmd_result.stdout.strip()
                # Output format: "supported=1 detected=1"
                
                if 'supported=1' in output:
                    result['supported'] = True
                if 'detected=1' in output:
                    result['detected'] = True
                
                # On newer systems, might need to check different way
                # Also check if camera is enabled in config
                result['enabled'] = result['supported'] and result['detected']
            
            return result
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # vcgencmd not found or error
            # Try alternative detection via /dev/video0
            if os.path.exists('/dev/video0'):
                result['detected'] = True
                result['enabled'] = True
            
            return result
    
    @staticmethod
    def detect_rpi_model() -> Dict[str, any]:
        """
        Detect Raspberry Pi model information.
        
        Returns:
            Dictionary with RPi information:
            {'model': '4B', 'revision': '1.4', 'memory': 4096, 'gpio_chip': 'BCM2711'}
        """
        result = {
            'model': 'Unknown',
            'revision': 'Unknown',
            'memory': 0,
            'gpio_chip': 'Unknown'
        }
        
        # Try reading from device tree
        model_file = Path('/proc/device-tree/model')
        if model_file.exists():
            try:
                model_str = model_file.read_text().strip('\x00')
                # Example: "Raspberry Pi 4 Model B Rev 1.4"
                result['model'] = DeviceDetection._parse_rpi_model(model_str)
            except Exception:
                pass
        
        # Read cpuinfo for additional details
        cpuinfo_file = Path('/proc/cpuinfo')
        if cpuinfo_file.exists():
            try:
                cpuinfo = cpuinfo_file.read_text()
                
                # Look for Hardware line
                hw_match = re.search(r'Hardware\s*:\s*(\S+)', cpuinfo)
                if hw_match:
                    result['gpio_chip'] = hw_match.group(1)
                
                # Look for Revision
                rev_match = re.search(r'Revision\s*:\s*(\S+)', cpuinfo)
                if rev_match:
                    result['revision'] = rev_match.group(1)
                    # Decode revision to get memory
                    result['memory'] = DeviceDetection._decode_revision_memory(rev_match.group(1))
                
            except Exception:
                pass
        
        return result
    
    @staticmethod
    def _parse_rpi_model(model_str: str) -> str:
        """Parse Raspberry Pi model string."""
        # Extract model number/letter
        if 'Pi 5' in model_str:
            return '5'
        elif 'Pi 4' in model_str:
            return '4'
        elif 'Pi 3' in model_str:
            if 'Model B+' in model_str or 'Plus' in model_str:
                return '3B+'
            return '3'
        elif 'Pi 2' in model_str:
            return '2'
        elif 'Pi Zero' in model_str:
            if 'W' in model_str:
                return 'Zero W'
            return 'Zero'
        
        return 'Unknown'
    
    @staticmethod
    def _decode_revision_memory(revision: str) -> int:
        """Decode memory size from revision code."""
        try:
            # New-style revision code (bit 23 set)
            rev_int = int(revision, 16)
            if rev_int & (1 << 23):
                # Bits 20-22 encode memory size
                mem_code = (rev_int >> 20) & 0x7
                mem_sizes = [256, 512, 1024, 2048, 4096, 8192]
                if mem_code < len(mem_sizes):
                    return mem_sizes[mem_code]
        except ValueError:
            pass
        
        return 0
    
    @staticmethod
    def list_gpio_in_use() -> List[int]:
        """
        List GPIO pins currently in use by checking /sys/class/gpio.
        
        Returns:
            List of GPIO pin numbers currently exported.
        """
        gpio_pins = []
        gpio_dir = Path('/sys/class/gpio')
        
        if not gpio_dir.exists():
            return gpio_pins
        
        try:
            for item in gpio_dir.iterdir():
                if item.is_dir() and item.name.startswith('gpio'):
                    # Extract pin number from gpio123
                    pin_match = re.match(r'gpio(\d+)', item.name)
                    if pin_match:
                        gpio_pins.append(int(pin_match.group(1)))
            
            return sorted(gpio_pins)
            
        except Exception:
            return gpio_pins
    
    @staticmethod
    def get_recommended_led_pin(rpi_model: str) -> int:
        """
        Get recommended GPIO pin for NeoPixel LED based on RPi model.
        
        Args:
            rpi_model: Raspberry Pi model string ('3', '4', '5', etc.)
        
        Returns:
            Recommended GPIO pin number.
        """
        if rpi_model == '5':
            # RPi 5 only supports GPIO 10 with SPI
            return 10
        else:
            # RPi 3/4 - GPIO 21 is safest (no conflicts with audio/PWM)
            return 21
    
    @staticmethod
    def format_device_for_display(device: Dict[str, any]) -> str:
        """
        Format a device dictionary for user-friendly display.
        
        Args:
            device: Device dictionary with 'id' and 'name'
        
        Returns:
            Formatted string like "USB Audio Device (plughw:2,0)"
        """
        name = device.get('name', 'Unknown Device')
        dev_id = device.get('id', '')
        
        # Truncate long names
        if len(name) > 50:
            name = name[:47] + '...'
        
        if device.get('default', False):
            return f"{name} (default)"
        else:
            return f"{name} ({dev_id})"


# Convenience functions for direct use
def detect_audio_devices() -> Tuple[List[Dict], List[Dict]]:
    """
    Detect both input and output audio devices.
    
    Returns:
        Tuple of (input_devices, output_devices)
    """
    detector = DeviceDetection()
    return (detector.detect_audio_input_devices(), 
            detector.detect_audio_output_devices())


def get_system_info() -> Dict[str, any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with all detected hardware information.
    """
    detector = DeviceDetection()
    
    input_devices, output_devices = detect_audio_devices()
    camera_info = detector.detect_camera()
    rpi_info = detector.detect_rpi_model()
    gpio_in_use = detector.list_gpio_in_use()
    
    return {
        'audio_input': input_devices,
        'audio_output': output_devices,
        'camera': camera_info,
        'raspberry_pi': rpi_info,
        'gpio_in_use': gpio_in_use,
        'recommended_led_pin': detector.get_recommended_led_pin(rpi_info['model'])
    }
