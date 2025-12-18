#!/usr/bin/env python
"""
Bulk upload Word documents for processing.

Usage:
    python scripts/bulk_upload.py /path/to/word/files/*.docx

Or upload entire directory:
    python scripts/bulk_upload.py /path/to/word/files/
"""
import asyncio
import sys
import os
import glob
from pathlib import Path
from typing import List
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

console = Console()


class BulkUploader:
    """Bulk upload Word documents to the API."""
    
    def __init__(self, api_url: str, token: str, org_id: str):
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.org_id = org_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-Org-Id": org_id,
        }
    
    async def upload_file(self, file_path: Path) -> dict:
        """Upload a single file."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(file_path, 'rb') as f:
                    files = {"file": (file_path.name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                    response = await client.post(
                        f"{self.api_url}/artifacts/upload",
                        headers=self.headers,
                        files=files,
                    )
                    response.raise_for_status()
                    return {
                        "status": "success",
                        "data": response.json(),
                        "file": file_path.name,
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file": file_path.name,
            }
    
    async def upload_files(self, file_paths: List[Path]) -> List[dict]:
        """Upload multiple files with progress bar."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Uploading files...", 
                total=len(file_paths)
            )
            
            for file_path in file_paths:
                progress.update(task, description=f"[cyan]Uploading {file_path.name}...")
                result = await self.upload_file(file_path)
                results.append(result)
                progress.advance(task)
        
        return results
    
    def print_results(self, results: List[dict]):
        """Print upload results in a nice table."""
        # Summary
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        
        console.print()
        console.print(f"[bold green]✓ Uploaded:[/bold green] {success_count}/{len(results)}")
        if error_count > 0:
            console.print(f"[bold red]✗ Failed:[/bold red] {error_count}/{len(results)}")
        
        # Detailed table
        table = Table(title="\nUpload Results")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")
        
        for result in results:
            if result["status"] == "success":
                artifact_id = result["data"].get("id", "N/A")
                table.add_row(
                    result["file"],
                    "✓ Success",
                    f"ID: {artifact_id[:8]}..."
                )
            else:
                table.add_row(
                    result["file"],
                    "✗ Error",
                    result["error"][:50]
                )
        
        console.print(table)


def find_word_files(path_arg: str) -> List[Path]:
    """Find all Word files in the given path."""
    path = Path(path_arg)
    
    if path.is_file():
        # Single file
        return [path]
    elif path.is_dir():
        # Directory - find all .docx files
        return list(path.glob("*.docx")) + list(path.glob("*.doc"))
    else:
        # Glob pattern
        return [Path(p) for p in glob.glob(path_arg)]


async def main():
    """Main function."""
    console.print("[bold blue]Meeting Intelligence - Bulk Upload Tool[/bold blue]")
    console.print()
    
    # Get path from command line
    if len(sys.argv) < 2:
        console.print("[red]Error: Please provide a path to Word files[/red]")
        console.print()
        console.print("Usage:")
        console.print("  python scripts/bulk_upload.py /path/to/files/*.docx")
        console.print("  python scripts/bulk_upload.py /path/to/files/")
        console.print()
        sys.exit(1)
    
    path_arg = sys.argv[1]
    
    # Find files
    files = find_word_files(path_arg)
    
    if not files:
        console.print(f"[red]Error: No Word files found in {path_arg}[/red]")
        sys.exit(1)
    
    console.print(f"[green]Found {len(files)} Word file(s)[/green]")
    console.print()
    
    # Get configuration
    api_url = os.getenv("API_URL", "http://localhost:8000")
    token = os.getenv("SUPABASE_TOKEN")
    org_id = os.getenv("ORG_ID")
    
    if not token:
        console.print("[yellow]Warning: SUPABASE_TOKEN not set[/yellow]")
        console.print("Please set your Supabase auth token:")
        console.print("  export SUPABASE_TOKEN='your-token-here'")
        console.print()
        
        # Prompt for token
        token = console.input("[cyan]Enter your auth token:[/cyan] ").strip()
        if not token:
            console.print("[red]Error: Token required[/red]")
            sys.exit(1)
    
    if not org_id:
        console.print("[yellow]Warning: ORG_ID not set[/yellow]")
        org_id = console.input("[cyan]Enter your organization ID:[/cyan] ").strip()
        if not org_id:
            console.print("[red]Error: Organization ID required[/red]")
            sys.exit(1)
    
    # Confirm
    console.print()
    console.print(f"[bold]Configuration:[/bold]")
    console.print(f"  API URL: {api_url}")
    console.print(f"  Org ID: {org_id}")
    console.print(f"  Files: {len(files)}")
    console.print()
    
    proceed = console.input("[cyan]Proceed with upload? (y/n):[/cyan] ").strip().lower()
    if proceed != 'y':
        console.print("[yellow]Upload cancelled[/yellow]")
        sys.exit(0)
    
    # Upload
    console.print()
    uploader = BulkUploader(api_url, token, org_id)
    results = await uploader.upload_files(files)
    
    # Print results
    uploader.print_results(results)
    
    # Next steps
    console.print()
    console.print("[bold green]Next Steps:[/bold green]")
    console.print("1. Files are being processed in the background (check Celery logs)")
    console.print("2. View meetings: curl http://localhost:8000/meetings")
    console.print("3. Check processing status in the dashboard")
    console.print()


if __name__ == "__main__":
    asyncio.run(main())





