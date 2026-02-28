"""
IBM Cloud credential wizard.

Guides users through obtaining and configuring IBM Watson service credentials.
"""

from typing import Dict, List, Tuple
from pathlib import Path
import getpass


class IBMCloudWizard:
    """Interactive wizard for IBM Cloud Watson services setup."""
    
    WATSON_SERVICES = {
        'speech-to-text': {
            'name': 'Watson Speech to Text',
            'env_prefix': 'SPEECH_TO_TEXT',
            'catalog_url': 'https://cloud.ibm.com/catalog/services/speech-to-text',
            'default_url': 'https://api.us-south.speech-to-text.watson.cloud.ibm.com'
        },
        'text-to-speech': {
            'name': 'Watson Text to Speech',
            'env_prefix': 'TEXT_TO_SPEECH',
            'catalog_url': 'https://cloud.ibm.com/catalog/services/text-to-speech',
            'default_url': 'https://api.us-south.text-to-speech.watson.cloud.ibm.com'
        },
        'assistant': {
            'name': 'Watson Assistant',
            'env_prefix': 'ASSISTANT',
            'catalog_url': 'https://cloud.ibm.com/catalog/services/watson-assistant',
            'default_url': 'https://api.us-south.assistant.watson.cloud.ibm.com'
        }
    }
    
    def __init__(self, config_dir: Path):
        """
        Initialize IBM Cloud wizard.
        
        Args:
            config_dir: Path to ~/.tjbot directory
        """
        self.config_dir = config_dir
        self.credentials_path = config_dir / 'ibm-credentials.env'
    
    def get_instructions(self, services: List[str]) -> str:
        """
        Get step-by-step instructions for obtaining credentials.
        
        Args:
            services: List of service keys to configure
        
        Returns:
            Formatted instructions string
        """
        instructions = """
╔══════════════════════════════════════════════════════════════════╗
║              IBM CLOUD WATSON SERVICES SETUP                      ║
╚══════════════════════════════════════════════════════════════════╝

IBM Cloud offers Watson AI services with a FREE tier. You'll need:
  • A free IBM Cloud account (no credit card required for Lite plans)
  • Service instances for the capabilities you selected

STEP 1: CREATE AN IBM CLOUD ACCOUNT
----------------------------------- 
  1. Go to: https://cloud.ibm.com/registration
  2. Sign up with your email
  3. Verify your email address
  4. Log in to IBM Cloud console

"""
        
        for service_key in services:
            service = self.WATSON_SERVICES.get(service_key)
            if service:
                instructions += f"""
STEP 2: CREATE {service['name'].upper()} SERVICE
{'-' * 60}
  1. Go to: {service['catalog_url']}
  2. Click "Create"
  3. Select region: Dallas (us-south) or your preferred region
  4. Select plan: "Lite" (FREE - no credit card required)
  5. Give it a name (or use default)
  6. Click "Create"
  
  7. After creation, click "Manage" in left sidebar
  8. You'll see:
     • API Key: (click "Show" to reveal)
     • URL: (service endpoint URL)
  
  9. Copy both values - you'll enter them shortly

"""
        
        instructions += """
REGIONAL URLS (reference):
  • Dallas (us-south): api.us-south.[service].watson.cloud.ibm.com
  • Washington DC (us-east): api.us-east.[service].watson.cloud.ibm.com
  • Frankfurt (eu-de): api.eu-de.[service].watson.cloud.ibm.com
  • London (eu-gb): api.eu-gb.[service].watson.cloud.ibm.com
  • Tokyo (jp-tok): api.jp-tok.[service].watson.cloud.ibm.com
  • Sydney (au-syd): api.au-syd.[service].watson.cloud.ibm.com

Press Enter when ready to enter your credentials...
"""
        return instructions
    
    def collect_credentials(self, services: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Interactively collect credentials for services.
        
        Args:
            services: List of service keys to configure
        
        Returns:
            Dictionary mapping service keys to {'api_key': ..., 'url': ...}
        """
        credentials = {}
        
        print("\n" + "=" * 70)
        print("CREDENTIAL ENTRY")
        print("=" * 70)
        
        for service_key in services:
            service = self.WATSON_SERVICES.get(service_key)
            if not service:
                continue
            
            print(f"\n📝 {service['name']}")
            print("-" * 70)
            
            # Get API key (hidden input)
            api_key = getpass.getpass(f"API Key (input hidden): ").strip()
            
            # Get URL with default
            url = input(f"Service URL [{service['default_url']}]: ").strip()
            if not url:
                url = service['default_url']
            
            credentials[service_key] = {
                'api_key': api_key,
                'url': url
            }
            
            print(f"✓ {service['name']} credentials entered")
        
        return credentials
    
    def write_credentials(self, credentials: Dict[str, Dict[str, str]]) -> bool:
        """
        Write credentials to ibm-credentials.env file.
        
        Args:
            credentials: Dictionary of service credentials
        
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate .env file content
            content = self._generate_env_file(credentials)
            
            # Write file
            with open(self.credentials_path, 'w') as f:
                f.write(content)
            
            # Set secure permissions (owner read/write only)
            self.credentials_path.chmod(0o600)
            
            return True
        
        except Exception as e:
            print(f"Error writing credentials: {e}")
            return False
    
    def _generate_env_file(self, credentials: Dict[str, Dict[str, str]]) -> str:
        """Generate .env file content from credentials."""
        from datetime import datetime
        
        lines = [
            "# IBM Cloud Credentials for TJBot",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "#",
            "# These credentials are used by TJBot to access IBM Watson AI services.",
            "# Keep this file secure and do not share it publicly.",
            "",
        ]
        
        for service_key, creds in credentials.items():
            service = self.WATSON_SERVICES.get(service_key)
            if service:
                lines.append(f"# {service['name']}")
                lines.append(f"{service['env_prefix']}_APIKEY={creds['api_key']}")
                lines.append(f"{service['env_prefix']}_URL={creds['url']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def run(self, services: List[str]) -> bool:
        """
        Run the complete IBM Cloud credential wizard.
        
        Args:
            services: List of service keys to configure
        
        Returns:
            True if credentials were successfully configured
        """
        # Show instructions
        instructions = self.get_instructions(services)
        print(instructions)
        input()  # Wait for user to press Enter
        
        # Collect credentials
        credentials = self.collect_credentials(services)
        
        if not credentials:
            print("\n✗ No credentials entered")
            return False
        
        # Write to file
        if self.write_credentials(credentials):
            print(f"\n✓ Credentials saved to: {self.credentials_path}")
            return True
        else:
            return False


def run_ibm_wizard(config_dir: Path, services: List[str]) -> bool:
    """
    Convenience function to run IBM Cloud wizard.
    
    Args:
        config_dir: Path to ~/.tjbot directory
        services: List of services to configure
    
    Returns:
        True if successful
    """
    wizard = IBMCloudWizard(config_dir)
    return wizard.run(services)
