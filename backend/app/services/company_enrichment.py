"""
Company Enrichment Service
Extracts company domains from emails and fetches company logos and data.
Uses Clearbit Logo API + direct website scraping as fallback.
"""
import re
from typing import Optional, Dict, List
import httpx
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import base64


def extract_domain_from_email(email: str) -> Optional[str]:
    """
    Extract domain from email address.
    
    Examples:
        'john@acme.com' -> 'acme.com'
        'jane@startup.io' -> 'startup.io'
    """
    if not email or '@' not in email:
        return None
    
    try:
        domain = email.split('@')[1].lower().strip()
        # Remove common email providers
        excluded_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'me.com', 'aol.com', 'protonmail.com',
            'mail.com', 'live.com', 'msn.com'
        ]
        
        if domain in excluded_domains:
            return None
            
        return domain
    except Exception:
        return None


def get_company_logo_url(domain: str, size: int = 128) -> str:
    """
    Get company logo URL using Clearbit Logo API (free, no auth required).
    
    Args:
        domain: Company domain (e.g., 'stripe.com')
        size: Logo size in pixels (default 128)
    
    Returns:
        URL to company logo
    
    Examples:
        'stripe.com' -> 'https://logo.clearbit.com/stripe.com'
        'apple.com' -> 'https://logo.clearbit.com/apple.com'
    """
    if not domain:
        return ''
    
    # Clearbit Logo API - free tier, no authentication needed
    return f'https://logo.clearbit.com/{domain}?size={size}'


def get_company_name_from_domain(domain: str) -> str:
    """
    Extract company name from domain.
    
    Examples:
        'disruptiveventures.com' -> 'Disruptive Ventures'
        'stripe.com' -> 'Stripe'
        'my-startup.io' -> 'My Startup'
    """
    if not domain:
        return 'Unknown Company'
    
    # Remove TLD
    name = domain.split('.')[0]
    
    # Replace hyphens and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    
    # Capitalize each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name


async def enrich_company_from_email(email: str) -> Optional[Dict]:
    """
    Extract company information from email address.
    
    Args:
        email: Email address
    
    Returns:
        Dict with company info or None
        {
            'domain': 'stripe.com',
            'name': 'Stripe',
            'logo_url': 'https://logo.clearbit.com/stripe.com',
            'website': 'https://stripe.com'
        }
    """
    domain = extract_domain_from_email(email)
    
    if not domain:
        return None
    
    return {
        'domain': domain,
        'name': get_company_name_from_domain(domain),
        'logo_url': get_company_logo_url(domain),
        'website': f'https://{domain}'
    }


async def fetch_company_details_clearbit(domain: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Fetch detailed company information from Clearbit Company API (requires paid API key).
    
    Args:
        domain: Company domain
        api_key: Clearbit API key (optional, for enhanced data)
    
    Returns:
        Enhanced company data or None
    """
    if not api_key:
        # Return basic info without API
        return {
            'domain': domain,
            'name': get_company_name_from_domain(domain),
            'logo': get_company_logo_url(domain),
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://company.clearbit.com/v2/companies/find?domain={domain}',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'domain': domain,
                    'name': data.get('name', get_company_name_from_domain(domain)),
                    'logo': data.get('logo', get_company_logo_url(domain)),
                    'description': data.get('description'),
                    'industry': data.get('category', {}).get('industry'),
                    'employees': data.get('metrics', {}).get('employees'),
                    'founded': data.get('foundedYear'),
                    'location': data.get('location'),
                    'linkedin': data.get('linkedin', {}).get('handle'),
                    'twitter': data.get('twitter', {}).get('handle'),
                }
            else:
                # Fallback to basic info
                return {
                    'domain': domain,
                    'name': get_company_name_from_domain(domain),
                    'logo': get_company_logo_url(domain),
                }
    except Exception as e:
        print(f"Error fetching Clearbit data for {domain}: {e}")
        return {
            'domain': domain,
            'name': get_company_name_from_domain(domain),
            'logo': get_company_logo_url(domain),
        }


async def scrape_logo_from_website(domain: str, timeout: float = 10.0) -> Optional[str]:
    """
    Scrape company logo directly from their website.
    Tries multiple sources in order of preference:
    1. Apple touch icon (usually high quality)
    2. Open Graph image
    3. Standard favicon
    4. Any large icon in the page
    
    Args:
        domain: Company domain (e.g., 'stripe.com')
        timeout: Request timeout in seconds
    
    Returns:
        URL to logo or None if not found
    """
    if not domain:
        return None
    
    try:
        website_url = f'https://{domain}'
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                website_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                },
                timeout=timeout
            )
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Priority 1: Apple touch icon (usually high quality)
            apple_icon = soup.find('link', rel=lambda x: x and 'apple-touch-icon' in x.lower())
            if apple_icon and apple_icon.get('href'):
                return urljoin(website_url, apple_icon['href'])
            
            # Priority 2: Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                og_url = og_image['content']
                # Filter out social media placeholders
                if 'logo' in og_url.lower() or 'icon' in og_url.lower():
                    return urljoin(website_url, og_url)
            
            # Priority 3: Standard favicon with size hints
            large_icon = soup.find('link', rel='icon', sizes=lambda x: x and any(s in x for s in ['192', '256', '512']))
            if large_icon and large_icon.get('href'):
                return urljoin(website_url, large_icon['href'])
            
            # Priority 4: Any favicon
            favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if favicon and favicon.get('href'):
                return urljoin(website_url, favicon['href'])
            
            # Priority 5: Default favicon location
            return f'{website_url}/favicon.ico'
            
    except Exception as e:
        print(f"Error scraping logo from {domain}: {e}")
        return None


async def get_best_logo_url(domain: str, try_scraping: bool = True) -> Optional[str]:
    """
    Get the best available logo for a company.
    Tries Clearbit first (fast), then scrapes website if needed.
    
    Args:
        domain: Company domain
        try_scraping: Whether to try scraping if Clearbit fails
    
    Returns:
        URL to logo or None
    """
    if not domain:
        return None
    
    # Try Clearbit first (free, fast, no scraping needed)
    clearbit_url = get_company_logo_url(domain)
    
    # Verify Clearbit has the logo (they return 404 image if not found)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(clearbit_url, timeout=3.0)
            if response.status_code == 200:
                return clearbit_url
    except Exception:
        pass
    
    # Fallback to scraping the actual website
    if try_scraping:
        scraped_logo = await scrape_logo_from_website(domain)
        if scraped_logo:
            return scraped_logo
    
    # Last resort: return Clearbit URL anyway (they have a generic placeholder)
    return clearbit_url


async def enrich_companies_from_people(people_list: list) -> Dict[str, Dict]:
    """
    Extract and enrich all companies from a list of people with email addresses.
    
    Args:
        people_list: List of people dicts with 'email' field
    
    Returns:
        Dict mapping domain to company info
        {
            'stripe.com': {
                'domain': 'stripe.com',
                'name': 'Stripe',
                'logo_url': 'https://logo.clearbit.com/stripe.com',
                'employee_count': 3,
                'employees': ['john@stripe.com', 'jane@stripe.com', ...]
            }
        }
    """
    companies = {}
    
    for person in people_list:
        email = person.get('email', '')
        if not email:
            continue
        
        domain = extract_domain_from_email(email)
        if not domain:
            continue
        
        # Initialize company if first time seeing this domain
        if domain not in companies:
            company_info = await enrich_company_from_email(email)
            if company_info:
                companies[domain] = {
                    **company_info,
                    'employee_count': 0,
                    'employees': []
                }
        
        # Add employee to company
        if domain in companies:
            companies[domain]['employee_count'] += 1
            companies[domain]['employees'].append({
                'name': person.get('name'),
                'email': email,
                'linkedin_url': person.get('linkedin_url')
            })
    
    return companies


