from duckduckgo_search import DDGS
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import os

console = Console()

def search_web(query: str):
    """Searches the web using DuckDuckGo and prints results in a rich table."""
    console.print(f"[dim]Searching the web for: '{query}'...[/dim]")
    try:
        # DDGS().text() returns a generator, so we convert to a list of max 5 items
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        table = Table(title=f"Search Results for '{query}'", show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan", max_width=30, overflow="fold")
        table.add_column("Snippet", style="white", overflow="fold")
        table.add_column("Link", style="blue", max_width=40, overflow="fold")

        for res in results:
            table.add_row(res.get('title', ''), res.get('body', ''), res.get('href', ''))

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Search Error:[/bold red] {e}")

def read_file(filepath: str):
    """Reads a file and prints it with syntax highlighting."""
    if not os.path.exists(filepath):
        console.print(f"[bold red]Error:[/bold red] File '{filepath}' does not exist.")
        return
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
            
        # Simple extension matching
        ext = os.path.splitext(filepath)[1].lower().replace('.', '')
        lang_map = {
            'py': 'python', 'js': 'javascript', 'html': 'html', 'css': 'css',
            'json': 'json', 'md': 'markdown', 'txt': 'text', 'ps1': 'powershell',
            'sh': 'bash'
        }
        lang = lang_map.get(ext, 'text')
        
        syntax = Syntax(code, lang, theme="monokai", line_numbers=True, word_wrap=True)
        console.print(f"\n[bold cyan]--- {filepath} ---[/bold cyan]")
        console.print(syntax)
        print("")
    except Exception as e:
        console.print(f"[bold red]Read Error:[/bold red] {e}")
