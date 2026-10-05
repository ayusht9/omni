from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from omni import config
from omni.executor import execute_native, execute_ai_command
from omni.llm import translate_to_shell
from rich.console import Console
import os

console = Console()

def main():
    # Load configuration
    config.load_omnirc()
    
    # Global Session History
    history_path = os.path.expanduser('~/.omni_history')
    session = PromptSession(history=FileHistory(history_path))
    console.print("[bold cyan]Welcome to Omni Shell![/bold cyan] Type 'exit' to quit.")

    while True:
        try:
            # Dynamic prompt showing current directory
            cwd = os.getcwd()
            folder_name = os.path.basename(cwd) or cwd
            
            # Interactive prompt
            user_input = session.prompt(f'omni {folder_name}❯ ')
            
            if user_input.strip().lower() in ['exit', 'quit']:
                break
                
            if not user_input.strip():
                continue
                
            input_lower = user_input.strip().lower()
            
            # Token-Free Built-in: history
            if input_lower == 'history':
                history_file = os.path.expanduser('~/.omni_history')
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines[-20:]): # Show last 20
                            console.print(f"[dim]{i+1}:[/dim] {line.strip()}")
                else:
                    console.print("[yellow]No history found yet.[/yellow]")
                continue
                
            # Token-Free Built-in: read
            if input_lower.startswith('read '):
                from omni.builtins import read_file
                filepath = user_input.strip()[5:].strip()
                read_file(filepath)
                continue
                
            # Token-Free Built-in: search
            if input_lower.startswith('search '):
                from omni.builtins import search_web
                query = user_input.strip()[7:].strip()
                search_web(query)
                continue
                
            # Route to AI if it starts with '?'
            if user_input.startswith('?'):
                ai_prompt = user_input[1:].strip()
                if ai_prompt:
                    shell_command = translate_to_shell(ai_prompt)
                    execute_ai_command(shell_command)
                else:
                    console.print("[yellow]Please ask a question after the '?'[/yellow]")
            else:
                # Execute natively
                execute_native(user_input)
            
        except KeyboardInterrupt:
            console.print("[yellow]^C[/yellow]")
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()
