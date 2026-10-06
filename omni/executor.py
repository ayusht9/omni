import os
import subprocess
import tempfile
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

console = Console()

def execute_native(command: str):
    """Executes native shell commands and permanently syncs the directory state."""
    if not command.strip():
        return
        
    cwd_file = os.path.join(tempfile.gettempdir(), 'omni_cwd.txt')
    
    # We append a hidden command to PowerShell to save its final working directory.
    # This ensures that whether you use 'cd', 'D:', or 'Set-Location' natively or via AI, Python always syncs up.
    ps_command = f"{command} ; (Get-Location).Path | Out-File -FilePath '{cwd_file}' -Encoding utf8"
    
    try:
        # Run through PowerShell for native Windows experience, allowing live streaming
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            console.print(f"[bold red]{result.stderr}[/bold red]", end='')
            
        # Sync Python's working directory with PowerShell's final directory
        if os.path.exists(cwd_file):
            with open(cwd_file, 'r', encoding='utf-8') as f:
                # Out-File with utf8 adds BOM, so strip it along with whitespace
                new_cwd = f.read().strip('\ufeff \n\r')
                if new_cwd and os.path.exists(new_cwd):
                    os.chdir(new_cwd)
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
