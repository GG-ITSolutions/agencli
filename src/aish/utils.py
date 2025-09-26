import os
import subprocess
import tempfile
from contextlib import contextmanager


@contextmanager
def script_capture(command):
    """Context manager for TTY-preserving command execution with output capture"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.script', delete=False) as script_file:
        script_filename = script_file.name
    
    try:
        subprocess.run(['script', '-q', '-e', '-c', command, script_filename], 
                      capture_output=False, text=True)
        
        try:
            with open(script_filename, 'r', encoding='utf-8', errors='ignore') as f:
                raw_output = f.read()
            yield _clean_script_output(raw_output)
        except:
            yield ""
    finally:
        try:
            os.unlink(script_filename)
        except:
            pass


def _clean_script_output(raw_output):
    """Clean script output for storage (remove control sequences)"""
    if not raw_output:
        return ""
    
    lines = raw_output.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    return '\n'.join(line.rstrip() for line in lines 
                    if line.strip() and not line.startswith('\x1b['))
