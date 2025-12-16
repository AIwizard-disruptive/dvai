#!/usr/bin/env python3
"""
Generate ALL 116 DV Documentation Documents in Google Drive
============================================================

Creates complete documentation library for Disruptive Ventures:
- People (HR & Culture) - 20 documents
- Dealflow (Analysis & Contracts) - 22 documents  
- Portfolio (Building Companies) - 21 documents
- Admin (Dashboard & Management) - 23 documents
- Templates (Tools & Frameworks) - 17 documents
- Compliance (GDPR & Legal) - 13 documents

Uses OpenAI GPT-4 to generate high-quality Swedish content following
the RETT/SAFE cultural playbook methodology.

All documents include:
- Data classification metadata
- GDPR compliance markers
- Access control specifications
- Retention policies
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError
import openai
from app.integrations.google_client import get_google_client
from supabase import create_client
from app.config import settings
import json

# Initialize OpenAI
openai.api_key = settings.openai_api_key

# Document Registry with all 116 documents
DOCUMENT_REGISTRY = {
    "1_People": {
        "Kultur_Program": [
            {
                "id": 1,
                "name": "DV_Kulturplaybook_Komplett",
                "title": "Disruptive Ventures - Komplett Kulturplaybook",
                "description": "Fullständig guide för att skapa företagskultur från grunden baserat på RETT/SAFE-modellen",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 2,
                "name": "DV_Kulturworkshop_Facilitatorguide",
                "title": "Kulturworkshop - Facilitatorguide",
                "description": "Steg-för-steg guide för facilitatorer att leda kulturworkshops",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 3,
                "name": "DV_Kulturworkshop_Deltagarhandledning",
                "title": "Kulturworkshop - Deltagarhandledning",
                "description": "Material och instruktioner för workshopdeltagare",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "2_years",
                "pii": False
            },
            {
                "id": 4,
                "name": "DV_RETT_Kulturmodell_Definitioner",
                "title": "RETT Kulturmodell - Detaljerade Definitioner",
                "description": "Fullständiga definitioner av Resultat, Engagemang, Team, Tydlighet",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 5,
                "name": "DV_Kulturimplementering_30_Dagarsplan",
                "title": "Kulturimplementering - 30-dagars Quick Start",
                "description": "Snabbstartsguide för att lansera kulturprogrammet på 30 dagar",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 6,
                "name": "DV_Kulturmätning_Framework",
                "title": "Kulturmätning - Framework och KPIer",
                "description": "Ramverk för att mäta och följa upp kulturutveckling",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            }
        ],
        "Onboarding_Utveckling": [
            {
                "id": 7,
                "name": "DV_Onboarding_Dag1_Kulturintroduktion",
                "title": "Onboarding Dag 1 - Kulturintroduktion",
                "description": "Första dagens program med fokus på RETT-kulturen",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 8,
                "name": "DV_Onboarding_Första_Veckan_Checklista",
                "title": "Onboarding - Första Veckans Checklista",
                "description": "Strukturerad checklista för nya medarbetares första vecka",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 9,
                "name": "DV_Onboarding_30_Dagars_Uppföljning",
                "title": "Onboarding - 30-dagars Uppföljning",
                "description": "Uppföljningsprocess efter en månad för nya medarbetare",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 10,
                "name": "DV_Medarbetarsamtal_Mall_RETT",
                "title": "Medarbetarsamtal - Mall kopplad till RETT",
                "description": "Performance review-mall strukturerad kring RETT-värdena",
                "classification": "Konfidentiellt",
                "access": "Leadership_HR",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 11,
                "name": "DV_360_Feedback_Ledning_Mall",
                "title": "360-graders Feedback - Ledning",
                "description": "Mall för 360-feedback av ledningsgruppen",
                "classification": "Strikt_Konfidentiellt",
                "access": "HR_Only",
                "retention": "7_years",
                "pii": True
            }
        ],
        "Policydokument": [
            {
                "id": 12,
                "name": "DV_GDPR_Policy",
                "title": "GDPR-policy för Disruptive Ventures",
                "description": "Komplett GDPR-efterlevnad och dataskyddspolicy",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 13,
                "name": "DV_Rekryteringspolicy_Kulturfit",
                "title": "Rekryteringspolicy med Kulturfokus",
                "description": "Policy för rekrytering med fokus på kulturell passform",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 14,
                "name": "DV_Remote_Hybrid_Policy",
                "title": "Remote och Hybrid Work Policy",
                "description": "Policy och riktlinjer för distans- och hybridarbete",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 15,
                "name": "DV_Medarbetarhandbok",
                "title": "Disruptive Ventures - Medarbetarhandbok",
                "description": "Komplett handbok för alla medarbetare",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 16,
                "name": "DV_Etisk_Kod",
                "title": "Etisk Kod och Beteenderegler",
                "description": "Etiska riktlinjer och förväntade beteenden",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            }
        ],
        "Erkännande_Program": [
            {
                "id": 17,
                "name": "DV_Hero_of_the_Month_Program",
                "title": "Hero of the Month - Erkännandeprogram",
                "description": "Månadsvis program för att erkänna RETT-beteenden",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 18,
                "name": "DV_RETT_Awards_Kvartalsvisa",
                "title": "RETT Awards - Kvartalsvisa",
                "description": "Kvartalsvis awards-ceremoni kopplad till RETT-värdena",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 19,
                "name": "DV_Karriärutveckling_Framework",
                "title": "Karriärutveckling - Framework",
                "description": "Ramverk för karriärvägar och utveckling inom DV",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 20,
                "name": "DV_Mentorprogram_Guide",
                "title": "Mentorprogram - Implementation Guide",
                "description": "Guide för mentor- och buddy-program",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            }
        ]
    },
    "2_Dealflow": {
        "Analyser_Due_Diligence": [
            {
                "id": 21,
                "name": "DV_Investment_Memo_Mall",
                "title": "Investment Memo - Standardmall",
                "description": "Standardiserad mall för investeringsmemon",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 22,
                "name": "DV_Due_Diligence_Checklista_Komplett",
                "title": "Due Diligence - Komplett Checklista",
                "description": "Omfattande DD-checklista för alla investeringar",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 23,
                "name": "DV_Due_Diligence_Kultur_Assessment",
                "title": "Due Diligence - Kulturanalys av Targets",
                "description": "Ramverk för att utvärdera målföretags kultur",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 24,
                "name": "DV_Marknadsanalys_Mall",
                "title": "Marknadsanalys - Template",
                "description": "Mall för djupgående marknadsanalys",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 25,
                "name": "DV_Konkurrensanalys_Framework",
                "title": "Konkurrentanalys - Framework",
                "description": "Ramverk för konkurrentkartläggning",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 26,
                "name": "DV_Finansiell_Analys_Mall",
                "title": "Finansiell Analys - Due Diligence Mall",
                "description": "Mall för finansiell due diligence",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 27,
                "name": "DV_Tech_Due_Diligence_Checklista",
                "title": "Teknisk Due Diligence - Checklista",
                "description": "Checklista för teknisk due diligence",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 28,
                "name": "DV_Legal_Due_Diligence_Checklista",
                "title": "Juridisk Due Diligence - Checklista",
                "description": "Checklista för juridisk due diligence",
                "classification": "Konfidentiellt",
                "access": "Investment_Team_Legal",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 29,
                "name": "DV_Team_Assessment_Mall",
                "title": "Team Assessment - Utvärderingsmall",
                "description": "Mall för att utvärdera målföretags team",
                "classification": "Strikt_Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": True
            },
            {
                "id": 30,
                "name": "DV_Produktanalys_Framework",
                "title": "Produktanalys - Framework",
                "description": "Ramverk för produkt/tjänsteanalys",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            }
        ],
        "Kontrakt_Juridik": [
            {
                "id": 31,
                "name": "DV_Term_Sheet_Mall",
                "title": "Term Sheet - Standardmall",
                "description": "Standardiserad term sheet för investeringar",
                "classification": "Strikt_Konfidentiellt",
                "access": "Legal_Investment_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 32,
                "name": "DV_Aktieägaravtal_Mall",
                "title": "Aktieägaravtal - Mall (SHA)",
                "description": "Shareholders Agreement standardmall",
                "classification": "Strikt_Konfidentiellt",
                "access": "Legal_Investment_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 33,
                "name": "DV_Investeringsavtal_Mall",
                "title": "Investeringsavtal - Mall",
                "description": "Investment Agreement standardmall",
                "classification": "Strikt_Konfidentiellt",
                "access": "Legal_Investment_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 34,
                "name": "DV_Styrelserepresentation_Avtal",
                "title": "Styrelserepresentation - Avtal",
                "description": "Avtal för styrelserepresentation",
                "classification": "Konfidentiellt",
                "access": "Legal_Investment_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 35,
                "name": "DV_NDA_Mall_Standard",
                "title": "NDA - Standard (Ensidig)",
                "description": "Standard Non-Disclosure Agreement (ensidig)",
                "classification": "Internt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 36,
                "name": "DV_NDA_Mall_Mutual",
                "title": "NDA - Mutual (Ömsesidig)",
                "description": "Mutual Non-Disclosure Agreement",
                "classification": "Internt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 37,
                "name": "DV_Rådgivningsavtal_Mall",
                "title": "Rådgivningsavtal - Mall",
                "description": "Advisory Agreement standardmall",
                "classification": "Konfidentiellt",
                "access": "Legal_Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 38,
                "name": "DV_Exit_Framework_Dokument",
                "title": "Exit Framework - Strategi och Struktur",
                "description": "Ramverk för exit-strategi och genomförande",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            }
        ],
        "Pipeline_Tracking": [
            {
                "id": 39,
                "name": "DV_Deal_Scorecard_Mall",
                "title": "Deal Scorecard - Scoring Mall",
                "description": "Mall för scoring av potentiella investeringar",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 40,
                "name": "DV_Pipeline_Tracking_System",
                "title": "Pipeline Tracking - System och Process",
                "description": "System för pipeline management",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 41,
                "name": "DV_Investment_Committee_Memo",
                "title": "Investment Committee - Presentation Mall",
                "description": "Mall för IC-presentationer",
                "classification": "Strikt_Konfidentiellt",
                "access": "Investment_Committee",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 42,
                "name": "DV_Portföljkandidater_Analys",
                "title": "Portföljkandidater - Utvärdering",
                "description": "Ramverk för utvärdering av kandidater",
                "classification": "Konfidentiellt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            }
        ]
    },
    "3_Portfolio": {
        "Kultur_Implementation": [
            {
                "id": 43,
                "name": "Portföljbolag_Kulturworkshop_Playbook",
                "title": "Portföljbolag - Kulturworkshop Playbook",
                "description": "Anpassad playbook för portföljbolags kulturworkshops",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 44,
                "name": "Portföljbolag_SAFE_Exempel_Fallstudie",
                "title": "Crystal Alarm SAFE - Case Study",
                "description": "Detaljerad fallstudie av SAFE-implementering",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 45,
                "name": "Portföljbolag_Akronym_Skapande_Guide",
                "title": "Skapa Eget Kulturakronym - Guide",
                "description": "Guide för att skapa företagsspecifikt kulturakronym",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 46,
                "name": "Portföljbolag_Skalningsguide_5_15_Personer",
                "title": "Skalningsguide - Startup (5-15 personer)",
                "description": "Kulturimplementering för startup stage",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 47,
                "name": "Portföljbolag_Skalningsguide_15_50_Personer",
                "title": "Skalningsguide - Growth (15-50 personer)",
                "description": "Kulturimplementering för growth stage",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 48,
                "name": "Portföljbolag_Skalningsguide_50plus_Personer",
                "title": "Skalningsguide - Scale-up (50+ personer)",
                "description": "Kulturimplementering för scale-up stage",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            }
        ],
        "Styrning_Rapportering": [
            {
                "id": 49,
                "name": "Portföljbolag_Kvartalsrapport_Mall",
                "title": "Kvartalsrapport - QBR Mall",
                "description": "Quarterly Business Review standardmall",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Board",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 50,
                "name": "Portföljbolag_Styrelseprotokoll_Mall",
                "title": "Styrelseprotokoll - Mall",
                "description": "Board Meeting standardmall",
                "classification": "Strikt_Konfidentiellt",
                "access": "Board_Members",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 51,
                "name": "Portföljbolag_Månadsbrev_Mall",
                "title": "Månadsbrev - Update Format",
                "description": "Monthly update standardformat",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "7_years",
                "pii": False
            },
            {
                "id": 52,
                "name": "Portföljbolag_KPI_Dashboard_Struktur",
                "title": "KPI Dashboard - Struktur och Metrics",
                "description": "KPI tracking framework för portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 53,
                "name": "Portföljbolag_OKR_Framework",
                "title": "OKR Framework - Objectives & Key Results",
                "description": "OKR-ramverk för portföljbolag",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "7_years",
                "pii": False
            },
            {
                "id": 54,
                "name": "Portföljbolag_Budgetprocess_Guide",
                "title": "Budgetprocess - Planning Guide",
                "description": "Guide för budget planning",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "10_years",
                "pii": False
            }
        ],
        "Operationellt_Stöd": [
            {
                "id": 55,
                "name": "Portföljbolag_Rekrytering_Playbook",
                "title": "Rekrytering - Hiring Playbook",
                "description": "Rekryteringsstöd för portföljbolag",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 56,
                "name": "Portföljbolag_Fundraising_Guide",
                "title": "Fundraising - Nästa Runda Guide",
                "description": "Guide för nästa finansieringsrunda",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 57,
                "name": "Portföljbolag_Go_To_Market_Framework",
                "title": "Go-To-Market - Strategy Framework",
                "description": "GTM-strategiramverk",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "7_years",
                "pii": False
            },
            {
                "id": 58,
                "name": "Portföljbolag_Produktutveckling_Framework",
                "title": "Produktutveckling - Framework",
                "description": "Product development ramverk",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "7_years",
                "pii": False
            },
            {
                "id": 59,
                "name": "Portföljbolag_Sales_Playbook",
                "title": "Sales Playbook - Säljprocess och Metodiker",
                "description": "Säljprocess och best practices",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 60,
                "name": "Portföljbolag_Marketing_Framework",
                "title": "Marketing Framework - Strategi och Tactics",
                "description": "Marknadsföringsstrategi-ramverk",
                "classification": "Internt",
                "access": "Building_Team_Portfolio_Companies",
                "retention": "5_years",
                "pii": False
            }
        ],
        "Exit_Tillväxt": [
            {
                "id": 61,
                "name": "Portföljbolag_Exit_Förberedelse_Checklista",
                "title": "Exit Readiness - Förberedelsechecklista",
                "description": "Checklista för exit-förberedelser",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Building_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 62,
                "name": "Portföljbolag_M&A_Playbook",
                "title": "M&A Playbook - Acquisitions Guide",
                "description": "Guide för M&A-processer",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Building_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 63,
                "name": "Portföljbolag_Expansion_Framework",
                "title": "International Expansion - Framework",
                "description": "Ramverk för internationell expansion",
                "classification": "Konfidentiellt",
                "access": "Building_Team_Portfolio_Leadership",
                "retention": "10_years",
                "pii": False
            }
        ]
    },
    "4_Admin": {
        "Dashboard_System": [
            {
                "id": 64,
                "name": "DV_Admin_Portfolio_Dashboard_Specifikation",
                "title": "Portfolio Dashboard - System Specifikation",
                "description": "Teknisk och funktionell spec för dashboard",
                "classification": "Internt",
                "access": "Admin_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 65,
                "name": "DV_Admin_Portfolio_Overview_Rapport",
                "title": "Portfolio Overview - Aggregerad Rapport",
                "description": "Övergripande portföljrapport-mall",
                "classification": "Konfidentiellt",
                "access": "Partners_Admin",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 66,
                "name": "DV_Admin_KPI_Aggregering_System",
                "title": "KPI Aggregering - System och Metrics",
                "description": "System för att aggregera KPIer från portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 67,
                "name": "DV_Admin_Företagsprofil_Mall",
                "title": "Företagsprofil - Standardmall per Portföljbolag",
                "description": "Standardprofil för varje portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 68,
                "name": "DV_Admin_Kultur_Progress_Tracking",
                "title": "Kultur Progress - Tracking per Företag",
                "description": "Kulturutveckling tracking för portföljbolag",
                "classification": "Internt",
                "access": "Admin_Building_Team",
                "retention": "7_years",
                "pii": False
            },
            {
                "id": 69,
                "name": "DV_Admin_Finansiell_Performance_Tracking",
                "title": "Finansiell Performance - Tracking System",
                "description": "Finansiell uppföljning per portföljbolag",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Admin",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 70,
                "name": "DV_Admin_Milstolpar_Progress_Dashboard",
                "title": "Milestones Progress - Dashboard",
                "description": "Milestone tracking för alla portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 71,
                "name": "DV_Admin_Team_Growth_Tracking",
                "title": "Team Growth - Tracking och Rekrytering",
                "description": "Teamtillväxt tracking per portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Building_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 72,
                "name": "DV_Admin_Product_Development_Status",
                "title": "Product Development - Status Tracking",
                "description": "Produktutvecklingsstatus per portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Building_Team",
                "retention": "7_years",
                "pii": False
            }
        ],
        "Risk_Compliance": [
            {
                "id": 73,
                "name": "DV_Admin_Risk_Assessment_Framework",
                "title": "Risk Assessment - Framework",
                "description": "Ramverk för riskbedömning av portföljbolag",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Admin",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 74,
                "name": "DV_Admin_Compliance_Checklista",
                "title": "Compliance Checklista - GDPR, Legal, Regulatory",
                "description": "Compliance-checklista för portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Legal",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 75,
                "name": "DV_Admin_Red_Flags_Monitoring",
                "title": "Red Flags - Early Warning System",
                "description": "System för att identifiera varningssignaler",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 76,
                "name": "DV_Admin_Action_Items_Tracking",
                "title": "Action Items - Tracking från Styrelsemöten",
                "description": "Action items tracking från board meetings",
                "classification": "Konfidentiellt",
                "access": "Admin_Board_Members",
                "retention": "10_years",
                "pii": False
            }
        ],
        "Strategisk_Planering": [
            {
                "id": 77,
                "name": "DV_Admin_Årlig_Portfolio_Review",
                "title": "Årlig Portfolio Review - Genomgång",
                "description": "Årlig strategisk genomgång av portföljen",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 78,
                "name": "DV_Admin_Investeringsstrategi_Dokument",
                "title": "Investeringsstrategi - Overall Strategy",
                "description": "Övergripande investeringsstrategi",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 79,
                "name": "DV_Admin_Portfolio_Konstruktion_Analys",
                "title": "Portfolio Construction - Analys och Diversifiering",
                "description": "Portfolio composition och balans",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Admin",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 80,
                "name": "DV_Admin_Synergier_Mellan_Företag",
                "title": "Cross-Portfolio Synergies - Opportunities",
                "description": "Synergiidentifiering mellan portföljbolag",
                "classification": "Konfidentiellt",
                "access": "Admin_Building_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 81,
                "name": "DV_Admin_LP_Rapport_Kvartal",
                "title": "LP Rapport - Kvartalsrapport",
                "description": "Limited Partner quarterly reporting",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 82,
                "name": "DV_Admin_LP_Rapport_Årlig",
                "title": "LP Rapport - Årsrapport",
                "description": "Limited Partner annual reporting",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            }
        ],
        "Interna_Processer": [
            {
                "id": 83,
                "name": "DV_Admin_Investment_Committee_Process",
                "title": "Investment Committee - Process och Regler",
                "description": "IC-process och beslutsregler",
                "classification": "Konfidentiellt",
                "access": "Investment_Committee",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 84,
                "name": "DV_Admin_Deal_Flow_Process",
                "title": "Deal Flow - Management Process",
                "description": "Process för deal flow management",
                "classification": "Internt",
                "access": "Investment_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 85,
                "name": "DV_Admin_Portfolio_Support_Process",
                "title": "Portfolio Support - Process för Portföljbolag",
                "description": "Support-process för portföljbolag",
                "classification": "Internt",
                "access": "Building_Team",
                "retention": "10_years",
                "pii": False
            },
            {
                "id": 86,
                "name": "DV_Admin_Exit_Process_Guide",
                "title": "Exit Process - Hantering och Genomförande",
                "description": "Exit-hantering process guide",
                "classification": "Strikt_Konfidentiellt",
                "access": "Partners_Only",
                "retention": "Permanent",
                "pii": False
            }
        ]
    },
    "5_Templates": {
        "Workshop_Material": [
            {
                "id": 87,
                "name": "Workshop_Facilitator_Script_Svenska",
                "title": "Workshop Facilitator - Komplett Script",
                "description": "Word-for-word facilitator script på svenska",
                "classification": "Internt",
                "access": "HR_Building_Team",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 88,
                "name": "Workshop_Presentation_Mall",
                "title": "Workshop Presentation - PowerPoint Mall",
                "description": "Färdig presentation för kulturworkshop",
                "classification": "Internt",
                "access": "HR_Building_Team",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 89,
                "name": "Workshop_Post_It_Instruktioner",
                "title": "Workshop - Post-It Övning Instruktioner",
                "description": "Tryckvänliga instruktioner för post-it-övning",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 90,
                "name": "Workshop_Dokumentation_Mall",
                "title": "Workshop Dokumentation - Mall",
                "description": "Mall för att dokumentera workshop-resultat",
                "classification": "Internt",
                "access": "HR_Building_Team",
                "retention": "7_years",
                "pii": False
            }
        ],
        "Visuella_Material": [
            {
                "id": 91,
                "name": "RETT_Modell_Affisch_A3",
                "title": "RETT Modell - A3 Affisch (Tryckvänlig)",
                "description": "Tryckvänlig affisch av RETT-modellen",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 92,
                "name": "RETT_Modell_Fickkort",
                "title": "RETT Modell - Pocket Cards",
                "description": "Fickkort med RETT-definitioner",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 93,
                "name": "Kulturmodell_Presentation_Mall",
                "title": "Kulturmodell - Presentationsmall",
                "description": "Generisk presentationsmall för kulturmodeller",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 94,
                "name": "Kulturmodell_Onboarding_Slides",
                "title": "Kulturmodell - Onboarding Slides",
                "description": "Onboarding-specifik presentation",
                "classification": "Internt",
                "access": "HR_All_Employees",
                "retention": "5_years",
                "pii": False
            }
        ],
        "Mätverktyg": [
            {
                "id": 95,
                "name": "Medarbetarundersökning_Kultur_Mall",
                "title": "Medarbetarundersökning - Kultur Focus",
                "description": "Employee survey med kulturfokus",
                "classification": "Internt",
                "access": "HR_Leadership",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 96,
                "name": "Pulse_Check_Månadsvis_Mall",
                "title": "Pulse Check - Månatlig Mätning",
                "description": "Snabb månatlig pulsmätning",
                "classification": "Internt",
                "access": "HR_Leadership",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 97,
                "name": "360_Feedback_Formulär",
                "title": "360 Feedback - Formulär",
                "description": "360-graders feedback formulär",
                "classification": "Strikt_Konfidentiellt",
                "access": "HR_Only",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 98,
                "name": "Exit_Interview_Mall",
                "title": "Exit Interview - Strukturerad Mall",
                "description": "Exit-intervju struktur och frågor",
                "classification": "Strikt_Konfidentiellt",
                "access": "HR_Only",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 99,
                "name": "Kultur_Audit_Årlig_Checklista",
                "title": "Kulturaudit - Årlig Checklista",
                "description": "Årlig kulturaudit-checklista",
                "classification": "Internt",
                "access": "HR_Leadership",
                "retention": "10_years",
                "pii": False
            }
        ],
        "Kommunikation": [
            {
                "id": 100,
                "name": "Kultur_Lansering_Kommunikation_Plan",
                "title": "Kulturlansering - Kommunikationsplan",
                "description": "Kommunikationsplan för kulturlansering",
                "classification": "Internt",
                "access": "HR_Leadership",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 101,
                "name": "Kultur_Newsletter_Mall",
                "title": "Kulturnyhetsbrev - Mall",
                "description": "Intern nyhetsbrev-mall",
                "classification": "Internt",
                "access": "HR_All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 102,
                "name": "Erkännande_Kommunikation_Mallar",
                "title": "Erkännande - Kommunikationsmallar",
                "description": "Mallar för recognition communications",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 103,
                "name": "Slack_Kanal_Riktlinjer_Kultur",
                "title": "Slack Channel - Kulturriktlinjer",
                "description": "Riktlinjer för kultur-relaterade Slack-kanaler",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            }
        ]
    },
    "6_Compliance": {
        "GDPR_Legal": [
            {
                "id": 104,
                "name": "DV_Dataskyddspolicy_Komplett",
                "title": "Dataskyddspolicy - Komplett GDPR",
                "description": "Fullständig dataskyddspolicy enligt GDPR",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 105,
                "name": "DV_Data_Classification_Framework",
                "title": "Data Classification - Framework",
                "description": "Ramverk för dataklassificering",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 106,
                "name": "DV_Data_Retention_Policy",
                "title": "Data Retention - Policy",
                "description": "Policy för datalagring och radering",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 107,
                "name": "DV_Access_Control_Matrix",
                "title": "Access Control - Behörighetsmatris",
                "description": "Vem får se vilka dokument och data",
                "classification": "Konfidentiellt",
                "access": "IT_Security_Admin",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 108,
                "name": "DV_Lönepolicy",
                "title": "Lönepolicy - Kompensationsstruktur",
                "description": "Policy för löner och kompensation",
                "classification": "Strikt_Konfidentiellt",
                "access": "HR_Leadership_Only",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 109,
                "name": "DV_Förmånspolicy",
                "title": "Förmånspolicy - Benefits",
                "description": "Policy för förmåner och benefits",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 110,
                "name": "DV_Semester_Ledighet_Policy",
                "title": "Semester och Ledighet - Policy",
                "description": "Policy för semester, föräldraledighet, etc.",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 111,
                "name": "DV_Arbetsmiljöpolicy_AML",
                "title": "Arbetsmiljöpolicy - AML Compliance",
                "description": "Policy enligt Arbetsmiljölagen",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 112,
                "name": "DV_Incidenthantering_Dataintrång",
                "title": "Incidenthantering - Dataintrång och Säkerhet",
                "description": "Process för hantering av dataintrång",
                "classification": "Konfidentiellt",
                "access": "IT_Security_Leadership",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 113,
                "name": "DV_Right_to_be_Forgotten_Process",
                "title": "Right to be Forgotten - GDPR Process",
                "description": "Process för att hantera raderingsförfrågningar",
                "classification": "Internt",
                "access": "HR_IT_Leadership",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 114,
                "name": "DV_Data_Export_Portability_Process",
                "title": "Data Portability - Export Process GDPR",
                "description": "Process för dataexport enligt GDPR",
                "classification": "Internt",
                "access": "HR_IT_Leadership",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 115,
                "name": "DV_Legal_Disclaimer_Kontraktsmallar",
                "title": "Legal Disclaimer - Kontraktsmallar",
                "description": "Disclaimer för användning av kontraktsmallar",
                "classification": "Internt",
                "access": "Legal_Investment_Team",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 116,
                "name": "DV_Hantering_Personuppgifter_Guide",
                "title": "Personuppgifter - Hanteringsguide",
                "description": "Guide för korrekt hantering av personuppgifter",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            }
        ]
    }
}


class DVDocumentGenerator:
    """Generate all 116 DV documents with OpenAI GPT-4 and Google Drive API."""
    
    def __init__(self):
        """Initialize generator with Google and OpenAI clients."""
        self.supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
        self.drive_service = None
        self.docs_service = None
        self.openai_client = openai
        self.generated_count = 0
        self.failed_documents = []
        
    async def initialize_google_services(self):
        """Initialize Google Drive and Docs services."""
        print("\n🔐 Initializing Google Services...")
        
        # Get Google integration from database
        integration = self.supabase.table('user_integrations').select('*').match({
            'integration_type': 'google',
            'is_active': True
        }).limit(1).execute()
        
        # Fallback to temp file if not in database
        if not integration.data:
            try:
                with open('/tmp/google_credentials.json', 'r') as f:
                    creds_data = json.load(f)
                    print("   ✓ Using Google credentials from temp file")
                    integration_data = creds_data
            except Exception as e:
                raise Exception(f"No Google credentials found. Error: {str(e)}")
        else:
            integration_data = integration.data[0]
        
        client = get_google_client(
            access_token=integration_data['access_token'],
            refresh_token=integration_data.get('refresh_token')
        )
        
        self.drive_service = build('drive', 'v3', credentials=client.credentials)
        self.docs_service = build('docs', 'v1', credentials=client.credentials)
        
        print("   ✓ Google Drive API initialized")
        print("   ✓ Google Docs API initialized")
    
    async def create_folder_structure(self) -> Dict[str, str]:
        """Create complete folder structure in Google Drive."""
        print("\n📁 Creating folder structure...")
        
        folder_map = {}
        
        # Create root folder
        root_folder = self._get_or_create_folder("DV Dokumentation", None)
        folder_map['root'] = root_folder['id']
        print(f"   ✓ Root: DV Dokumentation")
        
        # Create main category folders
        categories = {
            "1_People": "People (HR & Kultur)",
            "2_Dealflow": "Dealflow (Analyser & Kontrakt)",
            "3_Portfolio": "Portfolio (Building Companies)",
            "4_Admin": "Admin (Dashboard & Management)",
            "5_Templates": "Templates (Verktyg & Material)",
            "6_Compliance": "Compliance (GDPR & Legal)"
        }
        
        for key, name in categories.items():
            folder = self._get_or_create_folder(name, root_folder['id'])
            folder_map[key] = folder['id']
            print(f"   ✓ {name}")
        
        # Create subcategory folders
        for category_key, category_data in DOCUMENT_REGISTRY.items():
            parent_folder_id = folder_map[category_key]
            
            for subfolder_key in category_data.keys():
                # Convert snake_case to Title Case
                subfolder_name = subfolder_key.replace('_', ' ').title()
                folder = self._get_or_create_folder(subfolder_name, parent_folder_id)
                folder_map[f"{category_key}_{subfolder_key}"] = folder['id']
                print(f"      ↳ {subfolder_name}")
        
        print(f"\n✅ Folder structure complete: {len(folder_map)} folders created")
        return folder_map
    
    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> dict:
        """Get existing folder or create new one."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.drive_service.files().list(
            q=query,
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        if results.get('files'):
            return results['files'][0]
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        return self.drive_service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
    
    async def generate_document_content(self, doc_meta: dict) -> str:
        """Generate high-quality document content using OpenAI GPT-4."""
        
        # Build comprehensive prompt based on document type
        system_prompt = """Du är en expert på att skapa professionella företagsdokument för venture capital och portföljbolag.

Du skapar KOMPLETTA, PRODUKTIONSKLARA dokument på svenska som följer:
- RETT/SAFE kulturmodellen från playboken
- GDPR och svensk lag (AML, etc.)
- Best practices inom VC och företagsledning
- Konkreta exempel istället för placeholder-text
- Tydlig struktur med rubriker och underrubriker

Varje dokument ska vara minst 2000 ord och innehålla:
1. Metadata-sektion högst upp med classification, access, retention, PII
2. Executive Summary
3. Syfte och Målgrupp
4. Detaljerat innehåll med konkreta exempel
5. Implementeringsguide eller checklista
6. Referenser och relaterade dokument
7. Versionshistorik

VIKTIGT: INGA placeholders! Alla exempel ska vara realistiska och användbara."""

        user_prompt = f"""Skapa ett KOMPLETT dokument:

Titel: {doc_meta['title']}
Beskrivning: {doc_meta['description']}

Data Classification: {doc_meta['classification']}
Access Level: {doc_meta['access']}
Retention Period: {doc_meta['retention']}
Contains PII: {'Ja' if doc_meta['pii'] else 'Nej'}

Dokumentet ska vara minst 2000 ord och följa svensk standard för professionella företagsdokument.

Om dokumentet är en policy: Inkludera lagkrav, ansvarsområden, processer, och konsekvenser vid avvikelse.
Om dokumentet är en guide/playbook: Inkludera steg-för-steg instruktioner, konkreta exempel, och visuella beskrivningar.
Om dokumentet är en mall: Skapa färdig mall med alla sektioner ifyllda med exempeltext som kan ersättas.
Om dokumentet är om kultur (RETT/SAFE): Använd den kompletta playboken som grund och inkludera konkreta beteendeexempel.

Skapa dokumentet NU - komplett och produktionsklar."""

        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Add metadata header
            metadata_header = f"""
═══════════════════════════════════════════════════════════════════
DOKUMENT METADATA
═══════════════════════════════════════════════════════════════════
Titel: {doc_meta['title']}
Dokument ID: #{doc_meta['id']:03d}
Skapad: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Classification: {doc_meta['classification']}
Access Level: {doc_meta['access']}
Retention: {doc_meta['retention']}
Contains PII: {'Ja - Skyddas enligt GDPR' if doc_meta['pii'] else 'Nej'}
═══════════════════════════════════════════════════════════════════

"""
            
            return metadata_header + content
            
        except Exception as e:
            print(f"      ✗ OpenAI error: {str(e)}")
            return self._generate_fallback_content(doc_meta)
    
    def _generate_fallback_content(self, doc_meta: dict) -> str:
        """Generate basic fallback content if OpenAI fails."""
        return f"""
═══════════════════════════════════════════════════════════════════
DOKUMENT METADATA
═══════════════════════════════════════════════════════════════════
Titel: {doc_meta['title']}
Dokument ID: #{doc_meta['id']:03d}
Skapad: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Classification: {doc_meta['classification']}
Access Level: {doc_meta['access']}
Retention: {doc_meta['retention']}
Contains PII: {'Ja - Skyddas enligt GDPR' if doc_meta['pii'] else 'Nej'}
═══════════════════════════════════════════════════════════════════

# {doc_meta['title']}

## Beskrivning
{doc_meta['description']}

## Syfte
Detta dokument är en del av Disruptive Ventures komplett documentation library.

## Innehåll
[Dokumentet genereras med OpenAI GPT-4]

## Implementering
1. Granska dokumentet
2. Anpassa till era specifika behov
3. Implementera enligt riktlinjerna

## Relaterade Dokument
Se andra dokument i samma kategori.

---
**OBS:** Detta är en fallback-mall. Kontakta DV Documentation Team för fullständigt innehåll.
"""
    
    async def create_google_doc(
        self,
        doc_meta: dict,
        folder_id: str,
        content: str
    ) -> Optional[dict]:
        """Create Google Doc with content."""
        
        try:
            # Create empty Google Doc
            file_metadata = {
                'name': doc_meta['name'],
                'parents': [folder_id],
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            doc_file = self.drive_service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            # Insert content into doc
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_file['id'],
                body={'requests': requests}
            ).execute()
            
            return {
                'id': doc_file['id'],
                'name': doc_file['name'],
                'url': doc_file.get('webViewLink')
            }
            
        except HttpError as e:
            print(f"      ✗ Google API error: {str(e)}")
            return None
    
    async def generate_all_documents(self):
        """Generate all 116 documents."""
        
        print("\n" + "=" * 80)
        print("🚀 GENERATING ALL 116 DV DOCUMENTS")
        print("=" * 80)
        
        # Initialize services
        await self.initialize_google_services()
        
        # Create folder structure
        folder_map = await self.create_folder_structure()
        
        # Generate documents
        print("\n📄 Generating documents with OpenAI GPT-4...")
        print("   (This will take approximately 30-45 minutes)")
        print("")
        
        total_docs = 116
        
        for category_key, category_data in DOCUMENT_REGISTRY.items():
            print(f"\n{'='*80}")
            print(f"📂 CATEGORY: {category_key}")
            print(f"{'='*80}")
            
            for subfolder_key, documents in category_data.items():
                folder_id = folder_map[f"{category_key}_{subfolder_key}"]
                
                print(f"\n   📁 {subfolder_key.replace('_', ' ').title()}")
                print(f"   {'-'*75}")
                
                for doc_meta in documents:
                    doc_num = doc_meta['id']
                    print(f"   [{doc_num:03d}/{total_docs}] {doc_meta['title']:<60}", end='', flush=True)
                    
                    try:
                        # Generate content with OpenAI
                        content = await self.generate_document_content(doc_meta)
                        
                        # Create Google Doc
                        result = await self.create_google_doc(doc_meta, folder_id, content)
                        
                        if result:
                            self.generated_count += 1
                            print(f" ✅")
                            
                            # Small delay to avoid API rate limits
                            await asyncio.sleep(2)
                        else:
                            self.failed_documents.append(doc_meta)
                            print(f" ❌")
                    
                    except Exception as e:
                        self.failed_documents.append(doc_meta)
                        print(f" ❌ {str(e)[:30]}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("✅ GENERATION COMPLETE")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"   ✓ Successfully generated: {self.generated_count}/{total_docs}")
        print(f"   ✗ Failed: {len(self.failed_documents)}")
        
        if self.failed_documents:
            print(f"\n   Failed documents:")
            for doc in self.failed_documents:
                print(f"      - {doc['name']}")
        
        print(f"\n🔗 View all documents:")
        print(f"   📁 Google Drive: https://drive.google.com/drive/folders/{folder_map['root']}")
        print("\n" + "=" * 80)


async def main():
    """Main entry point."""
    generator = DVDocumentGenerator()
    await generator.generate_all_documents()


if __name__ == "__main__":
    asyncio.run(main())

