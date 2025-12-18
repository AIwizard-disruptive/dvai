"""
Google Sheets Integration Client
=================================
Reads KPI data from Google Sheets for portfolio companies
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from typing import Dict, List, Optional


class GoogleSheetsClient:
    """Client for Google Sheets API."""
    
    def __init__(self, credentials_json: str):
        """
        Initialize Google Sheets client.
        
        Args:
            credentials_json: Service account JSON string
        """
        credentials_dict = json.loads(credentials_json)
        
        # Define scopes
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        # Create credentials
        self.credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )
        
        # Initialize client
        self.client = gspread.authorize(self.credentials)
    
    def open_spreadsheet(self, spreadsheet_url: str):
        """
        Open spreadsheet by URL.
        
        Args:
            spreadsheet_url: Full Google Sheets URL
        
        Returns:
            Spreadsheet object
        """
        return self.client.open_by_url(spreadsheet_url)
    
    def get_q3_kpi_data(self, spreadsheet_url: str) -> Dict[str, Dict]:
        """
        Read Q3 2025 KPI data from the standard format spreadsheet.
        
        Expected sheet structure:
        - Company names in column A
        - Monthly data in subsequent columns
        - Rows for: Nettoomsättning, Resultat före skatt, Anställda, etc.
        
        Args:
            spreadsheet_url: URL to Q3 KPI report
        
        Returns:
            Dict of company_name -> {q3_revenue, q3_profit, employees, cash, etc.}
        """
        try:
            spreadsheet = self.open_spreadsheet(spreadsheet_url)
            
            # Get first sheet (or specify by name)
            sheet = spreadsheet.sheet1
            
            # Get all values
            all_values = sheet.get_all_values()
            
            # Parse KPI data
            # This is a simplified parser - will need adjustment based on actual sheet structure
            companies_data = {}
            
            # TODO: Implement parsing logic based on your sheet structure
            # For now, return empty dict
            
            return companies_data
        
        except Exception as e:
            print(f"Error reading Google Sheet: {e}")
            return {}
    
    def read_range(self, spreadsheet_url: str, range_name: str) -> List[List]:
        """
        Read specific range from spreadsheet.
        
        Args:
            spreadsheet_url: Google Sheets URL
            range_name: Range in A1 notation (e.g., 'Sheet1!A1:D10')
        
        Returns:
            List of rows, each row is a list of cell values
        """
        try:
            spreadsheet = self.open_spreadsheet(spreadsheet_url)
            
            # Parse sheet name and range
            if '!' in range_name:
                sheet_name, cell_range = range_name.split('!')
                sheet = spreadsheet.worksheet(sheet_name)
            else:
                sheet = spreadsheet.sheet1
                cell_range = range_name
            
            return sheet.get(cell_range)
        
        except Exception as e:
            print(f"Error reading range {range_name}: {e}")
            return []
    
    def get_company_monthly_data(
        self, 
        spreadsheet_url: str,
        company_name: str,
        metric: str = 'Nettoomsättning'
    ) -> List[float]:
        """
        Get monthly data for a specific company and metric.
        
        Args:
            spreadsheet_url: Google Sheets URL
            company_name: Company name (e.g., 'Crystal Alarm')
            metric: Metric name (e.g., 'Nettoomsättning', 'Resultat före skatt')
        
        Returns:
            List of monthly values
        """
        try:
            spreadsheet = self.open_spreadsheet(spreadsheet_url)
            sheet = spreadsheet.sheet1
            
            # Find company section
            # Find metric row
            # Extract monthly values
            
            # TODO: Implement based on sheet structure
            return []
        
        except Exception as e:
            print(f"Error getting monthly data: {e}")
            return []


class SimpleGoogleSheetsClient:
    """Simplified client using just the spreadsheet ID and public sharing."""
    
    @staticmethod
    def parse_spreadsheet_id(url: str) -> Optional[str]:
        """Extract spreadsheet ID from URL."""
        try:
            if '/d/' in url:
                return url.split('/d/')[1].split('/')[0]
            return None
        except:
            return None
    
    @staticmethod
    async def read_public_sheet(spreadsheet_id: str, range_name: str = 'A1:Z1000'):
        """
        Read from a publicly shared Google Sheet (no auth required).
        
        Note: Sheet must be set to "Anyone with the link can view"
        
        Args:
            spreadsheet_id: The ID from the sheet URL
            range_name: Range to read in A1 notation
        
        Returns:
            Dict with values
        """
        import httpx
        
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:json&sheet=Sheet1&range={range_name}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    # Parse Google Visualization API response
                    # It's wrapped in a function call, need to extract JSON
                    text = response.text
                    
                    if text.startswith('/*'):
                        text = text.split('(', 1)[1].rsplit(')', 1)[0]
                    
                    data = json.loads(text)
                    return data
                else:
                    print(f"Error: Sheet might not be public or doesn't exist")
                    return None
        
        except Exception as e:
            print(f"Error reading public sheet: {e}")
            return None

