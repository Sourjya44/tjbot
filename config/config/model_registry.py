"""
Model registry integration for TJBot AI models.

Parses model-registry.yaml from node-tjbotlib and provides model information
for configuration wizards.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class ModelRegistry:
    """Interface to TJBot model registry."""
    
    # Fallback minimal models if registry file not found
    FALLBACK_MODELS = {
        'stt': [
            {
                'key': 'sherpa-onnx-whisper-base.en',
                'label': 'Whisper Base (English)',
                'size_mb': 199,
                'quality': 'Good',
                'description': 'Balanced quality and speed for English speech recognition'
            }
        ],
        'tts': [
            {
                'key': 'vits-piper-en_US-ryan-medium',
                'label': 'Ryan (US Male, Medium)',
                'size_mb': 18,
                'quality': 'Good',
                'description': 'Natural-sounding American English male voice'
            }
        ],
        'vad': [
            {
                'key': 'silero-vad',
                'label': 'Silero VAD',
                'size_mb': 1,
                'quality': 'Excellent',
                'description': 'Voice activity detection'
            }
        ],
        'vision': {
            'object-detection': [
                {
                    'key': 'ssd-mobilenet-v2',
                    'label': 'SSD MobileNet V2',
                    'size_mb': 65,
                    'quality': 'Good',
                    'description': 'Fast object detection with 80+ categories'
                }
            ],
            'classification': [
                {
                    'key': 'mobilenetv3',
                    'label': 'MobileNet V3',
                    'size_mb': 10,
                    'quality': 'Good',
                    'description': 'Efficient image classification'
                }
            ],
            'face-detection': [
                {
                    'key': 'scrfd-2.5g',
                    'label': 'SCRFD 2.5G',
                    'size_mb': 3,
                    'quality': 'Good',
                    'description': 'Accurate face detection'
                }
            ]
        }
    }
    
    def __init__(self):
        self.registry_path = self._find_registry()
        self.registry_data = None
        
        if self.registry_path:
            self.load_registry()
    
    def _find_registry(self) -> Optional[Path]:
        """
        Find model-registry.yaml from node-tjbotlib.
        
        Returns:
            Path to model-registry.yaml or None if not found
        """
        search_paths = [
            Path.home() / 'Desktop' / 'node-tjbotlib' / 'src' / 'config' / 'model-registry.yaml',
            Path('/usr/local/lib/node_modules/node-tjbotlib/src/config/model-registry.yaml'),
            Path('/usr/lib/node_modules/node-tjbotlib/src/config/model-registry.yaml'),
            Path.home() / 'node_modules' / 'node-tjbotlib' / 'src' / 'config' / 'model-registry.yaml',
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        return None
    
    def load_registry(self) -> bool:
        """
        Load model registry from YAML file.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.registry_path:
            return False
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry_data = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Warning: Could not load model registry: {e}")
            return False
    
    def _parse_size_mb(self, size_str: str) -> float:
        """Parse size string like '199 MB' or '3.3 MB' to float."""
        try:
            # Remove 'MB' and any whitespace, convert to float
            size_str = size_str.upper().replace('MB', '').replace('GB', '000').strip()
            return float(size_str)
        except (ValueError, AttributeError):
            return 0
    
    def get_stt_models(self) -> List[Dict[str, Any]]:
        """
        Get speech-to-text models from registry.
        
        Returns:
            List of STT model dictionaries with display info
        """
        if not self.registry_data or not isinstance(self.registry_data, dict):
            return self.FALLBACK_MODELS['stt']
        
        models = []
        
        try:
            for model_key, model_data in self.registry_data.items():
                if not isinstance(model_data, dict):
                    continue
                if model_data.get('type') == 'stt':
                    # Parse size from URL or required files
                    size_mb = 0
                    if 'size' in model_data:
                        size_mb = self._parse_size_mb(model_data['size'])
                    elif 'whisper' in model_key.lower():
                        # Rough estimates for Whisper models
                        if 'tiny' in model_key:
                            size_mb = 113
                        elif 'base' in model_key:
                            size_mb = 199
                        else:
                            size_mb = 150
                    
                    models.append({
                        'key': model_key,
                        'label': model_data.get('label', model_key),
                        'size_mb': size_mb,
                        'quality': 'Good',  # Could parse from description
                        'description': f"{model_data.get('label', model_key)} - {model_data.get('kind', 'offline')} model"
                    })
        except Exception as e:
            print(f"Error parsing STT models: {e}")
            return self.FALLBACK_MODELS['stt']
        
        return models if models else self.FALLBACK_MODELS['stt']
    
    def get_tts_models(self) -> List[Dict[str, Any]]:
        """
        Get text-to-speech models from registry.
        
        Returns:
            List of TTS model dictionaries with display info
        """
        if not self.registry_data or not isinstance(self.registry_data, dict):
            return self.FALLBACK_MODELS['tts']
        
        models = []
        
        try:
            for model_key, model_data in self.registry_data.items():
                if not isinstance(model_data, dict):
                    continue
                if model_data.get('type') == 'tts':
                    size_mb = 0
                    if 'size' in model_data:
                        size_mb = self._parse_size_mb(model_data['size'])
                    else:
                        # Estimate for TTS models (usually 5-20 MB)
                        size_mb = 15
                    
                    label = model_data.get('label', model_key)
                    
                    models.append({
                        'key': model_key,
                        'label': label,
                        'size_mb': size_mb,
                        'quality': 'Good',
                        'description': label
                    })
        except Exception as e:
            print(f"Error parsing TTS models: {e}")
            return self.FALLBACK_MODELS['tts']
        
        return models if models else self.FALLBACK_MODELS['tts']
    
    def get_vision_models(self, model_type: str = 'object-detection') -> List[Dict[str, Any]]:
        """
        Get vision models from registry.
        
        Args:
            model_type: 'object-detection', 'classification', or 'face-detection'
        
        Returns:
            List of vision model dictionaries
        """
        if not self.registry_data or not isinstance(self.registry_data, dict):
            return self.FALLBACK_MODELS['vision'].get(model_type, [])
        
        models = []
        vision_type_map = {
            'object-detection': 'vision.object-recognition',
            'classification': 'vision.classification',
            'face-detection': 'vision.face-detection'
        }
        
        registry_type = vision_type_map.get(model_type, model_type)
        
        try:
            for model_key, model_data in self.registry_data.items():
                if not isinstance(model_data, dict):
                    continue
                if model_data.get('type') == registry_type:
                    size_mb = 0
                    if 'size' in model_data:
                        size_mb = self._parse_size_mb(model_data['size'])
                    else:
                        # Default estimates
                        size_mb = 20
                    
                    models.append({
                        'key': model_key,
                        'label': model_data.get('label', model_key),
                        'size_mb': size_mb,
                        'quality': 'Good',
                        'description': model_data.get('label', model_key)
                    })
        except Exception as e:
            print(f"Error parsing vision models: {e}")
            return self.FALLBACK_MODELS['vision'].get(model_type, [])
        
        return models if models else self.FALLBACK_MODELS['vision'].get(model_type, [])
    
    def get_vad_models(self) -> List[Dict[str, Any]]:
        """
        Get voice activity detection models.
        
        Returns:
            List of VAD model dictionaries
        """
        if not self.registry_data or not isinstance(self.registry_data, dict):
            return self.FALLBACK_MODELS['vad']
        
        models = []
        
        try:
            for model_key, model_data in self.registry_data.items():
                if not isinstance(model_data, dict):
                    continue
                if model_data.get('type') == 'vad':
                    models.append({
                        'key': model_key,
                        'label': model_data.get('label', model_key),
                        'size_mb': 1,
                        'quality': 'Excellent',
                        'description': model_data.get('label', model_key)
                    })
        except Exception:
            return self.FALLBACK_MODELS['vad']
        
        return models if models else self.FALLBACK_MODELS['vad']
    
    def format_model_option(self, model: Dict[str, Any]) -> str:
        """
        Format model for display in selection list.
        
        Args:
            model: Model dictionary
        
        Returns:
            Formatted string like "Whisper Base (199 MB) - Good quality, fast"
        """
        label = model.get('label', 'Unknown Model')
        size_mb = model.get('size_mb', 0)
        
        if size_mb > 0:
            return f"{label} ({int(size_mb)} MB)"
        else:
            return label
    
    def get_model_details(self, model_key: str) -> Optional[Dict[str, Any]]:
        """
        Get full details for a specific model.
        
        Args:
            model_key: Model key/identifier
        
        Returns:
            Model details dictionary or None if not found
        """
        if not self.registry_data or not isinstance(self.registry_data, dict):
            return None
        
        return self.registry_data.get(model_key)
    
    def calculate_total_download_size(self, selected_models: List[str]) -> float:
        """
        Calculate total download size for selected models.
        
        Args:
            selected_models: List of model keys
        
        Returns:
            Total size in MB
        """
        total_mb = 0
        
        # Get all models
        all_models = {}
        for model in self.get_stt_models():
            all_models[model['key']] = model
        for model in self.get_tts_models():
            all_models[model['key']] = model
        for model in self.get_vad_models():
            all_models[model['key']] = model
        for vision_type in ['object-detection', 'classification', 'face-detection']:
            for model in self.get_vision_models(vision_type):
                all_models[model['key']] = model
        
        # Sum sizes
        for model_key in selected_models:
            if model_key in all_models:
                total_mb += all_models[model_key].get('size_mb', 0)
        
        return total_mb
    
    def format_size(self, size_mb: float) -> str:
        """Format size in MB/GB for display."""
        if size_mb >= 1000:
            return f"{size_mb / 1000:.1f} GB"
        else:
            return f"{int(size_mb)} MB"


# Convenience functions
def get_stt_models() -> List[Dict[str, Any]]:
    """Get list of STT models."""
    registry = ModelRegistry()
    return registry.get_stt_models()


def get_tts_models() -> List[Dict[str, Any]]:
    """Get list of TTS models."""
    registry = ModelRegistry()
    return registry.get_tts_models()


def get_vision_models(model_type: str = 'object-detection') -> List[Dict[str, Any]]:
    """Get list of vision models."""
    registry = ModelRegistry()
    return registry.get_vision_models(model_type)
