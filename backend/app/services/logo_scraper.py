"""
Logo Scraper Service
Automatically fetch company logos and info from websites.
Similar to HubSpot/Clearbit enrichment.
"""
import httpx
from typing import Optional, Dict
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class LogoScraper:
    """
    Scrape company logos and info from websites.
    
    Methods:
    1. Clearbit Logo API (simple, works for most domains)
    2. Website favicon
    3. Website meta tags parsing
    4. Google search fallback
    """
    
    @staticmethod
    async def get_logo_from_domain(domain: str) -> Dict:
        """
        Get logo and company info from domain.
        
        Returns:
            dict with logo_url, favicon_url, company_name, description
        """
        
        result = {
            'domain': domain,
            'logo_url': None,
            'favicon_url': None,
            'company_name': None,
            'description': None,
            'scrape_success': False
        }
        
        # Method 1: Clearbit Logo API (free, no auth needed)
        try:
            clearbit_url = f"https://logo.clearbit.com/{domain}"
            async with httpx.AsyncClient() as client:
                response = await client.get(clearbit_url, timeout=5.0)
                if response.status_code == 200:
                    result['logo_url'] = clearbit_url
                    result['scrape_success'] = True
                    result['scrape_method'] = 'clearbit'
        except:
            pass
        
        # Method 2: Favicon from website
        try:
            website_url = f"https://{domain}" if not domain.startswith('http') else domain
            async with httpx.AsyncClient() as client:
                response = await client.get(website_url, timeout=10.0, follow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Get favicon
                    favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
                    if favicon and favicon.get('href'):
                        favicon_url = favicon['href']
                        if not favicon_url.startswith('http'):
                            # Relative URL
                            base_url = f"{urlparse(website_url).scheme}://{urlparse(website_url).netloc}"
                            favicon_url = base_url + favicon_url
                        result['favicon_url'] = favicon_url
                    
                    # Get company name from title or meta
                    title = soup.find('title')
                    if title:
                        result['company_name'] = title.get_text().strip()
                    
                    # Get description from meta
                    description = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    if description and description.get('content'):
                        result['description'] = description['content'][:500]
                    
                    result['scrape_success'] = True
                    result['scrape_method'] = 'website_parser'
        except:
            pass
        
        # Fallback: Use Google's favicon service
        if not result['favicon_url']:
            result['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
        
        return result
    
    @staticmethod
    def get_initials_from_name(name: str) -> str:
        """Get initials for avatar placeholder."""
        if not name:
            return "?"
        
        parts = name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif len(parts) == 1:
            return parts[0][:2].upper()
        return "?"
    
    @staticmethod
    async def enrich_organization(domain: str) -> Dict:
        """
        Full organization enrichment from domain.
        Like Clearbit/HubSpot enrichment.
        
        Returns:
            dict with all available company info
        """
        
        logo_data = await LogoScraper.get_logo_from_domain(domain)
        
        # Additional enrichment could include:
        # - Crunchbase API (if have key)
        # - LinkedIn Company API (if have key)
        # - Custom web scraping for specific fields
        
        return logo_data


async def enrich_organization_from_email(email: str) -> Optional[Dict]:
    """Extract domain from email and enrich organization."""
    if not email or '@' not in email:
        return None
    
    domain = email.split('@')[1]
    return await LogoScraper.get_logo_from_domain(domain)

