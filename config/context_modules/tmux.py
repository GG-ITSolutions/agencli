#!/usr/bin/env python3
"""
Tmux Context Module - Provides tmux session and pane information
"""

import os
import subprocess
from pathlib import Path

def get_tmux_context():
    """Get comprehensive tmux session context information."""
    context = ""

    try:
        if not _is_in_tmux():
            return "- Nicht in einer tmux-Session\n"

        context += "### Tmux Session Information\n"
        context += f"- **Session Name**: {_get_tmux_session_name()}\n"
        context += f"- **Window/Pane**: {_get_tmux_window_pane()}\n"
        context += f"- **Session Uptime**: {_get_session_uptime()}\n"
        context += f"- **Attached Clients**: {_get_attached_clients()}\n\n"

        # Add tmux configuration info
        context += "### Tmux Configuration\n"
        buffer_info = _get_buffer_info()
        if buffer_info:
            context += buffer_info + "\n\n"

        # Get current pane content
        context += "### Current Pane Content\n"
        pane_content = _get_pane_content()
        if pane_content:
            context += "```\n"
            context += pane_content
            context += "\n```\n\n"
        else:
            context += "- Pane content could not be captured\n\n"

        # Get window information
        context += "### Window Information\n"
        windows_info = _get_windows_info()
        if windows_info:
            context += windows_info + "\n\n"

        # Get pane layout
        context += "### Pane Layout\n"
        layout_info = _get_pane_layout()
        if layout_info:
            context += layout_info + "\n\n"

        # Add troubleshooting info
        context += "### Troubleshooting\n"
        context += "- If pane content is incomplete, check your tmux history-limit\n"
        context += "- Run: `tmux set-option -g history-limit 10000` for more history\n"
        context += "- Current pane content depends on tmux scrollback buffer\n"

    except Exception as e:
        context += f"- Error getting tmux information: {e}\n"

    return context

def _is_in_tmux():
    """Check if running inside tmux."""
    return 'TMUX' in os.environ

def _get_tmux_session_name():
    """Get current tmux session name."""
    try:
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#S'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except:
        return 'unknown'

def _get_tmux_window_pane():
    """Get current tmux window and pane info."""
    try:
        # Get window index
        window_result = subprocess.run(
            ['tmux', 'display-message', '-p', '#I'],
            capture_output=True,
            text=True,
            timeout=5
        )
        window = window_result.stdout.strip() if window_result.returncode == 0 else '?'

        # Get pane index
        pane_result = subprocess.run(
            ['tmux', 'display-message', '-p', '#P'],
            capture_output=True,
            text=True,
            timeout=5
        )
        pane = pane_result.stdout.strip() if pane_result.returncode == 0 else '?'

        return f"{window}:{pane}"
    except:
        return "?:?"

def _get_session_uptime():
    """Get session uptime information."""
    try:
        # Get session creation time
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#{session_created}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            import time
            created_time = int(result.stdout.strip())
            current_time = int(time.time())
            uptime_seconds = current_time - created_time

            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    except:
        pass
    return "unknown"

def _get_attached_clients():
    """Get number of attached clients."""
    try:
        result = subprocess.run(
            ['tmux', 'list-clients'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return str(len([line for line in lines if line.strip()]))
    except:
        pass
    return "unknown"

def _get_pane_content(capture_lines: int = 10000):
    try:
        result = subprocess.run(
            ['tmux', 'capture-pane', '-p', '-S', f'-{capture_lines}', '-E', f'{capture_lines}'],
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.returncode == 0 and result.stdout.strip():
            all_lines = result.stdout.strip().split('\n')
            total_lines = len(all_lines)

            if total_lines == 0:
                return "Tmux buffer appears to be empty"

            return f"[Complete buffer: {total_lines} lines]\n\n" + '\n'.join(all_lines)

    except Exception as e:
        return f"Error capturing tmux pane: {e}"

    return "No tmux pane content available"

def _get_windows_info():
    """Get information about all windows in session."""
    try:
        result = subprocess.run(
            ['tmux', 'list-windows', '-F', '#I: #W#F (#P panes)'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def _get_pane_layout():
    """Get pane layout information."""
    try:
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#{window_layout}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return f"Layout: {result.stdout.strip()}"
    except:
        pass
    return None

def _get_buffer_info():
    """Get tmux buffer and history configuration."""
    try:
        info = []

        # Get history limit
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#{history_limit}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            history_limit = result.stdout.strip()
            info.append(f"- **History Limit**: {history_limit} lines")

        # Get current pane size
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#{pane_width}x#{pane_height}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            pane_size = result.stdout.strip()
            info.append(f"- **Pane Size**: {pane_size}")

        # Get scroll position if available
        result = subprocess.run(
            ['tmux', 'display-message', '-p', '#{scroll_position}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            scroll_pos = result.stdout.strip()
            if scroll_pos != "0":
                info.append(f"- **Scroll Position**: {scroll_pos}")

        return '\n'.join(info) if info else None

    except Exception as e:
        return f"- Error getting buffer info: {e}"

if __name__ == "__main__":
    print(get_tmux_context())
