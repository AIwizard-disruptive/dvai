"""
Logo Scraper API
Endpoints for scraping and caching company logos
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from supabase import create_client

from app.config import settings
from app.services.company_enrichment import (
    get_best_logo_url,
    scrape_logo_from_website,
    get_company_name_from_domain
)

router = APIRouter(prefix="/api/logos", tags=["Logo Scraper"])


class LogoRequest(BaseModel):
    domain: str
    force_refresh: bool = False


class BulkLogoRequest(BaseModel):
    domains: list[str]
    force_refresh: bool = False


@router.post("/scrape")
async def scrape_company_logo(request: LogoRequest):
    """
    Scrape logo for a single company domain.
    Caches result in logo_scrape_cache table.
    
    Usage:
        POST /api/logos/scrape
        {
            "domain": "stripe.com",
            "force_refresh": false
        }
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Check cache first (unless force refresh)
        if not request.force_refresh:
            cached = supabase.table('logo_scrape_cache').select('*').eq('domain', request.domain).execute()
            if cached.data and len(cached.data) > 0:
                cache_entry = cached.data[0]
                return {
                    'domain': request.domain,
                    'logo_url': cache_entry['logo_url'],
                    'cached': True,
                    'cached_at': cache_entry['scraped_at']
                }
        
        # Scrape fresh logo
        logo_url = await get_best_logo_url(request.domain, try_scraping=True)
        company_name = get_company_name_from_domain(request.domain)
        
        if not logo_url:
            raise HTTPException(status_code=404, detail=f"Could not find logo for {request.domain}")
        
        # Cache the result
        cache_data = {
            'domain': request.domain,
            'logo_url': logo_url,
            'company_name': company_name,
            'scraped_at': datetime.utcnow().isoformat(),
            'scrape_method': 'clearbit' if 'clearbit.com' in logo_url else 'scraped'
        }
        
        # Upsert into cache
        supabase.table('logo_scrape_cache').upsert(cache_data).execute()
        
        return {
            'domain': request.domain,
            'logo_url': logo_url,
            'company_name': company_name,
            'cached': False,
            'scraped_at': cache_data['scraped_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping logo: {str(e)}")


@router.post("/bulk-scrape")
async def bulk_scrape_logos(request: BulkLogoRequest):
    """
    Scrape logos for multiple company domains in bulk.
    
    Usage:
        POST /api/logos/bulk-scrape
        {
            "domains": ["stripe.com", "shopify.com", "notion.so"],
            "force_refresh": false
        }
    """
    results = {
        'success': [],
        'failed': [],
        'cached': []
    }
    
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        for domain in request.domains:
            try:
                # Check cache first
                if not request.force_refresh:
                    cached = supabase.table('logo_scrape_cache').select('*').eq('domain', domain).execute()
                    if cached.data and len(cached.data) > 0:
                        results['cached'].append({
                            'domain': domain,
                            'logo_url': cached.data[0]['logo_url']
                        })
                        continue
                
                # Scrape logo
                logo_url = await get_best_logo_url(domain, try_scraping=True)
                
                if logo_url:
                    # Cache the result
                    cache_data = {
                        'domain': domain,
                        'logo_url': logo_url,
                        'company_name': get_company_name_from_domain(domain),
                        'scraped_at': datetime.utcnow().isoformat(),
                        'scrape_method': 'clearbit' if 'clearbit.com' in logo_url else 'scraped'
                    }
                    supabase.table('logo_scrape_cache').upsert(cache_data).execute()
                    
                    results['success'].append({
                        'domain': domain,
                        'logo_url': logo_url
                    })
                else:
                    results['failed'].append({
                        'domain': domain,
                        'error': 'Logo not found'
                    })
                    
            except Exception as e:
                results['failed'].append({
                    'domain': domain,
                    'error': str(e)
                })
        
        return {
            'total': len(request.domains),
            'success_count': len(results['success']),
            'cached_count': len(results['cached']),
            'failed_count': len(results['failed']),
            'results': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk scrape error: {str(e)}")


@router.get("/cache/{domain}")
async def get_cached_logo(domain: str):
    """
    Get cached logo for a domain.
    
    Usage:
        GET /api/logos/cache/stripe.com
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        cached = supabase.table('logo_scrape_cache').select('*').eq('domain', domain).execute()
        
        if not cached.data or len(cached.data) == 0:
            raise HTTPException(status_code=404, detail=f"No cached logo for {domain}")
        
        return cached.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cached logo: {str(e)}")


@router.post("/enrich-portfolio")
async def enrich_portfolio_companies():
    """
    Enrich all portfolio companies with logos (scrapes missing ones).
    
    Usage:
        POST /api/logos/enrich-portfolio
    """
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        
        # Get all portfolio companies without logos or with placeholder logos
        companies = supabase.table('portfolio_companies').select('*').execute()
        
        enriched_count = 0
        skipped_count = 0
        failed_count = 0
        
        for company in companies.data:
            # Skip if already has a good logo
            if company.get('logo_url') and 'clearbit.com' not in company.get('logo_url', ''):
                skipped_count += 1
                continue
            
            website = company.get('website', '')
            if not website:
                skipped_count += 1
                continue
            
            # Extract domain from website URL
            domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            try:
                # Get best logo
                logo_url = await get_best_logo_url(domain, try_scraping=True)
                
                if logo_url:
                    # Update company with logo
                    supabase.table('portfolio_companies').update({
                        'logo_url': logo_url
                    }).eq('id', company['id']).execute()
                    
                    enriched_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"Error enriching {domain}: {e}")
                failed_count += 1
        
        return {
            'total': len(companies.data),
            'enriched': enriched_count,
            'skipped': skipped_count,
            'failed': failed_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enriching portfolio: {str(e)}")

