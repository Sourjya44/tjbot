"""
Credential validator for cloud services.

Tests credentials against cloud provider APIs to verify they work.
"""

import requests
from typing import Dict, Tuple, Optional
import json
from pathlib import Path


class CredentialValidator:
    """Validate credentials for IBM Cloud, Google Cloud, and Azure."""
    
    @staticmethod
    def validate_ibm_credentials(service: str, api_key: str, url: str) -> Tuple[bool, str, Dict]:
        """
        Validate IBM Watson service credentials.
        
        Args:
            service: Service name ('speech-to-text', 'text-to-speech', etc.)
            api_key: IBM Cloud API key
            url: Service URL
        
        Returns:
            Tuple of (success, message, details)
        """
        try:
            # Make a simple GET request to the service URL
            # Most Watson services have a /v1/ or similar health endpoint
            response = requests.get(
                url,
                auth=('apikey', api_key),
                timeout=10
            )
            
            if response.status_code == 200:
                return (True, f"✓ {service} credentials are valid", {'status': 'active'})
            elif response.status_code == 401:
                return (False, f"✗ Invalid API key for {service}", {'error': 'unauthorized'})
            elif response.status_code == 403:
                return (False, f"✗ API key lacks permissions for {service}", {'error': 'forbidden'})
            elif response.status_code == 404:
                return (False, f"✗ Service URL not found. Check the URL for {service}", {'error': 'not_found'})
            else:
                # Some success codes or benign errors
                if response.status_code < 500:
                    return (True, f"✓ {service} credentials appear valid (status: {response.status_code})", {})
                else:
                    return (False, f"✗ Service error for {service}: {response.status_code}", {'error': 'server_error'})
        
        except requests.exceptions.Timeout:
            return (False, f"✗ Connection timeout for {service}. Check network connection.", {'error': 'timeout'})
        except requests.exceptions.ConnectionError:
            return (False, f"✗ Cannot connect to {service}. Check URL and network.", {'error': 'connection'})
        except Exception as e:
            return (False, f"✗ Error validating {service}: {str(e)}", {'error': 'exception'})
    
    @staticmethod
    def validate_google_credentials(json_path: str) -> Tuple[bool, str, Dict]:
        """
        Validate Google Cloud service account credentials.
        
        Args:
            json_path: Path to Google credentials JSON file
        
        Returns:
            Tuple of (success, message, details)
        """
        try:
            # Check file exists
            path = Path(json_path)
            if not path.exists():
                return (False, f"✗ Credentials file not found: {json_path}", {'error': 'not_found'})
            
            # Parse JSON
            with open(path, 'r') as f:
                creds = json.load(f)
            
            # Check required fields
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds]
            
            if missing_fields:
                return (False, f"✗ Missing required fields: {', '.join(missing_fields)}", {'error': 'invalid_format'})
            
            if creds.get('type') != 'service_account':
                return (False, "✗ Credentials must be for a service account", {'error': 'wrong_type'})
            
            # Basic validation passed - full validation requires Google auth library
            return (True, f"✓ Google Cloud credentials format is valid (project: {creds['project_id']})", 
                    {'project_id': creds['project_id'], 'email': creds['client_email']})
        
        except json.JSONDecodeError:
            return (False, "✗ Invalid JSON format in credentials file", {'error': 'invalid_json'})
        except Exception as e:
            return (False, f"✗ Error reading credentials: {str(e)}", {'error': 'exception'})
    
    @staticmethod
    def validate_azure_credentials(service: str, key: str, endpoint: str) -> Tuple[bool, str, Dict]:
        """
        Validate Azure Cognitive Services credentials.
        
        Args:
            service: Service name ('speech', 'vision', etc.)
            key: Azure subscription key
            endpoint: Azure endpoint URL
        
        Returns:
            Tuple of (success, message, details)
        """
        try:
            # Azure doesn't have a simple health check, but we can validate format
            if not endpoint.startswith('https://'):
                return (False, "✗ Azure endpoint must start with https://", {'error': 'invalid_url'})
            
            if 'cognitiveservices' not in endpoint.lower() and 'azure' not in endpoint.lower():
                return (False, "✗ Endpoint doesn't look like an Azure Cognitive Services URL", {'error': 'invalid_url'})
            
            if len(key) < 20:
                return (False, "✗ Azure key seems too short. Check if it's complete.", {'error': 'invalid_key'})
            
            # Parse region from endpoint
            region = 'unknown'
            if 'api.cognitive.microsoft.com' in endpoint:
                parts = endpoint.split('//')
                if len(parts) > 1:
                    region_part = parts[1].split('.')[0]
                    region = region_part
            
            # Format validation passed
            return (True, f"✓ Azure {service} credentials format is valid (region: {region})", {'region': region})
        
        except Exception as e:
            return (False, f"✗ Error validating credentials: {str(e)}", {'error': 'exception'})
    
    @staticmethod
    def test_all_credentials(config_dir: Path) -> Dict[str, Tuple[bool, str]]:
        """
        Test all credential files found in config directory.
        
        Args:
            config_dir: Path to ~/.tjbot directory
        
        Returns:
            Dictionary mapping service to (success, message) tuples
        """
        results = {}
        
        # Check for IBM credentials
        ibm_creds_path = config_dir / 'ibm-credentials.env'
        if ibm_creds_path.exists():
            try:
                # Parse .env file
                creds = CredentialValidator._parse_env_file(ibm_creds_path)
                
                # Test each service
                services = [
                    ('speech-to-text', 'SPEECH_TO_TEXT_APIKEY', 'SPEECH_TO_TEXT_URL'),
                    ('text-to-speech', 'TEXT_TO_SPEECH_APIKEY', 'TEXT_TO_SPEECH_URL'),
                    ('assistant', 'ASSISTANT_APIKEY', 'ASSISTANT_URL'),
                ]
                
                for service_name, key_var, url_var in services:
                    if key_var in creds and url_var in creds:
                        success, message, _ = CredentialValidator.validate_ibm_credentials(
                            service_name, creds[key_var], creds[url_var]
                        )
                        results[f'IBM {service_name}'] = (success, message)
            
            except Exception as e:
                results['IBM credentials'] = (False, f"Error reading IBM credentials: {e}")
        
        # Check for Google credentials
        google_creds_path = config_dir / 'google-credentials.json'
        if google_creds_path.exists():
            success, message, _ = CredentialValidator.validate_google_credentials(str(google_creds_path))
            results['Google Cloud'] = (success, message)
        
        # Check for Azure credentials
        azure_creds_path = config_dir / 'azure-credentials.env'
        if azure_creds_path.exists():
            try:
                creds = CredentialValidator._parse_env_file(azure_creds_path)
                
                services = [
                    ('speech', 'AZURE_SPEECH_KEY', 'AZURE_SPEECH_ENDPOINT'),
                    ('vision', 'AZURE_VISION_KEY', 'AZURE_VISION_ENDPOINT'),
                ]
                
                for service_name, key_var, endpoint_var in services:
                    if key_var in creds:
                        endpoint = creds.get(endpoint_var, f'https://{creds.get("AZURE_SPEECH_REGION", "eastus")}.api.cognitive.microsoft.com')
                        success, message, _ = CredentialValidator.validate_azure_credentials(
                            service_name, creds[key_var], endpoint
                        )
                        results[f'Azure {service_name}'] = (success, message)
            
            except Exception as e:
                results['Azure credentials'] = (False, f"Error reading Azure credentials: {e}")
        
        return results
    
    @staticmethod
    def _parse_env_file(path: Path) -> Dict[str, str]:
        """Parse .env file into dictionary."""
        env_vars = {}
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        return env_vars
