from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

def main():
    # Session with file history
    session = PromptSession(history=FileHistory('.omni_history'))
    print("Welcome to Omni Shell! Type 'exit' to quit.")

    while True:
        try:
            # Interactive prompt
            user_input = session.prompt('omni❯ ')
            
            if user_input.strip().lower() in ['exit', 'quit']:
                break
                
            if not user_input.strip():
                continue
                
            print(f"You typed: {user_input}")
            # Later: LLM integration and fallback logic will go here
            
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == '__main__':
    main()
