import os
from pathlib import Path

def load_omnirc():
    """Locates and executes commands from .omnirc on startup."""
    # Try local directory first, then home directory
    rc_path = Path('.omnirc')
    if not rc_path.exists():
        rc_path = Path.home() / '.omnirc'
    
    if rc_path.exists():
        print(f"[System] Loading config from {rc_path}")
        with open(rc_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Ignore empty lines and comments
                if line and not line.startswith('#'):
                    # For now we just print it. 
                    # Once we build the executor, this will actually run the commands!
                    print(f"[OmniRC] Executing: {line}")
    else:
        print("[System] No .omnirc found.")
