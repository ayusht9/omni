import os
import subprocess
from rich.console import Console

console = Console()

def execute_native(command: str):
    """Executes native shell commands, handling built-ins like 'cd' properly."""
    parts = command.strip().split()
    if not parts:
        return
        
    cmd = parts[0].lower()

    # Handle internal 'cd' command because subprocess 'cd' doesn't persist
    if cmd == 'cd':
        try:
            target_dir = " ".join(parts[1:]) if len(parts) > 1 else os.path.expanduser('~')
            os.chdir(target_dir)
        except Exception as e:
            console.print(f"[bold red]cd error:[/bold red] {e}")
        return

    # Handle other native commands via powershell
    try:
        # Run through PowerShell for native Windows experience
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            console.print(f"[bold red]{result.stderr}[/bold red]", end='')
            
    except Exception as e:
        console.print(f"[bold red]Execution error:[/bold red] {e}")
