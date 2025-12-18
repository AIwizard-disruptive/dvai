#!/usr/bin/env python3
"""
Bulk Logo Enrichment Script
Scrapes and caches logos for all portfolio companies
"""
import asyncio
import sys
from datetime import datetime
from supabase import create_client
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

# Add app to path
sys.path.insert(0, '.')

from app.config import settings
from app.services.company_enrichment import get_best_logo_url, get_company_name_from_domain

console = Console()


async def enrich_portfolio_companies(force_refresh: bool = False, limit: int = None):
    """
    Enrich all portfolio companies with logos.
    
    Args:
        force_refresh: Re-scrape even if logo exists
        limit: Max number of companies to process (for testing)
    """
    console.print("\n[bold blue]🎨 Company Logo Enrichment[/bold blue]\n")
    
    try:
        # Connect to Supabase
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all portfolio companies
        console.print("📊 Fetching portfolio companies...")
        companies_result = supabase.table('portfolio_companies').select('*').execute()
        companies = companies_result.data
        
        if limit:
            companies = companies[:limit]
        
        console.print(f"Found [bold]{len(companies)}[/bold] companies\n")
        
        # Stats
        enriched_count = 0
        skipped_count = 0
        failed_count = 0
        updated_companies = []
        
        # Process companies with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Processing companies...", total=len(companies))
            
            for company in companies:
                company_name = company.get('name', 'Unknown')
                progress.update(task, description=f"Processing {company_name[:30]}...")
                
                # Skip if already has a good logo (unless force refresh)
                existing_logo = company.get('logo_url', '')
                if existing_logo and not force_refresh:
                    # Skip if logo is not from Clearbit (meaning it's custom/scraped)
                    if 'clearbit.com' not in existing_logo:
                        skipped_count += 1
                        progress.advance(task)
                        continue
                
                # Get website
                website = company.get('website', '')
                if not website:
                    console.print(f"⚠️  {company_name}: No website")
                    skipped_count += 1
                    progress.advance(task)
                    continue
                
                # Extract domain from website
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
                
                try:
                    # Get best logo (Clearbit + scraping)
                    logo_url = await get_best_logo_url(domain, try_scraping=True)
                    
                    if logo_url:
                        # Update company with logo
                        supabase.table('portfolio_companies').update({
                            'logo_url': logo_url,
                            'updated_at': datetime.utcnow().isoformat()
                        }).eq('id', company['id']).execute()
                        
                        # Cache in logo_scrape_cache
                        cache_data = {
                            'domain': domain,
                            'logo_url': logo_url,
                            'company_name': company_name,
                            'scraped_at': datetime.utcnow().isoformat(),
                            'scrape_method': 'clearbit' if 'clearbit.com' in logo_url else 'scraped'
                        }
                        supabase.table('logo_scrape_cache').upsert(cache_data).execute()
                        
                        enriched_count += 1
                        updated_companies.append({
                            'name': company_name,
                            'domain': domain,
                            'logo': logo_url,
                            'method': cache_data['scrape_method']
                        })
                    else:
                        console.print(f"❌ {company_name}: Logo not found")
                        failed_count += 1
                        
                except Exception as e:
                    console.print(f"❌ {company_name}: Error - {str(e)[:50]}")
                    failed_count += 1
                
                progress.advance(task)
        
        # Summary
        console.print("\n[bold green]✅ Enrichment Complete![/bold green]\n")
        
        summary_table = Table(title="Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="magenta", justify="right")
        
        summary_table.add_row("Total Companies", str(len(companies)))
        summary_table.add_row("Enriched", str(enriched_count), style="green")
        summary_table.add_row("Skipped (already have logo)", str(skipped_count), style="yellow")
        summary_table.add_row("Failed", str(failed_count), style="red")
        
        console.print(summary_table)
        
        # Show some examples
        if updated_companies:
            console.print("\n[bold]Sample of Updated Companies:[/bold]")
            example_table = Table()
            example_table.add_column("Company", style="cyan")
            example_table.add_column("Domain", style="blue")
            example_table.add_column("Method", style="green")
            
            for company in updated_companies[:10]:
                example_table.add_row(
                    company['name'][:40],
                    company['domain'],
                    company['method']
                )
            
            console.print(example_table)
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}")
        raise


async def enrich_people_companies(force_refresh: bool = False):
    """
    Extract companies from people emails and enrich with logos.
    """
    console.print("\n[bold blue]👥 People Company Enrichment[/bold blue]\n")
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all people
        console.print("📊 Fetching people...")
        people_result = supabase.table('people').select('*').execute()
        people = people_result.data
        
        console.print(f"Found [bold]{len(people)}[/bold] people\n")
        
        # Extract unique company domains from emails
        from app.services.company_enrichment import extract_domain_from_email
        
        domains = set()
        for person in people:
            email = person.get('email', '')
            domain = extract_domain_from_email(email)
            if domain:
                domains.add(domain)
        
        console.print(f"Found [bold]{len(domains)}[/bold] unique company domains\n")
        
        # Enrich each domain
        enriched = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Processing domains...", total=len(domains))
            
            for domain in domains:
                progress.update(task, description=f"Processing {domain[:30]}...")
                
                try:
                    # Check cache first
                    if not force_refresh:
                        cached = supabase.table('logo_scrape_cache').select('*').eq('domain', domain).execute()
                        if cached.data:
                            progress.advance(task)
                            continue
                    
                    # Scrape logo
                    logo_url = await get_best_logo_url(domain, try_scraping=True)
                    
                    if logo_url:
                        # Cache result
                        cache_data = {
                            'domain': domain,
                            'logo_url': logo_url,
                            'company_name': get_company_name_from_domain(domain),
                            'scraped_at': datetime.utcnow().isoformat(),
                            'scrape_method': 'clearbit' if 'clearbit.com' in logo_url else 'scraped'
                        }
                        supabase.table('logo_scrape_cache').upsert(cache_data).execute()
                        enriched += 1
                        
                except Exception as e:
                    console.print(f"❌ {domain}: {str(e)[:50]}")
                
                progress.advance(task)
        
        console.print(f"\n[bold green]✅ Enriched {enriched} company logos from people data![/bold green]\n")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}")
        raise


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich company logos')
    parser.add_argument('--portfolio', action='store_true', help='Enrich portfolio companies')
    parser.add_argument('--people', action='store_true', help='Enrich companies from people emails')
    parser.add_argument('--all', action='store_true', help='Enrich both portfolio and people companies')
    parser.add_argument('--force', action='store_true', help='Force refresh existing logos')
    parser.add_argument('--limit', type=int, help='Limit number of companies to process (for testing)')
    
    args = parser.parse_args()
    
    if not (args.portfolio or args.people or args.all):
        console.print("[yellow]⚠️  Please specify --portfolio, --people, or --all[/yellow]")
        parser.print_help()
        sys.exit(1)
    
    async def main():
        if args.all or args.portfolio:
            await enrich_portfolio_companies(force_refresh=args.force, limit=args.limit)
        
        if args.all or args.people:
            await enrich_people_companies(force_refresh=args.force)
    
    asyncio.run(main())

