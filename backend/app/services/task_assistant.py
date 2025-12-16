"""
Intelligent Task Assistant
Analyzes action items and generates optimal prompts/solutions for assignees
Sends via Email or Slack with context and AI-generated guidance
"""
from typing import Dict, Optional
from openai import AsyncOpenAI
from app.config import settings


class TaskAssistant:
    """
    Intelligent assistant that helps assignees complete their tasks.
    
    For each action item:
    1. Understands the task and context
    2. Generates the best prompt/approach to solve it
    3. Sends to assignee via email/Slack with actionable guidance
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def analyze_and_assist(
        self,
        action_item: Dict,
        meeting_context: Dict,
        assignee_info: Dict
    ) -> Dict:
        """
        Analyze action item and generate assistance for assignee.
        
        Args:
            action_item: The action item dict with title, description, etc.
            meeting_context: Context from meeting (decisions, discussions)
            assignee_info: Info about the person assigned
        
        Returns:
            Dict with:
            - analysis: Understanding of the task
            - recommended_prompt: Best AI prompt to solve it
            - suggested_approach: Step-by-step approach
            - tools_needed: Tools/resources required
            - estimated_time: Time estimate
            - ai_assistance: How AI can help
        """
        
        if not self.client:
            raise ValueError("OpenAI API required for task assistance")
        
        task_title = action_item.get('title', '')
        task_description = action_item.get('description', '')
        priority = action_item.get('priority', 'medium')
        
        # Use AI to analyze the task deeply
        analysis_prompt = f"""You are an expert business consultant analyzing a task assignment.

TASK: {task_title}

CONTEXT: {task_description}

MEETING CONTEXT: {meeting_context.get('summary', 'Team meeting discussion')}

PRIORITY: {priority}

Analyze this task and provide:

1. **UNDERSTANDING**: What is this task really about? What's the core problem?

2. **BEST PROMPT**: If the assignee were to use AI (ChatGPT/Claude), what's the PERFECT prompt they should use? Make it specific, detailed, and actionable.

3. **APPROACH**: Step-by-step approach to complete this task efficiently.

4. **TOOLS**: What tools, data, or resources are needed?

5. **TIME ESTIMATE**: Realistic time estimate (hours/days).

6. **AI ASSISTANCE**: Exactly how AI can help at each step.

7. **SUCCESS CRITERIA**: How to know when it's done right.

Format as JSON with these keys: understanding, best_prompt, approach (array), tools (array), time_estimate, ai_assistance, success_criteria
"""
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert task analyst who helps people complete complex work efficiently using AI and best practices."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.4
        )
        
        import json
        analysis = json.loads(response.choices[0].message.content)
        
        return analysis
    
    async def generate_assistance_email(
        self,
        action_item: Dict,
        analysis: Dict,
        assignee_info: Dict,
        language: str = "sv"
    ) -> Dict:
        """
        Generate helpful email for assignee with AI-generated guidance.
        
        Args:
            action_item: The action item
            analysis: The task analysis from analyze_and_assist
            assignee_info: Info about assignee
            language: Language code (sv, en)
        
        Returns:
            Dict with subject, body, prompt_card
        """
        
        assignee_name = assignee_info.get('name', action_item.get('owner_name', 'Team member'))
        
        if language == "sv":
            subject = f"🎯 Uppgift: {action_item['title']}"
            
            body = f"""Hej {assignee_name},

Du har tilldelats följande uppgift från mötet:

**UPPGIFT:** {action_item['title']}

**PRIORITET:** {action_item.get('priority', 'medium').upper()}
{f"**DEADLINE:** {action_item.get('due_date')}" if action_item.get('due_date') else ""}

---

## 🤔 VAD HANDLAR DET OM?

{analysis.get('understanding', 'Se beskrivning nedan')}

---

## 🚀 REKOMMENDERAT TILLVÄGAGÅNGSSÄTT

{chr(10).join([f"{i}. {step}" for i, step in enumerate(analysis.get('approach', []), 1)])}

---

## 🛠️ VERKTYG & RESURSER

{chr(10).join([f"- {tool}" for tool in analysis.get('tools', [])])}

---

## ⏱️ TIDSUPPSKATTNING

{analysis.get('time_estimate', 'Uppskattas efter behov')}

---

## 🤖 HUR AI KAN HJÄLPA DIG

{analysis.get('ai_assistance', 'AI kan assistera med strukturering och analys')}

---

## ✨ PERFEKT AI-PROMPT ATT ANVÄNDA

Kopiera denna prompt till ChatGPT, Claude eller annan AI för bästa resultat:

```
{analysis.get('best_prompt', 'Se uppgiftsbeskrivning')}
```

---

## ✅ KLAR NÄR

{analysis.get('success_criteria', 'Uppgiften är klar när målet är uppnått')}

---

Lycka till! Hör av dig om du behöver hjälp.

/Disruptive Ventures
https://www.disruptiveventures.se
"""
        
        else:  # English
            subject = f"🎯 Task: {action_item['title']}"
            
            body = f"""Hi {assignee_name},

You've been assigned the following task from the meeting:

**TASK:** {action_item['title']}

**PRIORITY:** {action_item.get('priority', 'medium').upper()}
{f"**DUE:** {action_item.get('due_date')}" if action_item.get('due_date') else ""}

---

## 🤔 WHAT IS THIS ABOUT?

{analysis.get('understanding', 'See description below')}

---

## 🚀 RECOMMENDED APPROACH

{chr(10).join([f"{i}. {step}" for i, step in enumerate(analysis.get('approach', []), 1)])}

---

## 🛠️ TOOLS & RESOURCES

{chr(10).join([f"- {tool}" for tool in analysis.get('tools', [])])}

---

## ⏱️ TIME ESTIMATE

{analysis.get('time_estimate', 'Estimate as needed')}

---

## 🤖 HOW AI CAN HELP YOU

{analysis.get('ai_assistance', 'AI can assist with structure and analysis')}

---

## ✨ PERFECT AI PROMPT TO USE

Copy this prompt to ChatGPT, Claude or other AI for best results:

```
{analysis.get('best_prompt', 'See task description')}
```

---

## ✅ DONE WHEN

{analysis.get('success_criteria', 'Task complete when goal achieved')}

---

Good luck! Reach out if you need help.

/Disruptive Ventures
https://www.disruptiveventures.se
"""
        
        return {
            'subject': subject,
            'body': body,
            'prompt_card': analysis.get('best_prompt', ''),
            'tools': analysis.get('tools', []),
            'time_estimate': analysis.get('time_estimate', 'Unknown')
        }
    
    async def generate_slack_message(
        self,
        action_item: Dict,
        analysis: Dict,
        assignee_info: Dict
    ) -> Dict:
        """
        Generate Slack message with task assistance.
        
        Uses Slack's Block Kit for rich formatting.
        """
        
        assignee_name = assignee_info.get('name', action_item.get('owner_name', 'Team member'))
        
        # Slack Block Kit format
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🎯 New Task: {action_item['title']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Hi {assignee_name}!* You've been assigned a task from the meeting."
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{action_item.get('priority', 'medium').upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Due:*\n{action_item.get('due_date', 'No deadline')}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🤔 What is this about?*\n{analysis.get('understanding', 'See description')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⏱️ Estimated time:* {analysis.get('time_estimate', 'TBD')}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*✨ Perfect AI Prompt to Use:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{analysis.get('best_prompt', 'See task description')}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "💡 Copy this prompt to ChatGPT/Claude for instant help!"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🚀 Recommended Approach:*\n{chr(10).join([f'{i}. {step}' for i, step in enumerate(analysis.get('approach', []), 1)])}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Mark Complete"
                        },
                        "style": "primary",
                        "action_id": "mark_complete"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📋 View Meeting"
                        },
                        "url": f"http://localhost:8000/meeting/{action_item.get('meeting_id', '')}"
                    }
                ]
            }
        ]
        
        return {
            'channel': assignee_info.get('slack_channel', '#general'),
            'blocks': blocks,
            'text': f"New task assigned: {action_item['title']}"  # Fallback text
        }


# Example usage in API
async def send_task_assistance(action_item_id: str):
    """
    Send intelligent task assistance to assignee.
    
    This is called after action item is created/assigned.
    """
    from supabase import create_client
    
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # Get action item
    action_response = supabase.table('action_items').select('*').eq('id', action_item_id).execute()
    if not action_response.data:
        return
    
    action = action_response.data[0]
    
    # Get meeting context
    meeting_response = supabase.table('meetings').select('*, meeting_metadata').eq('id', action['meeting_id']).execute()
    meeting_context = meeting_response.data[0] if meeting_response.data else {}
    
    # Get assignee info
    assignee_info = {
        'name': action.get('owner_name', 'Team member'),
        'email': action.get('owner_email'),
        # In future: Get from people table with Slack handle
    }
    
    # Generate assistance
    assistant = TaskAssistant()
    
    # 1. Analyze task
    analysis = await assistant.analyze_and_assist(action, meeting_context, assignee_info)
    
    # 2. Generate email with AI prompt
    email = await assistant.generate_assistance_email(action, analysis, assignee_info, language="sv")
    
    # 3. Generate Slack message
    slack_msg = await assistant.generate_slack_message(action, analysis, assignee_info)
    
    # 4. Send via preferred channel
    # TODO: Integrate with email/Slack APIs
    # For now, return the generated content
    
    return {
        'email': email,
        'slack': slack_msg,
        'analysis': analysis
    }



