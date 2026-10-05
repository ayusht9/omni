import os
import subprocess
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

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

def execute_ai_command(command_str: str):
    """Safely previews an AI-generated command and asks for confirmation before executing."""
    if not command_str:
        return
        
    # Beautifully syntax-highlight the generated code
    syntax = Syntax(command_str, "powershell", theme="monokai", line_numbers=False, word_wrap=True)
    
    print("\n")
    console.print("[bold yellow]⚡ Omni AI suggests the following command:[/bold yellow]")
    console.print(syntax)
    print("")
    
    # Safety Check Prompt
    is_confirmed = Confirm.ask("Execute this command?")
    if is_confirmed:
        console.print("[bold green]Executing...[/bold green]")
        execute_native(command_str)
    else:
        console.print("[bold red]Aborted.[/bold red]")
