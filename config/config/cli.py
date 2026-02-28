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
    console.print("[yellow]Interactive editor implementation in progress...[/yellow]")
    console.print("\nFor now, you can edit the configuration file directly:")

    loader = ConfigLoader()
    config_path = loader.get_user_config_path()
    console.print(f"  {config_path}\n")

    if config_path.exists():
        console.print(f"[green]✓ Configuration file exists[/green]")
    else:
        console.print(f"[yellow]! Configuration file does not exist. Run 'config init' first.[/yellow]")

    return 0


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
