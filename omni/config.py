import os
from pathlib import Path

def get_omni_dir() -> Path:
    """Returns the path to the ~/.omni directory, creating it if necessary."""
    omni_dir = Path.home() / '.omni'
    if not omni_dir.exists():
        omni_dir.mkdir(parents=True, exist_ok=True)
    return omni_dir

def load_omnirc():
    """Locates and executes commands from ~/.omni/omnirc or local .omnirc on startup."""
    omni_dir = get_omni_dir()
    global_rc = omni_dir / 'omnirc'
    local_rc = Path('.omnirc')
    
    # Prefer local config for project-specific overrides, fallback to global
    if local_rc.exists():
        target_rc = local_rc
    elif global_rc.exists():
        target_rc = global_rc
    else:
        # Create a default empty one so the user has it ready
        global_rc.touch()
        target_rc = global_rc
    
    if target_rc.exists():
        print(f"[System] Loading config from {target_rc}")
        with open(target_rc, 'r') as f:
            for line in f:
                line = line.strip()
                # Ignore empty lines and comments
                if line and not line.startswith('#'):
                    # For now we just print it. 
                    # Once we build the executor, this will actually run the commands!
                    print(f"[OmniRC] Executing: {line}")
