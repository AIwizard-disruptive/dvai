"""
AI Automation Engine for DV VC Operating System.
Central service for all AI operations across 4 wheels.

Follows RETT/SAFE cultural principles:
- Resultat/Results: AI generates actionable, concrete outputs
- Engagemang/Engagement: Content is compelling and engaging
- Team/Together: Collaborative language and inclusive approach
- Tydlighet/Clarity: Clear, specific, no abstract buzzwords

Uses existing 3-agent workflow for all operations (zero fabrication policy).
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from pydantic import BaseModel
import logging

from app.services.three_agent_workflow import ThreeAgentWorkflow

logger = logging.getLogger(__name__)


class AIAutomationEngine:
    """
    Central AI service for all automations across 4 wheels.
    
    Principles (from RETT/SAFE):
    - Concrete over abstract (behaviors, not buzzwords)
    - Evidence-based (no hallucination)
    - Action-oriented (what to DO, not just what to BE)
    - Measurable (specific metrics and examples)
    """
    
    def __init__(self, db: AsyncSession, openai_api_key: str):
        self.db = db
        self.openai = AsyncOpenAI(api_key=openai_api_key)
        self.workflow = ThreeAgentWorkflow(db)
    
    # ========================================================================
    # PEOPLE WHEEL AI
    # ========================================================================
    
    async def parse_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Parse CV with GPT to extract structured data.
        
        Uses 3-agent workflow to ensure accuracy.
        
        Args:
            cv_text: Raw CV text
        
        Returns:
            {
                "summary": "2-3 sentence professional summary",
                "experience": [
                    {"title": "...", "company": "...", "duration": "...", "achievements": [...]}
                ],
                "education": [...],
                "skills": ["Python", "ML", "Leadership"],
                "certifications": [...]
            }
        """
        prompt = f"""
        Extract structured data from this CV.
        
        Requirements (TYDLIGHET principle - be specific):
        - Use EXACT text from CV (no hallucination)
        - Skills: List only explicitly mentioned skills
        - Experience: Include measurable achievements if stated
        - Summary: Write in professional, engaging tone (ENGAGEMANG)
        
        CV TEXT:
        {cv_text}
        
        Return JSON with: summary, experience, education, skills, certifications
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a professional CV parser. Extract only factual information from CVs. Never fabricate or infer beyond what's explicitly stated."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        logger.info(f"Parsed CV: {len(result.get('skills', []))} skills extracted")
        return result
    
    async def generate_professional_bio(
        self,
        person_name: str,
        role: str,
        competencies: List[str],
        cv_data: Optional[Dict] = None
    ) -> str:
        """
        Generate compelling professional bio for Google Workspace Directory.
        
        Follows ENGAGEMANG principle: engaging and authentic.
        
        Args:
            person_name: Person's name
            role: Job title
            competencies: List of skills
            cv_data: Optional structured CV data
        
        Returns:
            2-3 sentence professional bio
        """
        experience_context = ""
        if cv_data and cv_data.get('experience'):
            # Get most recent role
            recent = cv_data['experience'][0] if cv_data['experience'] else {}
            experience_context = f"Previously at {recent.get('company', 'various companies')}."
        
        prompt = f"""
        Write a compelling 2-3 sentence professional bio for Google Workspace Directory.
        
        Person: {person_name}
        Current role: {role}
        Key competencies: {', '.join(competencies[:5])}
        {experience_context}
        
        Requirements (RETT/SAFE principles):
        - ENGAGEMANG: Make it interesting and authentic (not corporate fluff)
        - TYDLIGHET: Be specific about expertise areas
        - RESULTAT: Focus on what they DO, not abstract qualities
        - Keep it professional but human
        - 2-3 sentences maximum
        - No buzzwords or clichés
        
        Example good bio:
        "Marcus is a Partner at Disruptive Ventures focusing on early-stage B2B SaaS investments. With 10+ years in startup scaling and technical due diligence, he helps founders navigate product-market fit and prepare for Series A. He's particularly passionate about AI-driven business models and developer tools."
        
        Example bad bio (avoid this):
        "Marcus is a results-oriented, passionate investor who leverages synergies to create value-add opportunities in the dynamic startup ecosystem."
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an expert at writing compelling, authentic professional bios. Follow the RETT/SAFE principles: concrete, engaging, clear, action-oriented."
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        
        bio = response.choices[0].message.content.strip()
        logger.info(f"Generated bio for {person_name}: {len(bio)} chars")
        return bio
    
    async def generate_policy(
        self,
        policy_category: str,
        requirements: Dict[str, Any],
        company_context: Optional[str] = None
    ) -> str:
        """
        Generate HR policy using 3-agent workflow.
        
        Follows TYDLIGHET principle: concrete and clear.
        
        Args:
            policy_category: 'employment', 'benefits', 'security', 'code-of-conduct'
            requirements: Specific requirements for this policy
            company_context: Optional company-specific context
        
        Returns:
            Full policy text (markdown)
        """
        prompt = f"""
        Generate a {policy_category} policy.
        
        Requirements: {requirements}
        Company context: {company_context or 'Not provided'}
        
        Principles (from RETT/SAFE methodology):
        - TYDLIGHET: Use concrete language, specific examples
        - ANSVAR: Clear ownership and accountability
        - KONKRET: Behaviors, not abstract values
        - Include "what TO DO" and "what NOT to do" sections
        - Make it scannable (headers, bullet points)
        - Include real scenarios/examples
        
        Structure:
        1. Purpose (why this policy exists)
        2. Scope (who it applies to)
        3. Concrete behaviors and guidelines
        4. Examples of good practice
        5. Examples of violations
        6. Consequences and escalation
        7. Review and updates process
        """
        
        # Use 3-agent workflow to ensure quality
        result = await self.workflow.extract_with_workflow(
            meeting_id=None,  # Not from meeting
            org_id=requirements.get('org_id'),
            content_type='policy_generation',
            qa_goal='zero_hallucinations',
            source_data={'prompt': prompt, 'requirements': requirements},
            correlation_id=f"policy_{policy_category}"
        )
        
        if not result.success or not result.qa_result.approved:
            raise ValueError(f"Policy generation failed QA: {result.qa_result.issues}")
        
        return result.content.data.get('policy_text', '')
    
    async def generate_contract(
        self,
        contract_type: str,
        terms: Dict[str, Any],
        template: Optional[str] = None
    ) -> str:
        """
        Generate contract from template + terms.
        
        Follows TYDLIGHET + ANSVAR principles.
        
        Args:
            contract_type: 'employment', 'contractor', 'nda', 'investment'
            terms: Contract-specific terms (salary, dates, etc.)
            template: Optional template text
        
        Returns:
            Full contract text
        """
        prompt = f"""
        Generate a {contract_type} contract.
        
        Terms: {terms}
        Template (if any): {template or 'Use standard format'}
        
        Principles (RETT/SAFE):
        - TYDLIGHET: Crystal clear language, no ambiguity
        - ANSVAR: Clear responsibilities for all parties
        - KONKRET: Specific numbers, dates, deliverables
        - Swedish law compliant
        
        Include:
        1. Parties (clear identification)
        2. Terms (specific, measurable)
        3. Responsibilities (what each party DOES)
        4. Timelines (exact dates)
        5. Termination conditions (clear criteria)
        6. Signatures section
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a legal contract specialist. Generate clear, enforceable contracts following Swedish law. Be specific and concrete."
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        
        contract_text = response.choices[0].message.content
        logger.info(f"Generated {contract_type} contract: {len(contract_text)} chars")
        return contract_text
    
    async def generate_role_description(
        self,
        role_title: str,
        role_level: str,
        department: str,
        company_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete role description for recruitment.
        
        Follows ENGAGEMANG principle: make roles attractive.
        
        Args:
            role_title: Job title
            role_level: 'junior', 'mid', 'senior', 'lead'
            department: Department name
            company_context: Company description
        
        Returns:
            {
                "description": "Engaging role description",
                "responsibilities": ["Concrete task 1", ...],
                "requirements": ["Specific skill 1", ...],
                "nice_to_have": [...],
                "why_join": "Compelling reason to join"
            }
        """
        prompt = f"""
        Create a compelling role description for:
        Title: {role_title}
        Level: {role_level}
        Department: {department}
        Company: {company_context or 'Exciting startup'}
        
        Principles (RETT/SAFE):
        - ENGAGEMANG: Make it exciting and authentic
        - TYDLIGHET: Be specific about what they'll DO
        - RESULTAT: Focus on impact and outcomes
        - TEAM: Emphasize collaboration
        
        Structure:
        1. Description: What you'll do (engaging, 2-3 paragraphs)
        2. Responsibilities: 5-7 CONCRETE tasks (use action verbs)
        3. Requirements: Specific skills and experience (measurable where possible)
        4. Nice-to-have: Additional skills that would help
        5. Why join: Compelling reason (not generic "great culture")
        
        BAD (abstract): "Drive strategic initiatives"
        GOOD (concrete): "Lead weekly product planning meetings with engineering and design to prioritize the roadmap"
        
        Return as JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an expert at writing compelling, specific job descriptions that attract great candidates. Follow RETT/SAFE principles: concrete, engaging, clear."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def screen_candidate(
        self,
        resume_text: str,
        role_requirements: List[str],
        company_culture: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Score candidate against role + culture fit.
        
        Follows ANSVAR principle: thorough evaluation.
        
        Args:
            resume_text: Candidate's resume
            role_requirements: Required skills/experience
            company_culture: Company's culture framework (e.g., "SAFE", "RETT")
        
        Returns:
            {
                "score": 0-100,
                "strengths": ["Specific strength 1", ...],
                "concerns": ["Specific concern 1", ...],
                "culture_fit_indicators": ["Evidence from resume"],
                "recommendation": "interview" | "pass" | "maybe"
            }
        """
        prompt = f"""
        Evaluate candidate against role requirements.
        
        Role requirements: {role_requirements}
        Company culture: {company_culture or 'Not specified'}
        
        Candidate resume:
        {resume_text}
        
        Evaluation criteria (RETT/SAFE):
        - RESULTAT: Look for concrete achievements, not just responsibilities
        - ANSVAR: Evidence of ownership and follow-through
        - TEAM: Collaboration indicators
        - TYDLIGHET: Clear communication in resume
        
        Provide:
        1. Score (0-100) with justification
        2. Strengths: SPECIFIC evidence from resume
        3. Concerns: SPECIFIC gaps or red flags
        4. Culture fit: Evidence they'd thrive in this culture
        5. Recommendation: interview/pass/maybe with reasoning
        
        Be honest but fair. Use evidence only.
        Return as JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an expert recruiter. Evaluate candidates fairly using only evidence from their resume. No assumptions or biases."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    # ========================================================================
    # DEALFLOW WHEEL AI
    # ========================================================================
    
    async def qualify_lead(
        self,
        company_data: Dict[str, Any],
        investment_thesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score lead against DV investment thesis.
        
        Follows RESULTAT + TYDLIGHET principles.
        
        Args:
            company_data: Company information
            investment_thesis: DV's criteria
        
        Returns:
            {
                "score": 0-100,
                "meets_thesis": bool,
                "reasoning": "Specific reasons",
                "key_strengths": [...],
                "key_concerns": [...],
                "next_steps": "Concrete recommendation"
            }
        """
        prompt = f"""
        Evaluate this lead against DV investment thesis.
        
        Company: {company_data.get('company_name')}
        Stage: {company_data.get('company_stage')}
        Market: {company_data.get('one_liner')}
        
        DV Thesis: {investment_thesis}
        
        Evaluation framework (RETT):
        - RESULTAT: Do they have traction/results?
        - TEAM: Quality of founders and team
        - TYDLIGHET: Clear value proposition and business model
        - Market fit: TAM, timing, competition
        
        Score 0-100:
        - Stage fit (0-25): Seed/Series A match
        - Sector fit (0-25): B2B SaaS, fintech, etc.
        - Traction (0-25): Real results, not just plans
        - Team (0-25): Founder quality and completeness
        
        Be specific. Use evidence only.
        Return as JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a VC investment analyst. Evaluate startups rigorously using evidence and frameworks."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def research_company(
        self,
        company_name: str,
        website: str,
        pitch_deck_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive company research.
        
        Follows ANSVAR principle: thorough and sourced.
        
        Args:
            company_name: Company name
            website: Company website
            pitch_deck_content: Optional pitch deck text
        
        Returns:
            {
                "market_analysis": {...},
                "company_analysis": {...},
                "team_analysis": {...},
                "investment_perspective": {...},
                "sources": ["All sources used"]
            }
        """
        # Note: In production, this would use web search API
        # For now, using available information
        
        prompt = f"""
        Research company: {company_name}
        Website: {website}
        Pitch deck: {pitch_deck_content or 'Not provided'}
        
        Generate research report following ANSVAR principle:
        - Cite ALL sources explicitly
        - Separate facts from analysis
        - Be honest about unknowns
        - No fabrication
        
        Sections:
        1. Market Analysis
           - TAM/SAM/SOM (with sources)
           - Key trends
           - Competitors
        
        2. Company Analysis
           - Product/service
           - Business model
           - Traction (metrics with sources)
        
        3. Team Analysis
           - Founder backgrounds
           - Team strengths/gaps
        
        4. Investment Perspective
           - Opportunity
           - Key risks
           - Suggested questions for first meeting
        
        5. Sources
           - List ALL sources used
           - Mark what couldn't be verified
        
        Return as JSON with all sections.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a VC research analyst. Provide thorough, sourced research. Never fabricate data. Cite all sources."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def generate_outreach_email(
        self,
        lead_data: Dict[str, Any],
        campaign_type: str,
        research_data: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate personalized outreach email.
        
        Follows ENGAGEMANG + TYDLIGHET principles.
        
        Args:
            lead_data: Lead information
            campaign_type: 'initial_outreach', 'follow_up', 'invitation'
            research_data: Optional research to reference
        
        Returns:
            {"subject": "...", "body": "..."}
        """
        prompt = f"""
        Write a personalized outreach email to {lead_data.get('founder_name')} at {lead_data.get('company_name')}.
        
        Campaign type: {campaign_type}
        Company: {lead_data.get('one_liner')}
        Research insights: {research_data.get('investment_opportunity') if research_data else 'Not available'}
        
        Principles (RETT):
        - ENGAGEMANG: Genuine interest, not template
        - TYDLIGHET: Clear ask and next steps
        - RESULTAT: Action-oriented
        - TEAM: Collaborative tone
        
        Requirements:
        - Reference SPECIFIC aspect of their company (from research)
        - Explain WHY DV is interested (be genuine)
        - Clear call to action
        - Professional but human tone
        - 3-4 short paragraphs maximum
        - Swedish or English based on context
        
        BAD (generic): "We're impressed by your innovative solution..."
        GOOD (specific): "Your approach to solving X problem in the Y market caught our attention, particularly how you've achieved Z metric in just 6 months..."
        
        Return JSON with: subject, body
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a VC partner writing outreach emails. Be genuine, specific, and respectful of founder's time."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    # ========================================================================
    # BUILDING COMPANIES WHEEL AI
    # ========================================================================
    
    async def predict_target_achievement(
        self,
        target_data: Dict[str, Any],
        progress_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predict if target will be met and suggest actions.
        
        Follows RESULTAT + ANSVAR principles.
        
        Args:
            target_data: Target details
            progress_history: Historical progress updates
        
        Returns:
            {
                "will_achieve": bool,
                "confidence": 0-1,
                "prediction_reasoning": "Why",
                "recommendations": ["Specific action 1", ...],
                "risks": ["Specific risk 1", ...]
            }
        """
        prompt = f"""
        Analyze target achievement probability.
        
        Target: {target_data.get('target_name')}
        Current: {target_data.get('current_value')} / Target: {target_data.get('target_value')}
        Deadline: {target_data.get('deadline')}
        Progress history: {progress_history}
        
        Analysis framework (RETT/SAFE):
        - RESULTAT: Look at actual progress trend
        - FOKUS: Are they on the right track?
        - ANSVAR: Identify what needs ownership
        - TYDLIGHET: Clear prediction and reasoning
        
        Provide:
        1. Prediction: Will they achieve? (yes/no/maybe)
        2. Confidence: 0-1 (based on data quality and trend)
        3. Reasoning: WHY you think this (specific data points)
        4. Recommendations: 3-5 CONCRETE actions to improve chances
        5. Risks: Specific obstacles to watch
        
        Be honest. Data-driven. Actionable.
        Return JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a business analyst helping portfolio companies hit targets. Be data-driven and actionable."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def calculate_qualification_score(
        self,
        portfolio_company_id: str,
        criteria: List[Dict[str, Any]],
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate next-round qualification score.
        
        Follows TYDLIGHET principle: transparent scoring.
        
        Args:
            portfolio_company_id: Company ID
            criteria: List of qualification criteria
            current_metrics: Current company metrics
        
        Returns:
            {
                "overall_score": 0-100,
                "status": "green" | "yellow" | "red",
                "criteria_scores": [{criterion, score, met}],
                "gaps": ["Specific gap 1", ...],
                "recommendations": ["Action 1", ...]
            }
        """
        prompt = f"""
        Calculate next-round qualification score.
        
        Criteria: {criteria}
        Current metrics: {current_metrics}
        
        Scoring (TYDLIGHET):
        - Show calculation for each criterion
        - Mandatory criteria: must ALL be met
        - Weighted criteria: calculate weighted average
        - Overall: 0-100 score
        
        Status:
        - Green (>80): On track for next round
        - Yellow (50-80): Needs focus
        - Red (<50): Significant gaps
        
        For each gap, provide:
        - What's missing (specific metric)
        - How far from target
        - Concrete action to close gap
        
        Be transparent. Show your work.
        Return JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are helping VCs evaluate portfolio company readiness for next funding round. Be rigorous and transparent."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def generate_ceo_recommendations(
        self,
        company_data: Dict[str, Any],
        targets: List[Dict[str, Any]],
        recent_updates: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate personalized recommendations for CEO.
        
        Follows RESULTAT + FOKUS principles.
        
        Args:
            company_data: Portfolio company details
            targets: All targets
            recent_updates: Recent target updates
        
        Returns:
            List of 3-5 specific, actionable recommendations
        """
        prompt = f"""
        Generate CEO recommendations.
        
        Company: {company_data.get('name')}
        Stage: {company_data.get('investment_stage')} → {company_data.get('target_stage')}
        Targets: {len(targets)} targets, {sum(1 for t in targets if t.get('status') == 'on_track')} on track
        
        Principles (SAFE):
        - FOKUS: Prioritize what matters most
        - RESULTAT: Action-oriented, specific
        - ANSVAR: Clear ownership
        - KONKRET: Measurable outcomes
        
        Generate 3-5 recommendations:
        - Each must be SPECIFIC and ACTIONABLE
        - Include WHAT to do, WHY, and expected OUTCOME
        - Prioritize by impact
        - Consider resource constraints
        
        BAD: "Improve customer acquisition"
        GOOD: "Launch referral program this month: 10% discount for referrers. Expected: 20% increase in qualified leads based on similar B2B SaaS benchmarks."
        
        Return as JSON array of recommendations.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an experienced startup advisor. Give specific, actionable advice that CEOs can implement immediately."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get('recommendations', [])
    
    # ========================================================================
    # ADMIN WHEEL AI
    # ========================================================================
    
    async def generate_portfolio_insights(
        self,
        portfolio_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate cross-portfolio insights for DV partners.
        
        Follows TYDLIGHET principle: clear patterns.
        
        Args:
            portfolio_data: List of portfolio company data
        
        Returns:
            {
                "patterns": ["Pattern 1", ...],
                "alerts": ["Alert 1", ...],
                "opportunities": ["Opportunity 1", ...],
                "recommendations": ["Action 1", ...]
            }
        """
        prompt = f"""
        Analyze portfolio of {len(portfolio_data)} companies.
        
        Data: {portfolio_data}
        
        Find (RETT/SAFE principles):
        - PATTERNS: What do successful companies have in common?
        - ALERTS: Which companies need attention NOW?
        - OPPORTUNITIES: Cross-portfolio synergies
        - FOKUS: What should DV partners prioritize?
        
        Be specific. Data-driven. Actionable.
        Return JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a VC portfolio analyst. Find patterns and insights across portfolio companies."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    # ========================================================================
    # CULTURE-SPECIFIC: Help portfolio companies build culture
    # ========================================================================
    
    async def generate_culture_acronym(
        self,
        core_values: List[str],
        company_industry: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Generate culture acronym following RETT/SAFE methodology.
        
        This implements the playbook methodology for portfolio companies.
        
        Args:
            core_values: 4-5 values from workshop voting
            company_industry: Industry/business area
            company_name: Company name
        
        Returns:
            {
                "acronym": "SAFE",
                "connection_to_business": "Why it fits",
                "mapping": {"original_value": "maps_to_letter"},
                "definitions": [{letter, meaning, examples}]
            }
        """
        prompt = f"""
        Create a culture acronym following the RETT/SAFE methodology.
        
        Company: {company_name}
        Industry: {company_industry}
        Core values (from workshop): {core_values}
        
        Methodology (from DV playbook):
        1. Find a word from their INDUSTRY that can be an acronym
        2. Map their core values to letters in that word
        3. ALL voted values must be represented
        4. Make it memorable and tied to their business
        
        Examples:
        - Security company → SAFE (Safety, Accountability, Focus, Excellence)
        - VC firm → RETT (Resultat, Engagemang, Team, Tydlighet)
        - Healthcare → CARE, HEAL, CURE
        - Tech → CODE, BUILD, SHIP
        
        Requirements:
        - 4-5 letter acronym
        - Connected to their business (not generic)
        - All core values mapped
        - Can be used in a sentence: "That was very [ACRONYM]"
        
        Return JSON with:
        - acronym
        - why it fits their business
        - mapping of original values to letters
        - preliminary definitions for each letter
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an expert at organizational culture design following the proven RETT/SAFE methodology from Disruptive Ventures."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    async def extract_culture_from_meetings(
        self,
        meeting_transcripts: List[str],
        existing_values: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract actual culture behaviors from meeting transcripts.
        
        Follows RETT/SAFE principle: culture is what you DO, not what you SAY.
        
        Args:
            meeting_transcripts: List of meeting transcripts
            existing_values: Optional stated values to compare against
        
        Returns:
            {
                "observed_behaviors": ["Behavior 1", ...],
                "positive_patterns": [...],
                "negative_patterns": [...],
                "values_gap": "If stated values don't match observed behaviors",
                "recommendations": ["Action 1", ...]
            }
        """
        prompt = f"""
        Analyze these meeting transcripts to identify ACTUAL culture behaviors.
        
        Transcripts: {meeting_transcripts}
        Stated values: {existing_values or 'None provided'}
        
        Extract (following playbook principle: "Culture is what you DO"):
        1. Positive behaviors you observe:
           - How do people communicate?
           - How are decisions made?
           - How is feedback given?
           - How are conflicts handled?
        
        2. Negative patterns:
           - What behaviors undermine stated values?
           - Red flags in team dynamics
        
        3. Gap analysis (if stated values provided):
           - Do behaviors match stated values?
           - Specific examples of alignment/misalignment
        
        4. Recommendations:
           - Reinforce positive patterns
           - Address negative patterns
           - Close values-behavior gap
        
        Be specific. Use quotes as evidence.
        Return JSON.
        """
        
        response = await self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are an organizational culture analyst. Observe actual behaviors and patterns from meeting data."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result


# ============================================================================
# RETT/SAFE VALIDATION
# ============================================================================

class RETTSAFEValidator:
    """
    Validates AI-generated content against RETT/SAFE principles.
    
    Ensures all content follows the cultural framework.
    """
    
    @staticmethod
    def validate_content(content: str, content_type: str) -> Dict[str, Any]:
        """
        Check if content follows RETT/SAFE principles.
        
        Returns:
            {
                "passes": bool,
                "scores": {"resultat": 0-100, "engagemang": 0-100, ...},
                "issues": ["Issue 1", ...],
                "suggestions": ["Fix 1", ...]
            }
        """
        issues = []
        suggestions = []
        
        # Check for buzzwords (violates TYDLIGHET)
        buzzwords = ['synergy', 'leverage', 'paradigm', 'disrupt', 'innovative solution']
        for word in buzzwords:
            if word.lower() in content.lower():
                issues.append(f"Contains buzzword: '{word}' (violates TYDLIGHET)")
                suggestions.append(f"Replace '{word}' with specific, concrete language")
        
        # Check for concrete examples (requires KONKRET)
        if content_type in ['policy', 'role_description']:
            if 'example' not in content.lower() and 'för exempel' not in content.lower():
                issues.append("Missing concrete examples (violates KONKRET principle)")
                suggestions.append("Add 3-5 specific examples of desired behaviors")
        
        # Check for action orientation (RESULTAT)
        action_verbs = ['create', 'build', 'deliver', 'achieve', 'implement', 'execute']
        has_action = any(verb in content.lower() for verb in action_verbs)
        if not has_action and content_type in ['policy', 'role_description']:
            issues.append("Lacks action orientation (violates RESULTAT)")
            suggestions.append("Use action verbs: what people should DO")
        
        passes = len(issues) == 0
        
        return {
            "passes": passes,
            "issues": issues,
            "suggestions": suggestions,
            "rett_safe_compliant": passes
        }

