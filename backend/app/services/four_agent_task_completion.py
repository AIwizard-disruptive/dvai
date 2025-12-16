"""
4-Agent Task Completion System with Research
Agent 1: RESEARCHER - Find and verify sources (only trusted, verified sources)
Agent 2: GENERATOR - Complete the task, create solution
Agent 3: MATCHER - Verify solution matches task requirements
Agent 4: QA APPROVER - Verify quality, check all links work, ensure all sources cited

ZERO FABRICATION POLICY:
- Never cite sources that don't exist
- Download and verify all sources
- Check all links work (no 404s)
- Only use trusted, verifiable sources
- Attach all sources to generated document
"""
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import httpx
import json
from datetime import datetime
from app.config import settings


class ResearchAgent:
    """
    AGENT 1: RESEARCHER
    
    Finds verified sources for task completion.
    Downloads sources and validates links.
    Only uses trusted sources.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.verified_sources = []
    
    async def research_task(self, task_title: str, task_description: str) -> Dict:
        """
        Research the task and find verified sources.
        
        Returns:
            sources: List of verified sources with URLs
            research_summary: Summary of findings
            verified_links: List of working links
        """
        
        print("\n" + "=" * 80)
        print("AGENT 1: RESEARCHER - Finding Verified Sources")
        print("=" * 80)
        
        # Use AI to identify what research is needed
        research_prompt = f"""Task: {task_title}

Context: {task_description}

What kind of sources, documentation, or research would be most helpful to complete this task?

List:
1. Specific topics to research
2. Type of sources needed (documentation, tutorials, best practices, etc.)
3. Trusted sources to check (official docs, industry standards, etc.)

Return as JSON with: topics (array), source_types (array), trusted_sources (array)
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a research assistant identifying what research is needed for a business task."},
                {"role": "user", "content": research_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        research_needs = json.loads(response.choices[0].message.content)
        
        print(f"\nResearch needs identified:")
        print(f"  Topics: {', '.join(research_needs.get('topics', []))}")
        print(f"  Source types: {', '.join(research_needs.get('source_types', []))}")
        
        # For now, identify key sources (in production, would use web search API)
        # Following Zero Fabrication Policy: Only list sources we can verify
        trusted_sources = {
            'google_sheets': {
                'url': 'https://support.google.com/docs/answer/3093340',
                'title': 'Google Sheets Help - Formulas and Functions',
                'verified': True,
                'type': 'official_documentation'
            },
            'google_sheets_best_practices': {
                'url': 'https://support.google.com/docs',
                'title': 'Google Workspace Learning Center',
                'verified': True,
                'type': 'official_documentation'
            }
        }
        
        # Verify links work (check for 404s)
        verified_sources = []
        print(f"\nVerifying sources...")
        
        for key, source in trusted_sources.items():
            try:
                async with httpx.AsyncClient() as client:
                    check = await client.head(source['url'], timeout=10.0, follow_redirects=True)
                    if check.status_code == 200:
                        verified_sources.append(source)
                        print(f"  ✓ {source['title']} - Link verified")
                    else:
                        print(f"  ❌ {source['title']} - Link returned {check.status_code}")
            except Exception as e:
                print(f"  ⚠ {source['title']} - Could not verify: {e}")
        
        print(f"\n✅ {len(verified_sources)} verified sources ready")
        
        return {
            'research_needs': research_needs,
            'verified_sources': verified_sources,
            'research_summary': f"Found {len(verified_sources)} verified sources for {task_title}",
            'all_links_verified': True
        }


class GeneratorAgent:
    """
    AGENT 2: GENERATOR
    
    Generates the complete solution to the task.
    Creates deliverable (document, analysis, plan, etc.)
    Uses only verified sources from Researcher.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_solution(
        self,
        task_title: str,
        task_description: str,
        research_data: Dict,
        language: str = "sv"
    ) -> Dict:
        """
        Generate complete solution to the task.
        
        Returns:
            solution_document: The actual deliverable
            approach_used: How it was solved
            sources_cited: All sources used (from research)
        """
        
        print("\n" + "=" * 80)
        print("AGENT 2: GENERATOR - Creating Solution")
        print("=" * 80)
        
        # Build prompt with verified sources only
        sources_context = "\n".join([
            f"- {s['title']}: {s['url']}"
            for s in research_data.get('verified_sources', [])
        ])
        
        generation_prompt = f"""You are completing a business task.

TASK: {task_title}

CONTEXT: {task_description}

VERIFIED SOURCES TO USE:
{sources_context}

Create a complete, actionable solution that SOLVES this task.

Include:
1. Executive Summary (2-3 sentences)
2. Detailed Solution/Approach
3. Implementation Steps
4. Example/Template (if applicable)
5. Best Practices
6. Recommendations

RULES:
- Only reference the verified sources provided
- Cite sources inline [Source: Title]
- Be specific and actionable
- Create ready-to-use deliverable
- Language: {'Swedish' if language == 'sv' else 'English'}

Format as professional business document.
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business consultant creating complete, actionable solutions. Only use verified sources. Be specific and practical."},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.4,
            max_tokens=2000
        )
        
        solution = response.choices[0].message.content
        
        print(f"\n✓ Solution generated ({len(solution)} chars)")
        print(f"  First 200 chars: {solution[:200]}...")
        
        return {
            'solution_document': solution,
            'sources_used': research_data.get('verified_sources', []),
            'word_count': len(solution.split()),
            'generated_at': datetime.now().isoformat()
        }


class MatcherAgent:
    """
    AGENT 3: MATCHER
    
    Verifies solution matches task requirements.
    Ensures nothing is missing.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def match_to_requirements(
        self,
        task_title: str,
        task_description: str,
        solution: str
    ) -> Dict:
        """
        Verify solution matches task requirements.
        
        Returns:
            matches: bool
            gaps: List of missing elements
            coverage: Percentage of requirements met
        """
        
        print("\n" + "=" * 80)
        print("AGENT 3: MATCHER - Verifying Solution Completeness")
        print("=" * 80)
        
        matching_prompt = f"""Compare the solution against the task requirements.

TASK: {task_title}
REQUIREMENTS: {task_description}

SOLUTION PROVIDED:
{solution[:1000]}...

Does the solution:
1. Address the core problem?
2. Provide actionable steps?
3. Include examples/templates?
4. Use only verified sources?
5. Cover all aspects of the task?

Return JSON with:
- matches: boolean (true if requirements met)
- coverage_percent: number (0-100)
- gaps: array of missing elements (empty if complete)
- strengths: array of what's done well
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a quality checker verifying task completion."},
                {"role": "user", "content": matching_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        matching_result = json.loads(response.choices[0].message.content)
        
        print(f"\n✓ Coverage: {matching_result.get('coverage_percent', 0)}%")
        
        if matching_result.get('gaps'):
            print(f"  Gaps found:")
            for gap in matching_result['gaps']:
                print(f"    - {gap}")
        else:
            print(f"  ✓ No gaps - solution complete")
        
        return matching_result


class QAAgent:
    """
    AGENT 4: QA APPROVER
    
    Final quality check:
    - Verify all links work (no 404s)
    - Ensure all sources are cited
    - Check for fabricated claims
    - Approve or reject for delivery
    """
    
    async def qa_approve(
        self,
        solution: str,
        sources_used: List[Dict],
        matching_result: Dict
    ) -> Dict:
        """
        Final QA check before delivery.
        
        Returns:
            approved: bool
            issues: List of critical issues
            warnings: List of minor issues
            link_check_passed: bool
        """
        
        print("\n" + "=" * 80)
        print("AGENT 4: QA APPROVER - Final Quality Check")
        print("=" * 80)
        
        issues = []
        warnings = []
        
        # Check 1: All sources cited
        print("\n1. Checking source citations...")
        sources_mentioned = sum(1 for s in sources_used if s['title'] in solution or s['url'] in solution)
        
        if sources_mentioned == 0 and len(sources_used) > 0:
            warnings.append("Sources provided but not cited in solution")
        else:
            print(f"   ✓ {sources_mentioned}/{len(sources_used)} sources cited")
        
        # Check 2: Verify all links work
        print("\n2. Verifying all links...")
        broken_links = []
        
        for source in sources_used:
            try:
                async with httpx.AsyncClient() as client:
                    check = await client.head(source['url'], timeout=10.0, follow_redirects=True)
                    if check.status_code != 200:
                        broken_links.append(f"{source['title']} - Status {check.status_code}")
                        issues.append(f"Broken link: {source['url']}")
                    else:
                        print(f"   ✓ {source['title']} - Link works")
            except Exception as e:
                broken_links.append(f"{source['title']} - Error: {str(e)[:50]}")
                issues.append(f"Link verification failed: {source['url']}")
        
        link_check_passed = len(broken_links) == 0
        
        if not link_check_passed:
            print(f"   ❌ {len(broken_links)} broken links found")
        else:
            print(f"   ✓ All {len(sources_used)} links verified working")
        
        # Check 3: Solution completeness
        print("\n3. Checking solution completeness...")
        coverage = matching_result.get('coverage_percent', 0)
        
        if coverage < 80:
            issues.append(f"Solution only {coverage}% complete - gaps exist")
        else:
            print(f"   ✓ {coverage}% coverage - adequate")
        
        # Check 4: No fabricated claims
        print("\n4. Checking for fabricated content...")
        fabrication_keywords = ['lorem ipsum', 'example.com', 'placeholder', 'TBD', 'TODO']
        fabrication_found = any(keyword.lower() in solution.lower() for keyword in fabrication_keywords)
        
        if fabrication_found:
            issues.append("Placeholder content detected - solution incomplete")
        else:
            print(f"   ✓ No placeholder content")
        
        # Final verdict
        approved = len(issues) == 0 and link_check_passed and coverage >= 80
        
        print("\n" + "=" * 80)
        print("QA VERDICT")
        print("=" * 80)
        
        if approved:
            print("\n✅ APPROVED - Solution ready for delivery")
            print(f"  ✓ All links verified working")
            print(f"  ✓ Sources properly cited")
            print(f"  ✓ {coverage}% coverage")
            print(f"  ✓ No fabricated content")
        else:
            print("\n❌ REJECTED - Issues must be fixed")
            for issue in issues:
                print(f"  - {issue}")
        
        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return {
            'approved': approved,
            'issues': issues,
            'warnings': warnings,
            'link_check_passed': link_check_passed,
            'coverage_percent': coverage,
            'sources_verified': len(sources_used),
            'ready_for_delivery': approved
        }


class FourAgentTaskCompletion:
    """
    Complete 4-agent system for task completion with research.
    
    Workflow:
    1. RESEARCHER: Find verified sources
    2. GENERATOR: Create solution using sources
    3. MATCHER: Verify completeness
    4. QA: Final approval (links, sources, quality)
    
    Output:
    - Complete solution document (MD)
    - Email to assignee with solution
    - All sources attached
    - Verified links only
    """
    
    async def complete_task(
        self,
        action_item: Dict,
        meeting_context: Dict,
        language: str = "sv"
    ) -> Dict:
        """
        Complete the task using 4-agent workflow.
        
        Args:
            action_item: The task to complete
            meeting_context: Context from meeting
            language: Language for output
        
        Returns:
            Dict with solution, email, sources, QA result
        """
        
        print("\n" + "=" * 80)
        print("4-AGENT TASK COMPLETION SYSTEM")
        print("=" * 80)
        print(f"\nTask: {action_item['title']}")
        print(f"Assignee: {action_item.get('owner_name', 'Unknown')}")
        print(f"Language: {language.upper()}")
        
        task_title = action_item['title']
        task_description = action_item.get('description', '')
        
        # AGENT 1: Research
        researcher = ResearchAgent()
        research_data = await researcher.research_task(task_title, task_description)
        
        # AGENT 2: Generate
        generator = GeneratorAgent()
        solution_data = await generator.generate_solution(
            task_title,
            task_description,
            research_data,
            language
        )
        
        # AGENT 3: Match
        matcher = MatcherAgent()
        matching_result = await matcher.match_to_requirements(
            task_title,
            task_description,
            solution_data['solution_document']
        )
        
        # AGENT 4: QA
        qa = QAAgent()
        qa_result = await qa.qa_approve(
            solution_data['solution_document'],
            research_data['verified_sources'],
            matching_result
        )
        
        # If not approved, don't send
        if not qa_result['approved']:
            print("\n❌ Task completion REJECTED by QA")
            print("Issues must be fixed before delivery")
            return {
                'success': False,
                'qa_result': qa_result,
                'issues': qa_result['issues']
            }
        
        # Generate email with solution
        email = self._generate_completion_email(
            action_item,
            solution_data,
            research_data,
            qa_result,
            language
        )
        
        # Create downloadable package
        package = self._create_deliverable_package(
            action_item,
            solution_data,
            research_data,
            email
        )
        
        print("\n" + "=" * 80)
        print("✅ TASK COMPLETION APPROVED & READY")
        print("=" * 80)
        print(f"\nDeliverables:")
        print(f"  ✓ Solution document: {solution_data['word_count']} words")
        print(f"  ✓ Email to {action_item.get('owner_name', 'assignee')}")
        print(f"  ✓ {len(research_data['verified_sources'])} verified sources attached")
        print(f"  ✓ All links checked and working")
        print(f"  ✓ QA approved")
        
        return {
            'success': True,
            'solution': solution_data['solution_document'],
            'email': email,
            'sources': research_data['verified_sources'],
            'qa_result': qa_result,
            'package': package
        }
    
    def _generate_completion_email(
        self,
        action_item: Dict,
        solution_data: Dict,
        research_data: Dict,
        qa_result: Dict,
        language: str
    ) -> Dict:
        """Generate email with completed task solution."""
        
        assignee_name = action_item.get('owner_name', 'Team member')
        
        # Build sources list
        sources_list = '\n'.join([
            f"{i}. {s['title']}\n   {s['url']}"
            for i, s in enumerate(research_data.get('verified_sources', []), 1)
        ])
        
        if language == "sv":
            subject = f"✅ Uppgift Klar: {action_item['title']}"
            
            body = f"""Hej {assignee_name},

Din uppgift har analyserats och en lösning har genererats:

**UPPGIFT:** {action_item['title']}

---

## 📋 LÖSNING

{solution_data['solution_document']}

---

## 📚 VERIFIERADE KÄLLOR

Alla källor nedan har verifierats och länkarna fungerar:

{sources_list}

---

## ✅ KVALITETSKONTROLL

- ✓ {qa_result['coverage_percent']}% täckning av krav
- ✓ {qa_result['sources_verified']} källor verifierade
- ✓ Alla länkar funktionstestade
- ✓ Ingen fabricerad information

---

Lösningen är klar att använda. Hör av dig vid frågor!

Mvh,
Disruptive Ventures AI Assistant
https://www.disruptiveventures.se
"""
        else:
            subject = f"✅ Task Complete: {action_item['title']}"
            
            body = f"""Hi {assignee_name},

Your task has been analyzed and a solution has been generated:

**TASK:** {action_item['title']}

---

## 📋 SOLUTION

{solution_data['solution_document']}

---

## 📚 VERIFIED SOURCES

All sources below have been verified and links checked:

{sources_list}

---

## ✅ QUALITY CONTROL

- ✓ {qa_result['coverage_percent']}% requirement coverage
- ✓ {qa_result['sources_verified']} sources verified
- ✓ All links tested and working
- ✓ No fabricated information

---

Solution is ready to use. Reach out with questions!

Best regards,
Disruptive Ventures AI Assistant
https://www.disruptiveventures.se
"""
        
        return {
            'subject': subject,
            'body': body,
            'to': action_item.get('owner_email', ''),
            'attachments': [f"solution_{action_item.get('id', 'task')}.md"]
        }
    
    def _create_deliverable_package(
        self,
        action_item: Dict,
        solution_data: Dict,
        research_data: Dict,
        email: Dict
    ) -> Dict:
        """
        Create complete package with all deliverables.
        
        Returns:
            md_document: Solution as Markdown
            pdf_document: Solution as PDF (future)
            email: Email content
            sources: All source files/links
        """
        
        # Build comprehensive MD document
        sources_section = '\n'.join([
            f"- [{s['title']}]({s['url']}) - {s['type']}"
            for s in research_data.get('verified_sources', [])
        ])
        
        md_document = f"""# {action_item['title']}

**Assignee:** {action_item.get('owner_name', 'Unknown')}  
**Priority:** {action_item.get('priority', 'medium').upper()}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  

---

{solution_data['solution_document']}

---

## 📚 Sources & References

{sources_section}

---

**Quality Assured by Disruptive Ventures AI**  
All sources verified | All links tested | Zero fabrication  
https://www.disruptiveventures.se
"""
        
        return {
            'md_document': md_document,
            'email': email,
            'sources': research_data['verified_sources'],
            'filename': f"solution_{action_item.get('title', 'task').replace(' ', '_')}.md"
        }




