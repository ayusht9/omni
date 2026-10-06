import os
import time
import subprocess
import re
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion, PathCompleter, ExecutableCompleter
from omni import config
from omni.executor import execute_native, execute_ai_command
from omni.llm import translate_to_shell
from rich.console import Console

console = Console()

def get_git_branch():
    """Returns the current git branch formatted for the prompt, or empty string."""
    try:
        # Hide the console window on Windows if possible
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, startupinfo=startupinfo)
        branch = result.stdout.strip()
        if branch:
            return f" <ansimagenta>🌿 {branch}</ansimagenta>"
    except Exception:
        pass
    return ""

def get_python_env():
    """Returns the current active Python virtual environment formatted for the prompt."""
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        name = os.path.basename(venv)
        return f" <ansiyellow>🐍 {name}</ansiyellow>"
    return ""

class OmniCompleter(Completer):
    def __init__(self):
        self.path_completer = PathCompleter(expanduser=True)
        self.exec_completer = ExecutableCompleter()
        self.commands = ['search', 'read', 'history', 'exit', 'quit', 'cd']

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # If we are typing the very first word, suggest built-in commands AND native executables
        if ' ' not in text:
            for cmd in self.commands:
                if cmd.startswith(text.lower()):
                    yield Completion(cmd, start_position=-len(text))
            # Autocomplete all globally installed programs (git, python, npm, etc.)
            yield from self.exec_completer.get_completions(document, complete_event)
                    
        # Always suggest file/directory paths
        yield from self.path_completer.get_completions(document, complete_event)

def main():
    # Ensure ~/.omni directory exists
    omni_dir = config.get_omni_dir()

    # Load configuration
    config.load_omnirc()
    
    # Global Session History & Autocomplete
    history_path = str(omni_dir / 'history')
    session = PromptSession(
        history=FileHistory(history_path),
        completer=OmniCompleter(),
        complete_while_typing=False
    )
    
    console.print("\n[bold magenta]✨ Welcome to Omni Shell ✨[/bold magenta]")
    console.print("[dim]Type 'exit' to quit or use '?' for AI translations.[/dim]\n")

    last_execution_time = 0.0

    while True:
        try:
            # Dynamic prompt showing current directory
            cwd = os.getcwd()
            folder_name = os.path.basename(cwd) or cwd
            
            # Format elapsed time for ZSH-style output
            elapsed_str = f" ⏱️ {last_execution_time:.2f}s " if last_execution_time > 0 else ""
            
            git_str = get_git_branch()
            venv_str = get_python_env()
            
            # Multiline ZSH-style beautiful prompt with Nerd Font icons
            prompt_html = HTML(
                f'<ansiblue>╭─</ansiblue> <ansicyan>🌌 Omni</ansicyan> <ansiblue>📂 {folder_name}</ansiblue>{git_str}{venv_str}<ansiyellow>{elapsed_str}</ansiyellow>\n'
                f'<ansiblue>╰─</ansiblue><ansigreen>⚡ </ansigreen>'
            )
            
            # Interactive prompt
            user_input = session.prompt(prompt_html)
            
            if user_input.strip().lower() in ['exit', 'quit']:
                console.print("[bold magenta]👋 Goodbye![/bold magenta]")
                break
                
            if not user_input.strip():
                last_execution_time = 0.0
                continue
                
            input_lower = user_input.strip().lower()
            
            # Start timer
            start_time = time.time()
            
            # Token-Free Built-in: history
            if re.match(r'^history[:]?\s*$', user_input, re.IGNORECASE):
                history_file = str(config.get_omni_dir() / 'history')
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines[-20:]): # Show last 20
                            console.print(f"[dim]{i+1}:[/dim] {line.strip()}")
                else:
                    console.print("[yellow]No history found yet.[/yellow]")
                last_execution_time = time.time() - start_time
                continue
                
            # Token-Free Built-in: read
            read_match = re.match(r'^read[:]?\s+(.*)', user_input, re.IGNORECASE)
            if read_match:
                from omni.builtins import read_file
                filepath = read_match.group(1).strip()
                read_file(filepath)
                last_execution_time = time.time() - start_time
                continue
                
            # Token-Free Built-in: search
            search_match = re.match(r'^search[:]?\s+(.*)', user_input, re.IGNORECASE)
            if search_match:
                from omni.builtins import search_web
                query = search_match.group(1).strip()
                search_web(query)
                last_execution_time = time.time() - start_time
                continue
                
            # Route to AI if it starts with '?'
            if user_input.strip().startswith('?'):
                # Strip the prefix robustly
                ai_prompt = user_input.strip()[1:].strip()
                if ai_prompt.startswith(':'):
                    ai_prompt = ai_prompt[1:].strip()
                if ai_prompt:
                    shell_command = translate_to_shell(ai_prompt)
                    execute_ai_command(shell_command)
                else:
                    console.print("[yellow]Please ask a question after the '?'[/yellow]")
            else:
                # Execute natively
                execute_native(user_input)
                
            # Stop timer
            last_execution_time = time.time() - start_time
            
        except KeyboardInterrupt:
            console.print("[yellow]^C[/yellow]")
            last_execution_time = 0.0
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()
