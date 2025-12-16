"""
Translation Service - Bilingual Support (Swedish ⟷ English)
All content exists in both languages
"""
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from app.config import settings


class TranslationService:
    """Service for translating meeting content between Swedish and English."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    async def translate_meeting_data(
        self,
        meeting_data: Dict,
        source_lang: str = "sv",
        target_lang: str = "en"
    ) -> Dict:
        """
        Translate all meeting data to target language.
        
        Args:
            meeting_data: Dict with attendees, decisions, actions, meeting_info
            source_lang: Source language code (sv=Swedish, en=English)
            target_lang: Target language code
        
        Returns:
            Translated meeting data in same structure
        """
        
        if not self.client:
            raise ValueError("OpenAI API key required for translation")
        
        # Translate meeting title and metadata
        translated_meeting_info = await self._translate_meeting_info(
            meeting_data.get('meeting_info', {}),
            source_lang,
            target_lang
        )
        
        # Translate decisions
        translated_decisions = await self._translate_decisions(
            meeting_data.get('decisions', []),
            source_lang,
            target_lang
        )
        
        # Translate action items
        translated_actions = await self._translate_actions(
            meeting_data.get('action_items', []),
            source_lang,
            target_lang
        )
        
        # Attendees: Names stay same, only roles/locations translate
        translated_attendees = meeting_data.get('attendees', []).copy()
        for attendee in translated_attendees:
            if attendee.get('role'):
                attendee['role'] = await self._translate_text(
                    attendee['role'],
                    source_lang,
                    target_lang
                )
        
        return {
            'meeting_info': translated_meeting_info,
            'decisions': translated_decisions,
            'action_items': translated_actions,
            'attendees': translated_attendees,
            'source_language': source_lang,
            'target_language': target_lang
        }
    
    async def _translate_meeting_info(self, meeting_info: Dict, source_lang: str, target_lang: str) -> Dict:
        """Translate meeting metadata."""
        
        translated = meeting_info.copy()
        
        if meeting_info.get('title'):
            translated['title'] = await self._translate_text(
                meeting_info['title'],
                source_lang,
                target_lang
            )
        
        if meeting_info.get('key_points'):
            translated['key_points'] = [
                await self._translate_text(point, source_lang, target_lang)
                for point in meeting_info['key_points']
            ]
        
        if meeting_info.get('main_topics'):
            translated['main_topics'] = [
                await self._translate_text(topic, source_lang, target_lang)
                for topic in meeting_info['main_topics']
            ]
        
        return translated
    
    async def _translate_decisions(self, decisions: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """Translate decisions."""
        
        translated = []
        
        for decision in decisions:
            trans_decision = decision.copy()
            
            if decision.get('decision'):
                trans_decision['decision'] = await self._translate_text(
                    decision['decision'],
                    source_lang,
                    target_lang
                )
            
            if decision.get('rationale'):
                trans_decision['rationale'] = await self._translate_text(
                    decision['rationale'],
                    source_lang,
                    target_lang
                )
            
            translated.append(trans_decision)
        
        return translated
    
    async def _translate_actions(self, actions: List[Dict], source_lang: str, target_lang: str) -> List[Dict]:
        """Translate action items."""
        
        translated = []
        
        for action in actions:
            trans_action = action.copy()
            
            if action.get('action') or action.get('title'):
                text_to_translate = action.get('action') or action.get('title')
                trans_action['action'] = await self._translate_text(
                    text_to_translate,
                    source_lang,
                    target_lang
                )
                trans_action['title'] = trans_action['action']
            
            if action.get('description') or action.get('context'):
                desc_to_translate = action.get('description') or action.get('context')
                trans_action['description'] = await self._translate_text(
                    desc_to_translate,
                    source_lang,
                    target_lang
                )
            
            # Owner names stay same (proper nouns)
            
            translated.append(trans_action)
        
        return translated
    
    async def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate single text using OpenAI.
        
        Uses GPT-4 for high-quality translation preserving business context.
        """
        
        lang_names = {
            'sv': 'Swedish',
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish'
        }
        
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective for translation
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate from {source_name} to {target_name}. Preserve business terminology and proper nouns. Return only the translation, no explanations."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect language of text.
        
        Returns: Language code (sv, en, etc.)
        """
        
        # Simple heuristic - check for Swedish-specific characters
        swedish_chars = set('åäöÅÄÖ')
        swedish_words = {'och', 'är', 'att', 'för', 'med', 'på', 'det', 'ska', 'kan', 'har', 'som'}
        
        text_lower = text.lower()
        
        # Check for Swedish characters
        if any(char in text for char in swedish_chars):
            return 'sv'
        
        # Check for Swedish words
        words = set(text_lower.split())
        swedish_word_count = len(words.intersection(swedish_words))
        
        if swedish_word_count >= 3:
            return 'sv'
        
        return 'en'  # Default to English




