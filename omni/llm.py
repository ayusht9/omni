import os
import warnings
import json
from datetime import datetime
from google import genai
from rich.console import Console
from dotenv import load_dotenv

# Suppress google-genai SDK warnings so they don't clutter the terminal
warnings.filterwarnings("ignore", message="Direct use of automatic function calling")

load_dotenv()
console = Console()

# Global chat session to persist context across commands
_chat_session = None
_client = None

def get_chat_session():
    global _chat_session, _client
    if _chat_session is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
            
        # Store client globally so it doesn't get garbage collected and closed
        _client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are a command-line translation assistant for Windows PowerShell. "
            "The user will describe what they want to do in natural language, and your job is to translate it into a valid PowerShell command.\n\n"
            "RULES:\n"
            "1. ONLY output the raw PowerShell command.\n"
            "2. DO NOT wrap the command in markdown blocks (e.g. ```powershell ... ```).\n"
            "3. DO NOT output any conversational text, explanations, or warnings.\n"
            "4. If the user references past context (like 'go into it' or 'delete those files'), use this chat history to deduce the command."
        )
        
        # Initialize a persistent chat session instead of a stateless generate_content call
        _chat_session = _client.chats.create(
            model='gemini-3.5-flash-lite',
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
    return _chat_session

def _get_usage_file():
    from omni.config import get_omni_dir
    return get_omni_dir() / 'usage.json'

def record_usage(tokens: int):
    usage_file = _get_usage_file()
    today = datetime.now().strftime("%Y-%m-%d")
    data = {"date": today, "tokens": 0}
    
    if usage_file.exists():
        try:
            with open(usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("date") != today:
                data = {"date": today, "tokens": 0}
        except Exception:
            pass
            
    data["tokens"] += tokens
    
    with open(usage_file, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def get_battery_status():
    """Returns a formatted battery string based on a soft limit of 50,000 tokens per day."""
    usage_file = _get_usage_file()
    today = datetime.now().strftime("%Y-%m-%d")
    tokens = 0
    
    if usage_file.exists():
        try:
            with open(usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("date") == today:
                tokens = data.get("tokens", 0)
        except Exception:
            pass
            
    # Assuming a visual limit of 50,000 tokens for the battery gauge
    limit = 50000
    percent = max(0, 100 - int((tokens / limit) * 100))
    
    if percent > 75:
        icon = "🔋"
        color = "ansigreen"
    elif percent > 25:
        icon = "🪫"
        color = "ansiyellow"
    else:
        icon = "💀"
        color = "ansired"
        
    token_str = f"{tokens/1000:.1f}k" if tokens >= 1000 else str(tokens)
    return f" <{color}>{icon} {percent}% ({token_str})</{color}>"

def translate_to_shell(prompt: str) -> str:
    """Translates a natural language prompt into a PowerShell command using Gemini."""
    chat = get_chat_session()
    if not chat:
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY not found in .env")
        return ""
        
    try:
        console.print("[dim]Asking Gemini...[/dim]")
        
        # Send message to the persistent chat session
        response = chat.send_message(prompt)
        
        if not response.text:
            console.print("[bold red]Translation Error:[/bold red] Gemini returned an empty response. (The prompt might have been blocked by safety filters or it couldn't generate a command).")
            return ""
            
        # Track usage natively
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            tokens = getattr(response.usage_metadata, 'total_token_count', 0)
            if tokens:
                record_usage(tokens)
        
        # Strip any accidental markdown formatting
        command = response.text.strip()
        if command.startswith("```powershell"):
            command = command[13:]
        if command.startswith("```"):
            command = command[3:]
        if command.endswith("```"):
            command = command[:-3]
            
        return command.strip()
        
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
            console.print("[bold yellow]⚠️ Token Limit Reached:[/bold yellow] You have exhausted your Gemini API quota or hit the rate limit. Please wait a minute or check your API key tier.")
        else:
            console.print(f"[bold red]Translation Error:[/bold red] {e}")
        return ""
