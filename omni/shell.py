from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from omni import config
from omni.executor import execute_native
from rich.console import Console
import os

console = Console()

def main():
    # Load configuration
    config.load_omnirc()
    
    # Session with file history
    session = PromptSession(history=FileHistory('.omni_history'))
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
                
            # Execute natively
            execute_native(user_input)
            
        except KeyboardInterrupt:
            console.print("[yellow]^C[/yellow]")
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()
