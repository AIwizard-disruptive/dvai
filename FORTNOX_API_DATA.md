# Fortnox API - Available Data 💰

**Official Documentation:** https://api.fortnox.se/apidocs

---

## Overview

Fortnox provides a comprehensive REST API for accessing financial data from your accounting system. Perfect for portfolio company financial tracking and KPIs.

---

## 1. Invoices 🧾

### Endpoints:
- `GET /invoices` - List all invoices
- `GET /invoices/{id}` - Get specific invoice
- `POST /invoices` - Create new invoice
- `PUT /invoices/{id}` - Update invoice

### Available Data:
```json
{
  "DocumentNumber": "123",
  "CustomerNumber": "1",
  "CustomerName": "Volvo Group",
  "InvoiceDate": "2025-01-01",
  "DueDate": "2025-01-31",
  "Total": 125000,
  "TotalVAT": 31250,
  "Currency": "SEK",
  "Status": "sent",
  "Booked": false,
  "Cancelled": false,
  "OCR": "1230000000",
  "InvoiceRows": [
    {
      "ArticleNumber": "SVC001",
      "Description": "Consulting Services",
      "Quantity": 40,
      "Price": 2500,
      "Total": 100000
    }
  ]
}
```

### Filters Available:
- `status` - cancelled, fully_paid, unpaid, etc.
- `customernumber` - Filter by customer
- `fromdate` / `todate` - Date range
- `invoicetype` - cash, invoice, etc.
- `lastmodified` - Get recent changes

### Use Cases for Portfolio Dashboard:
- **Revenue Tracking**: MRR, ARR calculations
- **Payment Status**: Overdue invoices, collection metrics
- **Customer Analysis**: Top customers by revenue
- **Cash Flow**: Projected vs actual income
- **Aging Reports**: Invoice aging by company

---

## 2. Customers 👥

### Endpoints:
- `GET /customers` - List all customers
- `GET /customers/{id}` - Get specific customer
- `POST /customers` - Create new customer
- `PUT /customers/{id}` - Update customer

### Available Data:
```json
{
  "CustomerNumber": "1",
  "Name": "Volvo Group",
  "OrganisationNumber": "556012-5790",
  "Email": "accounting@volvo.com",
  "Phone": "+46 31 66 00 00",
  "Address1": "Gropegårdsgatan",
  "City": "Göteborg",
  "Country": "Sverige",
  "VATNumber": "SE556012579001",
  "YourReference": "John Doe",
  "OurReference": "Jane Smith",
  "Currency": "SEK",
  "PaymentTerms": "30",
  "Type": "COMPANY"
}
```

### Use Cases:
- **Client Database**: Sync customers across portfolio companies
- **Payment Terms**: Track average payment cycles
- **Geographic Analysis**: Revenue by region
- **Customer Types**: B2B vs B2C breakdown

---

## 3. Financial Accounts (Chart of Accounts) 📊

### Endpoints:
- `GET /accounts` - List all accounts
- `GET /accounts/{id}` - Get specific account

### Available Data:
```json
{
  "Number": "3000",
  "Description": "Sales Revenue",
  "Active": true,
  "BalanceBroughtForward": 0,
  "BalanceCarriedForward": 2450000,
  "CostCenter": "CC1",
  "Year": 2025
}
```

### Key Accounts to Track:
- **Revenue Accounts** (3000-3999)
- **Cost of Goods Sold** (4000-5999)
- **Operating Expenses** (6000-7999)
- **Assets** (1000-1999)
- **Liabilities** (2000-2999)

### Use Cases:
- **P&L Statement**: Automated profit/loss generation
- **Balance Sheet**: Real-time financial position
- **Burn Rate**: Monthly operating expenses
- **Gross Margin**: Revenue vs COGS

---

## 4. Vouchers (Journal Entries) 📝

### Endpoints:
- `GET /vouchers` - List vouchers
- `GET /vouchers/{id}` - Get specific voucher
- `POST /vouchers` - Create voucher

### Available Data:
```json
{
  "VoucherSeries": "A",
  "VoucherNumber": 1234,
  "TransactionDate": "2025-01-15",
  "Description": "Monthly Payroll",
  "Total": 350000,
  "VoucherRows": [
    {
      "Account": 7010,
      "Debit": 350000,
      "Credit": 0,
      "Description": "Salaries January"
    }
  ]
}
```

### Use Cases:
- **Transaction History**: Detailed financial audit trail
- **Expense Categorization**: Auto-categorize spending
- **Bookkeeping Automation**: Sync transactions
- **Financial Reconciliation**: Match payments

---

## 5. Articles (Products/Services) 🛍️

### Endpoints:
- `GET /articles` - List articles
- `GET /articles/{id}` - Get specific article
- `POST /articles` - Create article

### Available Data:
```json
{
  "ArticleNumber": "SVC001",
  "Description": "Consulting Services",
  "SalesPrice": 2500,
  "PurchasePrice": 0,
  "Unit": "hour",
  "VAT": 25,
  "Active": true,
  "StockBalance": null
}
```

### Use Cases:
- **Product Mix**: Revenue by product/service
- **Pricing Analysis**: Average selling price trends
- **Margin Analysis**: Profit per product

---

## 6. Suppliers 🏭

### Endpoints:
- `GET /suppliers` - List suppliers
- `GET /suppliers/{id}` - Get specific supplier

### Available Data:
```json
{
  "SupplierNumber": "100",
  "Name": "AWS EMEA SARL",
  "OrganisationNumber": "LU-123456",
  "Email": "billing@aws.com",
  "Currency": "USD",
  "OurReference": "IT Department"
}
```

### Use Cases:
- **Vendor Management**: Track key suppliers
- **Cost Analysis**: Spending by vendor
- **Payment Tracking**: Supplier payment terms

---

## 7. Supplier Invoices (Accounts Payable) 📥

### Endpoints:
- `GET /supplierinvoices` - List supplier invoices
- `GET /supplierinvoices/{id}` - Get specific invoice

### Available Data:
```json
{
  "GivenNumber": "AWS-2025-001",
  "SupplierNumber": "100",
  "SupplierName": "AWS EMEA SARL",
  "InvoiceDate": "2025-01-01",
  "DueDate": "2025-01-31",
  "Total": 45000,
  "Currency": "USD",
  "Booked": true
}
```

### Use Cases:
- **Expense Tracking**: Monthly operating costs
- **Cash Flow Planning**: Upcoming payments
- **Vendor Spending**: Cost breakdown by category

---

## 8. Cost Centers 🎯

### Endpoints:
- `GET /costcenters` - List cost centers

### Available Data:
```json
{
  "Code": "CC1",
  "Description": "Product Development",
  "Note": "All product-related costs",
  "Active": true
}
```

### Use Cases:
- **Department Tracking**: Costs by team
- **Project Accounting**: Expense allocation
- **Budget vs Actual**: Performance by center

---

## 9. Company Settings ⚙️

### Endpoints:
- `GET /settings/company` - Get company info

### Available Data:
```json
{
  "CompanyName": "Crystal Alarm AB",
  "OrganizationNumber": "556XXX-XXXX",
  "VisitAddress": "...",
  "PostalAddress": "...",
  "Email": "info@crystalalarm.se",
  "Phone": "+46...",
  "BankAccount": "...",
  "VATNumber": "SE..."
}
```

---

## 10. Financial Years 📅

### Endpoints:
- `GET /financialyears` - List financial years

### Available Data:
```json
{
  "Id": 1,
  "FromDate": "2025-01-01",
  "ToDate": "2025-12-31",
  "AccountingMethod": "ACCRUAL"
}
```

---

## Integration Workflow for Portfolio Dashboard

### 1. **Monthly Revenue Tracking**
```python
# Get invoices for current month
GET /invoices?fromdate=2025-01-01&todate=2025-01-31&status=fully_paid

# Calculate MRR
mrr = sum(invoice['Total'] for invoice in invoices) / months
```

### 2. **Cash Flow Monitoring**
```python
# Unpaid invoices (AR)
GET /invoices?status=unpaid

# Supplier invoices due (AP)
GET /supplierinvoices?status=unpaid

# Net cash flow = AR - AP
```

### 3. **Burn Rate Calculation**
```python
# Get operating expenses
GET /vouchers?accountfrom=6000&accountto=7999

# Monthly burn = Total expenses / months
```

### 4. **Customer Concentration Risk**
```python
# Get all invoices
GET /invoices?fromdate=2025-01-01

# Calculate top 5 customers
# Flag if any customer > 20% of revenue
```

---

## Required Scopes (OAuth)

When setting up Fortnox integration, request these scopes:

- `invoice` - Read/write invoices
- `customer` - Read/write customers
- `account` - Read chart of accounts
- `voucher` - Read financial transactions
- `supplier` - Read suppliers
- `supplierinvoice` - Read supplier invoices
- `article` - Read products/services
- `settings` - Read company info

---

## Authentication

### OAuth 2.0 Flow:
1. Register app at: https://developer.fortnox.se
2. Get `client_id` and `client_secret`
3. Redirect user to authorize
4. Exchange authorization code for access token
5. Use access token in API requests

### Headers Required:
```
Authorization: Bearer {access_token}
Client-Secret: {client_secret}
Content-Type: application/json
Accept: application/json
```

---

## Rate Limits

- **4 requests per second** per access token
- Implement exponential backoff for 429 errors
- Cache frequently accessed data

---

## Key Metrics We Can Calculate

### Revenue Metrics:
- **MRR** (Monthly Recurring Revenue)
- **ARR** (Annual Recurring Revenue)
- **Revenue Growth Rate** (MoM, YoY)
- **Average Deal Size**
- **Customer Lifetime Value**

### Financial Health:
- **Burn Rate** (Monthly cash consumption)
- **Runway** (Months until cash depletes)
- **Gross Margin** (Revenue - COGS) / Revenue
- **Operating Margin** (Operating Income / Revenue)
- **Cash Flow** (Inflows - Outflows)

### Operational Metrics:
- **Days Sales Outstanding** (DSO)
- **Accounts Payable Aging**
- **Expense Ratio** (OpEx / Revenue)
- **Customer Concentration** (Top 5 customers %)

---

## Implementation Priority

### Phase 1: Essential Metrics
1. ✅ Invoices - Revenue tracking
2. ✅ Customers - Client database
3. ✅ Supplier Invoices - Expense tracking

### Phase 2: Financial Analysis
4. Accounts - P&L automation
5. Vouchers - Transaction details
6. Cost Centers - Department tracking

### Phase 3: Advanced Analytics
7. Articles - Product mix analysis
8. Financial Years - Multi-year comparison
9. Suppliers - Vendor management

---

## Example API Integration Code

```python
import httpx
from datetime import datetime, timedelta

class FortnoxClient:
    def __init__(self, access_token: str, client_secret: str):
        self.base_url = "https://api.fortnox.se/3"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Client-Secret": client_secret,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get_invoices(self, from_date=None, status=None):
        """Get invoices with optional filters."""
        params = {}
        if from_date:
            params['fromdate'] = from_date.strftime('%Y-%m-%d')
        if status:
            params['status'] = status
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/invoices",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def get_monthly_revenue(self):
        """Calculate MRR from paid invoices."""
        today = datetime.now()
        first_day = today.replace(day=1)
        
        invoices = await self.get_invoices(
            from_date=first_day,
            status='fully_paid'
        )
        
        mrr = sum(inv['Total'] for inv in invoices.get('Invoices', []))
        return mrr
```

---

## Next Steps

1. **Register Fortnox Developer Account**
   - Go to: https://developer.fortnox.se
   - Create application
   - Get credentials

2. **Implement OAuth Flow**
   - Add redirect endpoint
   - Store access tokens securely
   - Handle token refresh

3. **Build Integration Module**
   - Create `fortnox_client.py`
   - Implement rate limiting
   - Add error handling

4. **Connect to Dashboard**
   - Update financial board
   - Add real-time KPIs
   - Create sync schedule

---

## Documentation

- **Official API Docs**: https://api.fortnox.se/apidocs
- **Developer Portal**: https://developer.fortnox.se
- **OAuth Guide**: https://developer.fortnox.se/general/authentication
- **Scopes Reference**: https://www.fortnox.se/en/developer/guides-and-good-to-know/scopes

---

## Summary

Fortnox provides comprehensive access to all financial data needed for portfolio company tracking:

✅ **Invoices** - Revenue and receivables  
✅ **Customers** - Client database  
✅ **Accounts** - Chart of accounts  
✅ **Vouchers** - All transactions  
✅ **Supplier Invoices** - Payables and expenses  
✅ **Articles** - Products/services  
✅ **Cost Centers** - Department tracking  
✅ **Company Info** - Business details  

This enables real-time financial KPIs for each portfolio company without manual data entry!

---

**Ready to integrate?** Let me know which metrics you want to prioritize first! 🚀

