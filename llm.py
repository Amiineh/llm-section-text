# This file contains client that will send reqs to llm, we use Claud

import os
import anthropic
import logging
import json
logger = logging.getLogger(__name__)

class SectionerAgent:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY', None)
        if api_key is None:
            raise ValueError('ANTHROPIC_API_KEY not defined in .env')
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        self.max_token = 4000


    def _get_prompt(self, document, target_slides):
        prompt = f"""
                You are helping split a document into exactly {target_slides} sections for a presentation slide deck.
                Given an input string in markdown format and int N (number of target slides), output a json array of unique strings specifying the ending of each section. 
                Each section should represent one cohesive idea that could become a single slide.

                CRITICAL REQUIREMENTS:
                1. You must identify exactly {target_slides} split points
                2. Only split at natural semantic boundaries (between ideas, sections, or paragraphs)
                3. Splits should be at paragraph breaks (double newlines) or major section transitions
                4. DO NOT split in the middle of sentences, bullet points, or paragraphs
                5. The content must be preserved exactly - we're only deciding where to split

                Your task:
                Analyze the document and return EXACTLY {target_slides} unique text snippets that mark where each split should occur.
                Each snippet should be the LAST 40-60 characters before the split point (before the newlines that separate sections).

                Return ONLY a valid JSON array in this exact format:
                [
                  "unique text snippet ending section 1",
                  "unique text snippet ending section 2",
                  ...
                ]

                Requirements for snippets:
                - Each snippet must appear EXACTLY ONCE in the document
                - Include enough text to be unique (40-60 chars)
                - The split will occur immediately AFTER this snippet
                - Choose snippets that end naturally (end of paragraphs/sections)

                Document to split:
                {document}

                Return only the JSON array, no other text.
            """
        return prompt


    def get_llm_response(self, document, target_slides):
        if os.getenv('DEBUG'):
            return ['workflows faster than ever before.', 'economic actors in the field.\n']
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_token,  # todo: handel case where input is too long by dividing it
            messages=[{"role": "user", "content": self._get_prompt(document, target_slides)}]
        )
        response_text = message.content[0].text.strip()
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = ''.join(lines[1:-1])

        logger.info(f"llm response: {response_text}")
        endings = json.loads(response_text)
        return endings
