#!/usr/bin/env python3
"""
System Info Context Module - Provides system information for the AI
"""

import platform
import os
import socket

def get_system_info():
    """Generate system information for context."""
    return f"""
# System Information

## Operating System
- **OS**: {platform.system()} {platform.release()}
- **Version**: {platform.version()}
- **Architecture**: {platform.machine()}

## Python Environment
- **Python Version**: {platform.python_version()}
- **User**: {os.getenv('USER', 'unknown')}
- **Hostname**: {socket.gethostname()}

## Environment Variables
- **HOME**: {os.getenv('HOME', 'not set')}
- **PATH**: Available (length: {len(os.getenv('PATH', ''))} chars)
- **SHELL**: {os.getenv('SHELL', 'not set')}

## Current Working Directory
- **PWD**: {os.getcwd()}

Use this system information to provide relevant, contextual responses.
"""

if __name__ == "__main__":
    print(get_system_info())
