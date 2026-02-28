"""
Microsoft Azure credential wizard.

Guides users through obtaining and configuring Azure Cognitive Services credentials.
"""

from typing import Dict, List, Tuple
from pathlib import Path
import getpass


class AzureWizard:
    """Interactive wizard for Microsoft Azure Cognitive Services setup."""
    
    AZURE_SERVICES = {
        'speech': {
            'name': 'Azure Speech Services',
            'env_prefix': 'AZURE_SPEECH',
            'resource_type': 'Speech'
        },
        'vision': {
            'name': 'Azure Computer Vision',
            'env_prefix': 'AZURE_VISION',
            'resource_type': 'ComputerVision'
        }
    }
    
    REGIONS = {
        'eastus': 'East US',
        'westus': 'West US',
        'westus2': 'West US 2',
        'centralus': 'Central US',
        'westeurope': 'West Europe',
        'northeurope': 'North Europe',
        'eastasia': 'East Asia',
        'southeastasia': 'Southeast Asia',
        'japaneast': 'Japan East',
        'australiaeast': 'Australia East'
    }
    
    def __init__(self, config_dir: Path):
        """
        Initialize Azure wizard.
        
        Args:
            config_dir: Path to ~/.tjbot directory
        """
        self.config_dir = config_dir
        self.credentials_path = config_dir / 'azure-credentials.env'
    
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
║            MICROSOFT AZURE COGNITIVE SERVICES SETUP               ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: Azure requires a credit card for sign-up.
    Free tier includes:
    • Speech Services: 5 hours audio/month, 1 concurrent request
    • Computer Vision: 5,000 transactions/month

STEP 1: CREATE AZURE ACCOUNT
-----------------------------
  1. Go to: https://portal.azure.com
  2. Click "Sign in" (or "Start free" for new accounts)
  3. Complete account setup (credit card required)

STEP 2: CREATE RESOURCE GROUP
------------------------------
  1. In Azure Portal, search for "Resource groups"
  2. Click "+ Create"
  3. Subscription: Select your subscription
  4. Resource group name: "tjbot-resources"
  5. Region: Choose closest to you (e.g., "East US")
  6. Click "Review + create" → "Create"

"""
        
        for service_key in services:
            service = self.AZURE_SERVICES.get(service_key)
            if service:
                instructions += f"""
STEP 3: CREATE {service['name'].upper()}
{'-' * 60}
  1. In Azure Portal, search for "Cognitive Services"
  2. Click "+ Create"
  3. Click "{service['resource_type']}"
  
  4. Fill in details:
     • Subscription: Your subscription
     • Resource group: tjbot-resources
     • Region: Same as resource group
     • Name: tjbot-{service_key}
     • Pricing tier: "Free F0" (if available, otherwise "Standard S0")
  
  5. Click "Review + create" → "Create"
  6. Wait for deployment to complete
  
  7. Click "Go to resource"
  8. In left menu, click "Keys and Endpoint"
  9. You'll see:
     • KEY 1: (click "Show" to reveal)
     • KEY 2: (backup key)
     • Endpoint: (service URL)
  
  10. Copy KEY 1 and Endpoint - you'll enter them shortly

"""
        
        instructions += """
Press Enter when ready to enter your credentials...
"""
        return instructions
    
    def collect_credentials(self, services: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Interactively collect credentials for services.
        
        Args:
            services: List of service keys to configure
        
        Returns:
            Dictionary mapping service keys to {'key': ..., 'endpoint': ..., 'region': ...}
        """
        credentials = {}
        
        print("\n" + "=" * 70)
        print("CREDENTIAL ENTRY")
        print("=" * 70)
        
        for service_key in services:
            service = self.AZURE_SERVICES.get(service_key)
            if not service:
                continue
            
            print(f"\n📝 {service['name']}")
            print("-" * 70)
            
            # Get key (hidden input)
            key = getpass.getpass(f"Subscription Key (KEY 1, input hidden): ").strip()
            
            # Get endpoint
            endpoint = input(f"Endpoint URL: ").strip()
            
            # Parse region from endpoint if possible
            region = 'eastus'  # default
            if endpoint:
                for region_code in self.REGIONS.keys():
                    if region_code in endpoint.lower():
                        region = region_code
                        break
            
            credentials[service_key] = {
                'key': key,
                'endpoint': endpoint,
                'region': region
            }
            
            print(f"✓ {service['name']} credentials entered")
        
        return credentials
    
    def write_credentials(self, credentials: Dict[str, Dict[str, str]]) -> bool:
        """
        Write credentials to azure-credentials.env file.
        
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
            "# Microsoft Azure Cognitive Services Credentials for TJBot",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "#",
            "# These credentials are used by TJBot to access Azure AI services.",
            "# Keep this file secure and do not share it publicly.",
            "",
        ]
        
        for service_key, creds in credentials.items():
            service = self.AZURE_SERVICES.get(service_key)
            if service:
                lines.append(f"# {service['name']}")
                lines.append(f"{service['env_prefix']}_KEY={creds['key']}")
                lines.append(f"{service['env_prefix']}_REGION={creds['region']}")
                if creds.get('endpoint'):
                    lines.append(f"{service['env_prefix']}_ENDPOINT={creds['endpoint']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def run(self, services: List[str]) -> bool:
        """
        Run the complete Azure credential wizard.
        
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


def run_azure_wizard(config_dir: Path, services: List[str]) -> bool:
    """
    Convenience function to run Azure wizard.
    
    Args:
        config_dir: Path to ~/.tjbot directory
        services: List of services to configure
    
    Returns:
        True if successful
    """
    wizard = AzureWizard(config_dir)
    return wizard.run(services)
