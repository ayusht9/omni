import os
import warnings
from google import genai
from rich.console import Console
from dotenv import load_dotenv

# Suppress google-genai SDK warnings so they don't clutter the terminal
warnings.filterwarnings("ignore", message="Direct use of automatic function calling")

load_dotenv()
console = Console()

def translate_to_shell(prompt: str) -> str:
    """Translates natural language into a Windows PowerShell command."""
    # Check for API key (loaded from .env usually, or system env)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY environment variable is not set.")
        console.print("Please set it in your .env file or system environment.")
        return ""
        
    try:
        console.print("[dim]Asking Gemini...[/dim]")
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are an expert Windows PowerShell assistant. "
            "The user will provide a natural language request. "
            "You must output ONLY the raw, executable PowerShell command that fulfills the request. "
            "Do NOT wrap the command in markdown blocks. Do NOT provide any explanation or conversational text. "
            "If the request spans multiple commands, separate them with a semicolon."
        )
        
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )
        
        return response.text.strip().replace("```powershell", "").replace("```", "").strip()
    except Exception as e:
        console.print(f"[bold red]LLM Error:[/bold red] {e}")
        return ""
