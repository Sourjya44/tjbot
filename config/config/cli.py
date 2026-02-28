"""
Command-line interface for TJBot configuration tool.

Provides commands: init, edit, validate, test, show, reset, backup, restore, export, import
"""

import argparse
import sys
from pathlib import Path

from config import __version__
from config.config_loader import ConfigLoader
from config.config_writer import ConfigWriter
from config.device_detection import get_system_info
from config.validators import validate_config
from config.credential_guides.validator import CredentialValidator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def _inquirer():
    """Lazy import inquirer for interactive commands."""
    import inquirer
    return inquirer


def _build_editor_wizard():
    """Create and initialize wizard instance for advanced editing."""
    from config.wizard import InitWizard

    wizard = InitWizard()
    wizard._load_existing_config()
    wizard.config = dict(wizard.existing_config) if wizard.existing_config else {}
    wizard.system_info = get_system_info()
    return wizard

def _edit_listen_configuration(wizard):
    """Edit microphone and STT configuration."""
    wizard.config.setdefault('hardware', {})['microphone'] = True
    wizard._configure_microphone()
    wizard._configure_listen_backend()


def _edit_see_configuration(wizard):
    """Edit camera and vision configuration."""
    wizard.config.setdefault('hardware', {})['camera'] = True
    wizard._configure_camera()
    wizard._configure_see_backend()


def _edit_shine_configuration(wizard):
    """Edit LED configuration."""
    inquirer = _inquirer()
    questions = [
        inquirer.List(
            'led_type',
            message='Select LED configuration to edit',
            choices=[
                ('NeoPixel LED', 'neopixel'),
                ('Common Anode RGB LED', 'common_anode'),
            ],
            default='neopixel'
        )
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return

    wizard.config.setdefault('hardware', {})['led_neopixel'] = answers['led_type'] == 'neopixel'
    wizard.config['hardware']['led_common_anode'] = answers['led_type'] == 'common_anode'

    if answers['led_type'] == 'neopixel':
        wizard._configure_neopixel()
    else:
        wizard._configure_common_anode()


def _edit_speak_configuration(wizard):
    """Edit speaker and TTS configuration."""
    wizard.config.setdefault('hardware', {})['speaker'] = True
    wizard._configure_speaker()
    wizard._configure_speak_backend()


def _edit_wave_configuration(wizard):
    """Edit servo configuration."""
    wizard.config.setdefault('hardware', {})['servo'] = True
    wizard._configure_servo()


def _run_advanced_editor():
    """Run interactive advanced editor with hierarchical section list."""
    inquirer = _inquirer()
    wizard = _build_editor_wizard()

    while True:
        questions = [
            inquirer.List(
                'section',
                message='Select configuration section to edit',
                choices=[
                    ('Logging mode', 'logging'),
                    ('Hardware configuration', 'hardware'),
                    ('Listen configuration (Microphone + Speech-to-Text)', 'listen'),
                    ('See configuration (Camera + Vision)', 'see'),
                    ('Shine configuration (LED)', 'shine'),
                    ('Speak configuration (Speaker + Text-to-Speech)', 'speak'),
                    ('Wave configuration (Servo)', 'wave'),
                    ('💾 Save and exit', 'save'),
                    ('🚪 Exit without saving', 'exit'),
                ],
                default='logging'
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:
            return 130

        section = answers['section']

        if section == 'logging':
            wizard._configure_logging()
        elif section == 'hardware':
            wizard._configure_hardware()
        elif section == 'listen':
            _edit_listen_configuration(wizard)
        elif section == 'see':
            _edit_see_configuration(wizard)
        elif section == 'shine':
            _edit_shine_configuration(wizard)
        elif section == 'speak':
            _edit_speak_configuration(wizard)
        elif section == 'wave':
            _edit_wave_configuration(wizard)
        elif section == 'save':
            writer = ConfigWriter()
            if writer.write_config(wizard.config, add_comments=True, create_backup=True):
                console.print("\n[green]✓ Configuration saved[/green]\n")
                return 0
            console.print("\n[red]✗ Failed to save configuration[/red]\n")
            return 1
        elif section == 'exit':
            console.print("\n[yellow]No changes saved[/yellow]\n")
            return 0


def cmd_init(args):
    """Run initialization wizard."""
    from config.wizard import run_init_wizard

    try:
        success = run_init_wizard()
        return 0 if success else 1
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        return 1


def cmd_edit(args):
    """Run advanced editor."""
    console.print("\n[bold yellow]TJBot Configuration Editor[/bold yellow]\n")
    return _run_advanced_editor()


def cmd_validate(args):
    """Validate configuration and credentials."""
    console.print("\n[bold]Validating TJBot Configuration[/bold]\n")

    loader = ConfigLoader()
    config_dir = loader.get_config_dir()

    # Check if config exists
    if not loader.has_user_config():
        console.print(f"[yellow]! No configuration file found at {loader.get_user_config_path()}[/yellow]")
        console.print(f"[yellow]  Run 'config init' to create one.[/yellow]\n")
        return 1

    # Load and validate config
    try:
        config = loader.load_config()
        result = validate_config(config)

        if result.valid:
            console.print("[green]✓ Configuration is valid[/green]")
        else:
            console.print("[red]✗ Configuration has errors:[/red]")
            for error in result.errors:
                console.print(f"  [red]• {error}[/red]")

        if result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]• {warning}[/yellow]")

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        return 1

    # Validate credentials
    console.print("\n[bold]Validating Credentials[/bold]\n")

    validator = CredentialValidator()
    cred_results = validator.test_all_credentials(config_dir)

    if not cred_results:
        console.print("[yellow]No credential files found[/yellow]")
    else:
        table = Table()
        table.add_column("Service", style="cyan")
        table.add_column("Status")

        for service, (success, message) in cred_results.items():
            status_style = "green" if success else "red"
            table.add_row(service, f"[{status_style}]{message}[/{status_style}]")

        console.print(table)

    console.print()
    return 0 if result.valid else 1


def cmd_show(args):
    """Show current configuration."""
    console.print("\n[bold]Current TJBot Configuration[/bold]\n")

    loader = ConfigLoader()

    if not loader.has_user_config():
        console.print(f"[yellow]No configuration file found[/yellow]")
        console.print(f"Run 'config init' to create one.\n")
        return 1

    try:
        config = loader.load_config()

        # Print configuration in readable format
        import tomlkit
        console.print(f"[dim]Configuration loaded from: {loader.get_user_config_path()}[/dim]\n")
        console.print(tomlkit.dumps(config))

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        return 1

    return 0


def cmd_reset(args):
    """Reset configuration to defaults."""
    console.print("\n[bold red]Reset Configuration[/bold red]\n")
    console.print("[yellow]This will delete your current configuration![/yellow]")

    loader = ConfigLoader()
    config_path = loader.get_user_config_path()

    if not config_path.exists():
        console.print("[yellow]No configuration file to reset.[/yellow]\n")
        return 0

    if not args.yes:
        confirm = input("Are you sure? [y/N]: ").strip().lower()
        if confirm != 'y':
            console.print("[yellow]Reset cancelled.[/yellow]\n")
            return 0

    try:
        # Create backup first
        writer = ConfigWriter()
        backup_path = writer.create_backup()
        if backup_path:
            console.print(f"[green]✓ Backup created: {backup_path}[/green]")

        # Delete config file
        config_path.unlink()
        console.print(f"[green]✓ Configuration reset[/green]\n")

    except Exception as e:
        console.print(f"[red]Error resetting configuration: {e}[/red]")
        return 1

    return 0


def cmd_backup(args):
    """Create manual backup of configuration."""
    console.print("\n[bold]Backup Configuration[/bold]\n")

    writer = ConfigWriter()
    backup_path = writer.create_backup()

    if backup_path:
        console.print(f"[green]✓ Backup created: {backup_path}[/green]\n")
        return 0
    else:
        console.print("[yellow]No configuration file to backup[/yellow]\n")
        return 1


def cmd_test(args):
    """Run hardware tests."""
    console.print("\n[bold]Hardware Tests[/bold]\n")
    console.print("[yellow]Test integration coming soon...[/yellow]")
    console.print("\nFor now, you can run tests manually from the tests/ directory:\n")
    console.print("  cd ~/Desktop/tjbot/tests")
    console.print("  node test.speaker.js")
    console.print("  node test.microphone.js")
    console.print("  node test.led.js\n")

    return 0


def main():
    """Main entry point for config CLI."""
    parser = argparse.ArgumentParser(
        description='TJBot Configuration Tool - Interactive hardware and service configuration',
        prog='config'
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init command
    subparsers.add_parser('init', help='Run initialization wizard (beginner mode)')

    # edit command
    subparsers.add_parser('edit', help='Run advanced configuration editor')

    # validate command
    subparsers.add_parser('validate', help='Validate configuration and credentials')

    # show command
    subparsers.add_parser('show', help='Show current configuration')

    # reset command
    parser_reset = subparsers.add_parser('reset', help='Reset configuration to defaults')
    parser_reset.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')

    # backup command
    subparsers.add_parser('backup', help='Create manual backup of configuration')

    # test command
    parser_test = subparsers.add_parser('test', help='Run hardware tests')
    parser_test.add_argument('device', nargs='?', default='all',
                            choices=['all', 'speaker', 'microphone', 'led', 'servo', 'camera'],
                            help='Device to test')

    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command handler
    command_map = {
        'init': cmd_init,
        'edit': cmd_edit,
        'validate': cmd_validate,
        'show': cmd_show,
        'reset': cmd_reset,
        'backup': cmd_backup,
        'test': cmd_test,
    }

    handler = command_map.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Operation cancelled by user[/yellow]\n")
            return 130
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")
            return 1
    else:
        console.print(f"[red]Unknown command: {args.command}[/red]")
        return 1


if __name__ == '__main__':
    sys.exit(main())
