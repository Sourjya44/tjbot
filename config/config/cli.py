"""
Command-line interface for TJBot configuration tool.

Provides commands: init, edit, validate, show, reset, backup
"""

import argparse
import sys
from pathlib import Path

from config import __version__
from config.config_loader import ConfigLoader
from config.config_writer import ConfigWriter
from config.schema_loader import ConfigSchemaError, load_config_schema
from config.validators import validate_config
from rich.console import Console

console = Console()

_CONFIG_DIR = Path.home() / '.tjbot'
_CONFIG_PATH = _CONFIG_DIR / 'tjbot.toml'


def cmd_init(args):
    """
    Create ~/.tjbot/tjbot.toml from the canonical upstream default.

    If the file already exists the user is prompted before overwriting.
    """
    from config.wizard import download_default_config

    if _CONFIG_PATH.exists():
        console.print(
            f'\n[yellow]Configuration already exists at {_CONFIG_PATH}[/yellow]\n')
        try:
            answer = input('Overwrite with a fresh default copy? [y/N] ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print('\n[yellow]Cancelled.[/yellow]\n')
            return 0
        if answer != 'y':
            console.print('[yellow]Keeping existing configuration.[/yellow]\n')
            return 0
        # Create a backup before overwriting
        writer = ConfigWriter()
        backup = writer.create_backup(_CONFIG_PATH)
        if backup:
            console.print(f'[dim]Backup saved to {backup}[/dim]\n')

    ok = download_default_config(_CONFIG_DIR, _CONFIG_PATH)
    return 0 if ok else 1


def cmd_edit(args):
    """
    Open the interactive hierarchical configuration editor.

    If ~/.tjbot/tjbot.toml does not yet exist, it is downloaded from the
    canonical upstream default first.
    """
    from config.wizard import ensure_config_exists, run_editor

    console.print()
    if not ensure_config_exists(_CONFIG_DIR, _CONFIG_PATH):
        console.print(
            '[red]Cannot open editor – no configuration file available.[/red]\n')
        return 1

    try:
        schema = load_config_schema(required=True)
    except ConfigSchemaError as exc:
        console.print(f'[red]Cannot open editor: {exc}[/red]\n')
        return 1

    return run_editor(_CONFIG_PATH, schema=schema)


def cmd_show(args):
    """Show current configuration."""
    console.print("\n[bold]Current TJBot Configuration[/bold]\n")

    loader = ConfigLoader()
    config_path = loader.get_user_config_path()

    if not config_path.exists():
        console.print(f"[yellow]No configuration file found[/yellow]")
        console.print(f"Run 'tjbot config init' to create one.\n")
        return 1

    try:
        console.print(f"[dim]Configuration loaded from: {config_path}[/dim]\n")
        console.print(config_path.read_text(encoding='utf-8'))

    except Exception as e:
        console.print(f"[red]Error reading configuration: {e}[/red]")
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


def cmd_validate(args):
    """Load and validate configuration."""
    console.print("\n[bold]Configuration Validation[/bold]\n")

    loader = ConfigLoader()

    if not loader.has_user_config():
        console.print(f"[yellow]No configuration file found[/yellow]")
        console.print(f"Run 'tjbot config init' to create one.\n")
        return 1

    try:
        schema = load_config_schema(required=True)
        console.print(f"[dim]Schema loaded from: {schema.path}[/dim]\n")

        config = loader.load_config()
        result = validate_config(config, schema=schema)

        if result.valid:
            console.print("[green]✓ Configuration is valid[/green]\n")
        else:
            console.print("[red]✗ Configuration has errors:[/red]")
            for error in result.errors:
                console.print(f"  [red]• {error}[/red]")
            console.print()

        if result.warnings:
            console.print("[yellow]⚠ Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]• {warning}[/yellow]")
            console.print()

        if result.suggestions:
            console.print("[cyan]ℹ Suggestions:[/cyan]")
            for suggestion in result.suggestions:
                console.print(f"  [cyan]• {suggestion}[/cyan]")
            console.print()

    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]\n")
        return 1

    return 0 if result.valid else 1


def main():
    """Main entry point for config CLI."""
    parser = argparse.ArgumentParser(
        description='TJBot Configuration Tool - Interactive hardware and service configuration',
        prog='config'
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init command
    subparsers.add_parser(
        'init',
        help='Download the default tjbot.toml to ~/.tjbot/ (prompts before overwriting)',
    )

    # edit command
    subparsers.add_parser(
        'edit',
        help='Open the interactive configuration editor (default when no subcommand given)',
    )

    # show command
    subparsers.add_parser('show', help='Show current configuration')

    # reset command
    parser_reset = subparsers.add_parser('reset', help='Reset configuration to defaults')
    parser_reset.add_argument('-y', '--yes', action='store_true', help='Skip confirmation prompt')

    # backup command
    subparsers.add_parser('backup', help='Create manual backup of configuration')

    # validate command
    subparsers.add_parser('validate', help='Validate configuration and report any issues')

    args = parser.parse_args()

    # Plain `tjbot config` (no subcommand) is a shortcut for `tjbot config edit`
    if not args.command:
        args.command = 'edit'

    # Route to appropriate command handler
    command_map = {
        'init': cmd_init,
        'edit': cmd_edit,
        'show': cmd_show,
        'reset': cmd_reset,
        'backup': cmd_backup,
        'validate': cmd_validate,
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
