"""
Google Cloud Platform credential wizard.

Guides users through obtaining and configuring Google Cloud service credentials.
"""

from typing import Dict
from pathlib import Path
import json
import shutil


class GoogleCloudWizard:
    """Interactive wizard for Google Cloud Platform services setup."""
    
    def __init__(self, config_dir: Path):
        """
        Initialize Google Cloud wizard.
        
        Args:
            config_dir: Path to ~/.tjbot directory
        """
        self.config_dir = config_dir
        self.credentials_path = config_dir / 'google-credentials.json'
    
    def get_instructions(self) -> str:
        """Get step-by-step instructions for obtaining credentials."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║          GOOGLE CLOUD PLATFORM SERVICES SETUP                     ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: Google Cloud requires a credit card even for free tier.
    However, you WON'T be charged if you stay within free tier limits:
    • Speech-to-Text: 60 minutes/month free
    • Text-to-Speech: 1M standard characters/month free
    • Cloud Vision: 1,000 units/month free

STEP 1: CREATE GOOGLE CLOUD ACCOUNT
------------------------------------
  1. Go to: https://console.cloud.google.com
  2. Sign in with your Google account
  3. Accept terms of service
  4. Set up billing (credit card required but not charged within free tier)

STEP 2: CREATE A PROJECT
-------------------------
  1. In Google Cloud Console, click the project dropdown (top left)
  2. Click "New Project"
  3. Name it "tjbot" (or any name you prefer)
  4. Click "Create"
  5. Wait for project creation, then select it

STEP 3: ENABLE APIs
--------------------
  1. Go to: https://console.cloud.google.com/apis/library
  2. Search for and enable each API you need:
     • "Cloud Speech-to-Text API" → Click "Enable"
     • "Cloud Text-to-Speech API" → Click "Enable"
     • "Cloud Vision API" → Click "Enable"

STEP 4: CREATE SERVICE ACCOUNT
-------------------------------
  1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
  2. Click "+ CREATE SERVICE ACCOUNT"
  3. Service account name: "tjbot-services"
  4. Description: "TJBot AI services access"
  5. Click "CREATE AND CONTINUE"
  
  6. Grant roles (click "Select a role"):
     • Add "Cloud Speech Service Agent"
     • Add "Cloud Vision AI Service Agent"
     • Click "CONTINUE"
  
  7. Click "DONE"

STEP 5: CREATE AND DOWNLOAD KEY
--------------------------------
  1. Click on the service account you just created
  2. Go to "KEYS" tab
  3. Click "ADD KEY" → "Create new key"
  4. Select "JSON" format
  5. Click "CREATE"
  6. A JSON file will download - save it somewhere safe!

Press Enter when you have the JSON file ready...
"""
    
    def collect_credentials(self) -> Dict:
        """
        Interactively collect Google Cloud credentials.
        
        Returns:
            Credentials dictionary or None if cancelled
        """
        print("\n" + "=" * 70)
        print("CREDENTIAL ENTRY")
        print("=" * 70)
        print("\nYou can either:")
        print("  1. Provide the path to your downloaded JSON file")
        print("  2. Paste the JSON content directly")
        print()
        
        choice = input("Enter choice [1]: ").strip() or "1"
        
        if choice == "1":
            return self._load_from_file()
        else:
            return self._load_from_paste()
    
    def _load_from_file(self) -> Dict:
        """Load credentials from a file path."""
        while True:
            file_path = input("\nEnter path to JSON file: ").strip()
            
            # Expand user home directory
            file_path = Path(file_path).expanduser()
            
            if not file_path.exists():
                print(f"✗ File not found: {file_path}")
                retry = input("Try again? [Y/n]: ").strip().lower()
                if retry == 'n':
                    return None
                continue
            
            try:
                with open(file_path, 'r') as f:
                    creds = json.load(f)
                
                # Validate
                if self._validate_credentials_format(creds):
                    return creds
                else:
                    print("✗ Invalid credentials format")
                    return None
            
            except json.JSONDecodeError:
                print("✗ File is not valid JSON")
                return None
            except Exception as e:
                print(f"✗ Error reading file: {e}")
                return None
    
    def _load_from_paste(self) -> Dict:
        """Load credentials from pasted JSON content."""
        print("\nPaste JSON content (press Ctrl+D or Ctrl+Z when done):")
        print("-" * 70)
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        json_content = '\n'.join(lines)
        
        try:
            creds = json.loads(json_content)
            
            if self._validate_credentials_format(creds):
                return creds
            else:
                print("\n✗ Invalid credentials format")
                return None
        
        except json.JSONDecodeError:
            print("\n✗ Invalid JSON format")
            return None
    
    def _validate_credentials_format(self, creds: Dict) -> bool:
        """Validate that credentials have required fields."""
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        
        for field in required_fields:
            if field not in creds:
                print(f"✗ Missing required field: {field}")
                return False
        
        if creds.get('type') != 'service_account':
            print("✗ Credentials must be for a service account")
            return False
        
        print(f"✓ Credentials valid for project: {creds['project_id']}")
        return True
    
    def write_credentials(self, credentials: Dict) -> bool:
        """
        Write credentials to google-credentials.json file.
        
        Args:
            credentials: Credentials dictionary
        
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            with open(self.credentials_path, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Set secure permissions (owner read/write only)
            self.credentials_path.chmod(0o600)
            
            return True
        
        except Exception as e:
            print(f"Error writing credentials: {e}")
            return False
    
    def run(self) -> bool:
        """
        Run the complete Google Cloud credential wizard.
        
        Returns:
            True if credentials were successfully configured
        """
        # Show instructions
        instructions = self.get_instructions()
        print(instructions)
        input()  # Wait for user to press Enter
        
        # Collect credentials
        credentials = self.collect_credentials()
        
        if not credentials:
            print("\n✗ No credentials entered")
            return False
        
        # Write to file
        if self.write_credentials(credentials):
            print(f"\n✓ Credentials saved to: {self.credentials_path}")
            print(f"✓ Project: {credentials['project_id']}")
            print(f"✓ Service account: {credentials['client_email']}")
            return True
        else:
            return False


def run_google_wizard(config_dir: Path) -> bool:
    """
    Convenience function to run Google Cloud wizard.
    
    Args:
        config_dir: Path to ~/.tjbot directory
    
    Returns:
        True if successful
    """
    wizard = GoogleCloudWizard(config_dir)
    return wizard.run()
