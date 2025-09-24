#!/usr/bin/env python3
"""
Zsh Context Module - Provides zsh-specific information and history
"""

import os
import subprocess
from pathlib import Path

def get_zsh_context():
    """Get zsh-specific context information."""
    context = ""

    try:
        # Check if we're in zsh
        if not _is_zsh():
            return "- Nicht in zsh-Shell\n"

        context += "### Zsh Session Information\n"
        context += f"- **Shell**: zsh\n"
        context += f"- **History file**: {_get_history_file()}\n"
        context += f"- **History size**: {_get_history_size()}\n\n"

        # Get recent zsh history
        context += "### Recent Zsh Commands\n"
        history = _get_zsh_history()
        if history and not "Keine" in history:
            context += history
        else:
            context += "- Keine zsh-History verfügbar\n"

    except Exception as e:
        context += f"- Error getting zsh information: {e}\n"

    return context

def _is_zsh():
    """Check if current shell is zsh."""
    return 'zsh' in os.environ.get('SHELL', '').lower()

def _get_history_file():
    """Get zsh history file path."""
    histfile = os.environ.get('HISTFILE', '~/.zsh_history')
    return os.path.expanduser(histfile)

def _get_history_size():
    """Get zsh history size."""
    try:
        hist_size = os.environ.get('HISTSIZE', 'unknown')
        save_hist = os.environ.get('SAVEHIST', 'unknown')
        return f"HISTSIZE={hist_size}, SAVEHIST={save_hist}"
    except:
        return "unknown"

def _get_zsh_history():
    """Get recent zsh history using fc command."""
    try:
        # Use fc command to get recent history
        result = subprocess.run(
            ['zsh', '-c', 'fc -ln -30 2>/dev/null || echo "fc command failed"'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if lines and "fc command failed" not in lines[0]:
                return _format_zsh_history(lines)

        # Fallback: try to read history file directly
        return _read_zsh_history_file()

    except Exception as e:
        return f"- Fehler beim Lesen der zsh-History: {e}\n"

def _format_zsh_history(lines):
    """Format zsh history lines for display."""
    history_text = ""
    command_count = 0
    max_commands = 15

    for line in reversed(lines):
        line = line.strip()
        if line and command_count < max_commands:
            # Clean up zsh extended history format (timestamp:command)
            if ': ' in line:
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    line = parts[1]

            # Skip very trivial commands
            if line and len(line.strip()) > 2 and not any(skip in line.lower() for skip in ['pwd', 'ls']):
                history_text += f"- {line}\n"
                command_count += 1

    return history_text if history_text else "- Keine zsh-Befehle gefunden\n"

def _read_zsh_history_file():
    """Read zsh history file directly."""
    try:
        histfile = Path.home() / '.zsh_history'
        if histfile.exists():
            with open(histfile, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-30:]
                return _format_zsh_history(lines)
        else:
            return "- Zsh-History-Datei nicht gefunden\n"
    except Exception as e:
        return f"- Fehler beim Lesen der zsh-History-Datei: {e}\n"

if __name__ == "__main__":
    print(get_zsh_context())
